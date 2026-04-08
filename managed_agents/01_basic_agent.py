"""
01 — Basic managed agent.

Runs a single prompt through the Agent SDK and prints the result.
The agent can read files and search the codebase; it cannot write or execute.
"""

import anyio
from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, SystemMessage

load_dotenv()


async def main() -> None:
    print("=== Basic Agent ===\n")

    async for message in query(
        prompt="List the markdown files in the current directory and summarise what each one is about.",
        options=ClaudeAgentOptions(
            cwd=".",
            allowed_tools=["Read", "Glob"],
            max_turns=10,
        ),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print(f"Session: {message.data.get('session_id')}\n")

        if isinstance(message, ResultMessage):
            print("Result:")
            print(message.result)
            print(f"\nStop reason: {message.stop_reason}")


if __name__ == "__main__":
    anyio.run(main)
