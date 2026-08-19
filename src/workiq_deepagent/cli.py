"""Typer command-line interface for the WorkIQ Deep Agent."""

import asyncio
import shutil
import sys
from collections.abc import Coroutine
from typing import Annotated, Any, TypeVar, cast
from uuid import uuid4

import typer
from langchain_core.runnables import RunnableConfig
from rich.console import Console
from rich.table import Table

from workiq_deepagent import __version__
from workiq_deepagent.agent import open_agent
from workiq_deepagent.config import Settings
from workiq_deepagent.metrics import MetricsTracker, ModelPricing, UsageMetrics
from workiq_deepagent.output import response_text
from workiq_deepagent.streaming import stream_agent

app = typer.Typer(
    name="workiq-agent",
    help="Query Microsoft 365 context with Deep Agents and WorkIQ.",
    no_args_is_help=True,
    invoke_without_command=True,
)
console = Console()
error_console = Console(stderr=True)
ResultT = TypeVar("ResultT")

ModelOption = Annotated[
    str | None,
    typer.Option("--model", help="Azure model deployment name."),
]
TenantOption = Annotated[
    str | None,
    typer.Option("--tenant-id", help="Microsoft Entra tenant ID."),
]
WritesOption = Annotated[
    bool,
    typer.Option("--allow-writes", help="Expose mutating WorkIQ tools."),
]


def _settings(model: str | None, tenant_id: str | None) -> Settings:
    settings = Settings()
    if model:
        settings.model = model
    if tenant_id:
        settings.tenant_id = tenant_id
    return settings


def _agent_config(thread_id: str) -> RunnableConfig:
    return {"configurable": {"thread_id": thread_id}}


async def _invoke(
    prompt: str,
    *,
    settings: Settings,
    allow_writes: bool,
    thread_id: str,
) -> tuple[str, UsageMetrics, bool]:
    tracker = MetricsTracker()
    async with open_agent(settings, allow_writes=allow_writes) as (agent, _):
        streamed = await stream_agent(
            agent,
            {"messages": [{"role": "user", "content": prompt}]},
            config=_agent_config(thread_id),
            console=console,
        )
    return (
        response_text(streamed.state),
        tracker.update({"messages": streamed.model_messages}),
        streamed.text_rendered,
    )


def _print_metrics(
    label: str,
    metrics: UsageMetrics,
    pricing: ModelPricing,
) -> None:
    tools = ", ".join(f"{name} x{count}" for name, count in sorted(metrics.tool_calls.items()))
    tool_summary = tools or "none"
    cost = metrics.estimated_cost_usd(pricing)
    console.print(
        f"[dim]{label}: input {metrics.input_tokens:,} "
        f"(cached {metrics.cached_input_tokens:,}) | "
        f"output {metrics.output_tokens:,} | model calls {metrics.model_calls:,} | "
        f"tool calls {metrics.tool_call_count:,} ({tool_summary}) | "
        f"estimated model cost ${cost:.6f} USD[/dim]"
    )


async def _chat(settings: Settings, *, allow_writes: bool) -> None:
    thread_id = str(uuid4())
    tracker = MetricsTracker()
    pricing = ModelPricing.from_settings(settings)
    async with open_agent(settings, allow_writes=allow_writes) as (agent, tools):
        console.print(
            f"Connected to WorkIQ with [bold]{len(tools)}[/bold] tools. "
            "Type [bold]/quit[/bold] to exit. Live model, reasoning summary, and tool "
            "events are shown; private chain-of-thought is not exposed."
        )
        while True:
            try:
                prompt = await asyncio.to_thread(console.input, "[bold cyan]workiq> [/bold cyan]")
            except (EOFError, KeyboardInterrupt):
                console.print()
                break

            prompt = prompt.strip()
            if not prompt:
                continue
            if prompt.casefold() in {"/exit", "/quit", "exit", "quit"}:
                break

            streamed = await stream_agent(
                agent,
                {"messages": [{"role": "user", "content": prompt}]},
                config=_agent_config(thread_id),
                console=console,
            )
            if not streamed.text_rendered:
                console.print(response_text(streamed.state))
            turn = tracker.update({"messages": streamed.model_messages})
            _print_metrics("Turn", turn, pricing)
            _print_metrics("Session", tracker.total, pricing)


async def _list_tools(settings: Settings, *, allow_writes: bool) -> None:
    async with open_agent(settings, allow_writes=allow_writes) as (_, tools):
        table = Table("Tool", "Description")
        for tool in sorted(tools, key=lambda item: item.name):
            table.add_row(tool.name, tool.description)
        console.print(table)


def _unwrap_exception(exc: Exception) -> Exception:
    while isinstance(exc, ExceptionGroup):
        group = cast(ExceptionGroup[Exception], exc)
        if len(group.exceptions) != 1:
            break
        exc = group.exceptions[0]
    return cast(Exception, exc)


def _run(coroutine: Coroutine[Any, Any, ResultT]) -> ResultT:
    try:
        return asyncio.run(coroutine)
    except FileNotFoundError as exc:
        error_console.print(f"[red]Missing executable:[/red] {exc.filename or 'npx'}")
        raise typer.Exit(1) from exc
    except Exception as exc:
        exc = _unwrap_exception(exc)
        error_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command()
def ask(
    question: Annotated[str, typer.Argument(help="Question for the WorkIQ agent.")],
    model: ModelOption = None,
    tenant_id: TenantOption = None,
    allow_writes: WritesOption = False,
) -> None:
    """Ask one question and exit."""
    settings = _settings(model, tenant_id)
    answer, metrics, text_rendered = _run(
        _invoke(
            question,
            settings=settings,
            allow_writes=allow_writes,
            thread_id=str(uuid4()),
        )
    )
    if not text_rendered:
        console.print(answer)
    _print_metrics("Request", metrics, ModelPricing.from_settings(settings))


@app.command()
def chat(
    model: ModelOption = None,
    tenant_id: TenantOption = None,
    allow_writes: WritesOption = False,
) -> None:
    """Start a multi-turn interactive session."""
    _run(_chat(_settings(model, tenant_id), allow_writes=allow_writes))


@app.command("tools")
def tools_command(
    tenant_id: TenantOption = None,
    allow_writes: WritesOption = False,
) -> None:
    """List WorkIQ tools available under the current policy."""
    _run(_list_tools(_settings(None, tenant_id), allow_writes=allow_writes))


@app.command()
def doctor() -> None:
    """Check local runtime prerequisites without starting WorkIQ."""
    settings = Settings()
    checks = {
        "Python 3.11+": sys.version_info >= (3, 11),
        "az": shutil.which("az") is not None,
        "node": shutil.which("node") is not None,
        "npx": shutil.which("npx") is not None,
        "model endpoint": bool(settings.model_base_url),
        "model tenant": bool(settings.model_tenant_id),
    }

    for label, passed in checks.items():
        marker = "[green]OK[/green]" if passed else "[red]MISSING[/red]"
        console.print(f"{marker} {label}")

    if not all(checks.values()):
        raise typer.Exit(1)


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", help="Show the version and exit.", is_eager=True),
    ] = None,
) -> None:
    """Query Microsoft 365 context with Deep Agents and WorkIQ."""
    if version:
        console.print(__version__)
        raise typer.Exit()
