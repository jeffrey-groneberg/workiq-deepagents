from typing import Any

from langchain_core.tools import StructuredTool

from workiq_deepagent.config import Settings, select_workiq_tools

MODEL_TENANT_ID = "model-tenant-id"


def make_tool(name: str) -> StructuredTool:
    def run(**kwargs: Any) -> str:
        return "ok"

    return StructuredTool.from_function(
        func=run,
        name=name,
        description="Test tool",
    )


def test_workiq_connection_uses_npx() -> None:
    connection = Settings(model_tenant_id=MODEL_TENANT_ID).workiq_connection()

    assert connection == {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@microsoft/workiq", "mcp"],
    }


def test_workiq_connection_includes_tenant() -> None:
    connection = Settings(
        model_tenant_id=MODEL_TENANT_ID,
        tenant_id="tenant-id",
    ).workiq_connection()

    assert connection["args"] == [
        "-y",
        "@microsoft/workiq",
        "--tenant-id",
        "tenant-id",
        "mcp",
    ]


def test_read_only_policy_excludes_mutating_tools() -> None:
    tools = [make_tool("fetch"), make_tool("create_entity")]

    selected = select_workiq_tools(tools, allow_writes=False)

    assert [tool.name for tool in selected] == ["fetch"]


def test_write_policy_keeps_all_tools() -> None:
    tools = [make_tool("fetch"), make_tool("create_entity")]

    selected = select_workiq_tools(tools, allow_writes=True)

    assert selected == tools
