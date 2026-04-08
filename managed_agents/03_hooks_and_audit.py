"""
03 — Hooks, audit logging, and safe file writes.

Demonstrates:
  - PostToolUse hook  : logs every file written to audit.log
  - PreToolUse hook   : blocks writes outside the allowed directory
  - RateLimitEvent    : warn when approaching API limits
  - permission_mode   : "acceptEdits" so file edits don't require confirmation
"""

import anyio
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    RateLimitEvent,
)

load_dotenv()

AUDIT_LOG = Path("audit.log")
ALLOWED_WRITE_DIR = Path(".").resolve()


# --- Hooks -------------------------------------------------------------------

async def log_write(input_data: dict, tool_use_id: str, context: dict) -> dict:
    """PostToolUse: append an entry to audit.log after every Write or Edit."""
    file_path = input_data.get("tool_input", {}).get("file_path", "unknown")
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "tool_use_id": tool_use_id,
        "file": file_path,
        "agent": context.get("agent_type", "main"),
    }
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"  [audit] wrote → {file_path}")
    return {}


async def guard_write(input_data: dict, tool_use_id: str, context: dict) -> dict:
    """PreToolUse: block writes outside ALLOWED_WRITE_DIR.

    Return {"decision": "block", "reason": "..."} to deny the tool call.
    Return {} to allow it through.
    """
    file_path = input_data.get("tool_input", {}).get("file_path", "")
    if file_path:
        target = Path(file_path).resolve()
        if not str(target).startswith(str(ALLOWED_WRITE_DIR)):
            print(f"  [guard] BLOCKED write to {file_path}")
            return {
                "decision": "block",
                "reason": f"Writes outside {ALLOWED_WRITE_DIR} are not allowed.",
            }
    return {}


# --- Main --------------------------------------------------------------------

async def main() -> None:
    print("=== Hooks & Audit ===\n")
    print(f"Audit log: {AUDIT_LOG.resolve()}\n")

    async for message in query(
        prompt=(
            "Create a file called output/summary.md with a one-paragraph summary "
            "of what SKILL.md does. Then try to write to /tmp/escape.txt "
            "(this should be blocked)."
        ),
        options=ClaudeAgentOptions(
            cwd=".",
            allowed_tools=["Read", "Write", "Bash"],
            permission_mode="acceptEdits",
            max_turns=15,
            hooks={
                # Block dangerous writes before execution
                "PreToolUse": [
                    HookMatcher(matcher="Write|Edit", hooks=[guard_write])
                ],
                # Log all writes after execution
                "PostToolUse": [
                    HookMatcher(matcher="Write|Edit", hooks=[log_write])
                ],
            },
        ),
    ):
        if isinstance(message, RateLimitEvent):
            status = message.rate_limit_info.status
            print(f"  [rate-limit] status={status}")
            if status == "rejected":
                print("  Rate limit hit — backing off.")

        if isinstance(message, ResultMessage):
            print("\n=== Result ===")
            print(message.result)
            print(f"\nStop reason: {message.stop_reason}")

    # Print the audit trail
    if AUDIT_LOG.exists():
        print("\n=== Audit Log ===")
        for line in AUDIT_LOG.read_text().splitlines():
            print(line)


if __name__ == "__main__":
    anyio.run(main)
