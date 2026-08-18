"""Application configuration and WorkIQ tool policy."""

from collections.abc import Sequence
from decimal import Decimal

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.sessions import StdioConnection
from pydantic_settings import BaseSettings, SettingsConfigDict

READ_ONLY_TOOL_NAMES = frozenset(
    {
        "ask",
        "call_function",
        "fetch",
        "get_schema",
        "list_agents",
        "search_paths",
    }
)


class Settings(BaseSettings):
    """Configuration loaded from environment variables and CLI overrides."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="WORKIQ_AGENT_",
        extra="ignore",
    )

    model: str = "gpt-5.6-sol"
    model_base_url: str = ""
    model_token_scope: str = "https://ai.azure.com/.default"
    model_tenant_id: str = ""
    pricing_input_per_million_usd: Decimal = Decimal("5.00")
    pricing_cached_input_per_million_usd: Decimal = Decimal("0.50")
    pricing_output_per_million_usd: Decimal = Decimal("30.00")
    tenant_id: str | None = None

    def workiq_connection(self) -> StdioConnection:
        """Return the stdio connection used by langchain-mcp-adapters."""
        args = ["-y", "@microsoft/workiq"]
        if self.tenant_id:
            args.extend(["--tenant-id", self.tenant_id])
        args.append("mcp")
        return {
            "transport": "stdio",
            "command": "npx",
            "args": args,
        }


def select_workiq_tools(tools: Sequence[BaseTool], *, allow_writes: bool) -> list[BaseTool]:
    """Apply the default read-only policy to WorkIQ tools."""
    if allow_writes:
        return list(tools)
    return [tool for tool in tools if tool.name in READ_ONLY_TOOL_NAMES]
