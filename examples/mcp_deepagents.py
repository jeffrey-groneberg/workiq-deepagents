"""Minimal read-only WorkIQ MCP integration with Deep Agents."""

import argparse
import asyncio
from uuid import uuid4

from deepagents import create_deep_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.checkpoint.memory import InMemorySaver

from workiq_deepagent.agent import READ_ONLY_PROMPT
from workiq_deepagent.config import Settings, select_workiq_tools
from workiq_deepagent.model import create_model
from workiq_deepagent.output import response_text


async def ask_workiq(question: str) -> str:
    settings = Settings()
    client = MultiServerMCPClient({"workiq": settings.workiq_connection()})

    async with client.session("workiq") as session:
        discovered_tools = await load_mcp_tools(session, server_name="workiq")
        tools = select_workiq_tools(discovered_tools, allow_writes=False)
        if not tools:
            raise RuntimeError("WorkIQ exposed no tools allowed by the read-only policy.")

        agent = create_deep_agent(
            model=create_model(settings),
            tools=tools,
            system_prompt=READ_ONLY_PROMPT,
            checkpointer=InMemorySaver(),
            name="workiq_example",
        )
        state = await agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            config={"configurable": {"thread_id": str(uuid4())}},
        )

    return response_text(state)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="Question to answer from Microsoft 365 context.")
    args = parser.parse_args()
    print(asyncio.run(ask_workiq(args.question)))


if __name__ == "__main__":
    main()
