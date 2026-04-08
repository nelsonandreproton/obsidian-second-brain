"""
04 — Session resumption.

Shows how to capture a session ID from the first query and resume it
in a second query so the agent retains full context.

Useful for: multi-turn CLI tools, step-by-step workflows, human-in-the-loop.
"""

import anyio
from dotenv import load_dotenv
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
)

load_dotenv()


async def run_query(prompt: str, resume: str | None = None) -> str | None:
    """Run one query turn; returns the session_id captured from the init event."""
    session_id: str | None = None

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=".",
            allowed_tools=["Read", "Glob"],
            max_turns=10,
            **({"resume": resume} if resume else {}),
        ),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            session_id = message.data.get("session_id")

        if isinstance(message, ResultMessage):
            print(f"[turn] {message.result[:200]}\n")

    return session_id


async def main() -> None:
    print("=== Session Resumption ===\n")

    # Turn 1 — establish context
    print("Turn 1: reading SKILL.md ...")
    session_id = await run_query("Read SKILL.md and remember its structure.")

    if not session_id:
        print("No session ID captured — cannot resume.")
        return

    print(f"Session captured: {session_id}\n")

    # Turn 2 — resume with full prior context (no need to re-explain)
    print("Turn 2: asking a follow-up without re-loading the file ...")
    await run_query(
        prompt="Based on what you just read, how many commands does the skill define?",
        resume=session_id,
    )


if __name__ == "__main__":
    anyio.run(main)
