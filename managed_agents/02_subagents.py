"""
02 — Orchestrator + subagents.

The main agent spawns two specialised subagents:
  - reader   : read-only, summarises files
  - reviewer : read-only, reviews code quality

The orchestrator decides which subagent to invoke based on the task.
"""

import anyio
from dotenv import load_dotenv
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    ResultMessage,
    SystemMessage,
    AssistantMessage,
    TextBlock,
)

load_dotenv()


async def main() -> None:
    print("=== Orchestrator + Subagents ===\n")

    async for message in query(
        prompt=(
            "First use the reader agent to summarise SKILL.md, "
            "then use the reviewer agent to assess its quality and flag any issues."
        ),
        options=ClaudeAgentOptions(
            cwd=".",
            allowed_tools=["Read", "Glob", "Agent"],
            max_turns=20,
            model="claude-opus-4-6",
            agents={
                "reader": AgentDefinition(
                    description="Reads and summarises files. Use for understanding what a file contains.",
                    prompt="You are a concise summariser. Read the requested file and return a clear summary.",
                    tools=["Read", "Glob"],
                ),
                "reviewer": AgentDefinition(
                    description="Reviews content quality, structure, and correctness. Use after the reader.",
                    prompt=(
                        "You are a critical reviewer. Assess clarity, completeness, and correctness. "
                        "Be specific about what is good and what could be improved."
                    ),
                    tools=["Read"],
                ),
            },
        ),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print(f"Session: {message.data.get('session_id')}\n")

        # Stream intermediate thinking to the console
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip():
                    print(f"[agent] {block.text[:120]}...")

        if isinstance(message, ResultMessage):
            print("\n=== Final Result ===")
            print(message.result)


if __name__ == "__main__":
    anyio.run(main)
