"""Live terminal rendering for Deep Agent stream events."""

from collections.abc import Mapping
from dataclasses import dataclass
from time import monotonic
from typing import cast

from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.schema import StreamEvent
from rich.console import Console
from rich.status import Status

from workiq_deepagent.agent import AgentRunner


@dataclass(frozen=True)
class StreamResult:
    """Final graph state and whether answer text was rendered."""

    state: dict[str, object]
    model_messages: list[AIMessage]
    text_rendered: bool


class EventRenderer:
    """Render model and tool lifecycle events without logging sensitive payloads."""

    def __init__(self, console: Console) -> None:
        self.console = console
        self.text_rendered = False
        self._answer_line_open = False
        self._reasoning_line_open = False
        self._model_step = 0
        self._model_started: dict[str, tuple[int, float]] = {}
        self._tool_started: dict[str, tuple[str, float]] = {}
        self._status: Status | None = None

    def handle(self, event: StreamEvent) -> None:
        """Render one standard LangChain stream event."""
        event_name = event["event"]
        run_id = event["run_id"]
        name = event.get("name", "unknown")

        if event_name == "on_chat_model_start":
            self._model_step += 1
            self._model_started[run_id] = (self._model_step, monotonic())
            self._set_status(f"Model step {self._model_step} working...")
        elif event_name == "on_chat_model_stream":
            self._render_model_chunk(event)
        elif event_name == "on_chat_model_end":
            self._finish_model(run_id)
        elif event_name == "on_tool_start":
            self._start_tool(run_id, name)
        elif event_name == "on_tool_end":
            self._finish_tool(run_id, succeeded=True)
        elif event_name == "on_tool_error":
            self._finish_tool(run_id, succeeded=False)

    def close(self) -> None:
        """Restore the terminal after streaming finishes or fails."""
        self._clear_status()
        self._finish_reasoning_line()
        self._finish_answer_line()

    def _render_model_chunk(self, event: StreamEvent) -> None:
        chunk = event["data"].get("chunk")
        if not isinstance(chunk, AIMessageChunk):
            return

        reasoning_parts: list[str] = []
        for block in chunk.content_blocks:
            if block.get("type") != "reasoning":
                continue
            reasoning = block.get("reasoning")
            if isinstance(reasoning, str):
                reasoning_parts.append(reasoning)
        if reasoning_parts:
            self._render_reasoning("".join(reasoning_parts))

        text = str(chunk.text)
        if not text:
            return

        self._clear_status()
        self._finish_reasoning_line()
        if not self._answer_line_open:
            self.console.print("[bold green]assistant>[/bold green] ", end="")
            self._answer_line_open = True
        self.console.print(text, end="", markup=False, highlight=False, soft_wrap=True)
        self.text_rendered = True

    def _finish_model(self, run_id: str) -> None:
        self._clear_status()
        self._finish_reasoning_line()
        self._finish_answer_line()
        step, started = self._model_started.pop(run_id, (self._model_step, monotonic()))
        elapsed = monotonic() - started
        self.console.print(f"[dim]Model step {step} completed in {elapsed:.1f}s[/dim]")

    def _render_reasoning(self, reasoning: str) -> None:
        self._clear_status()
        self._finish_answer_line()
        if not self._reasoning_line_open:
            self.console.print("[dim]thought> [/dim]", end="")
            self._reasoning_line_open = True
        self.console.print(
            reasoning,
            end="",
            style="dim",
            markup=False,
            highlight=False,
            soft_wrap=True,
        )

    def _start_tool(self, run_id: str, name: str) -> None:
        self._clear_status()
        self._finish_reasoning_line()
        self._finish_answer_line()
        self._tool_started[run_id] = (name, monotonic())
        self.console.print(f"[cyan]Tool {name} started[/cyan]")
        self._set_status(f"Tool {name} running...")

    def _finish_tool(self, run_id: str, *, succeeded: bool) -> None:
        self._clear_status()
        name, started = self._tool_started.pop(run_id, ("unknown", monotonic()))
        elapsed = monotonic() - started
        if succeeded:
            self.console.print(f"[cyan]Tool {name} completed in {elapsed:.1f}s[/cyan]")
        else:
            self.console.print(f"[red]Tool {name} failed after {elapsed:.1f}s[/red]")

    def _set_status(self, message: str) -> None:
        self._clear_status()
        self._status = self.console.status(message, spinner="dots")
        self._status.start()

    def _clear_status(self) -> None:
        if self._status is not None:
            self._status.stop()
            self._status = None

    def _finish_answer_line(self) -> None:
        if self._answer_line_open:
            self.console.print()
            self._answer_line_open = False

    def _finish_reasoning_line(self) -> None:
        if self._reasoning_line_open:
            self.console.print()
            self._reasoning_line_open = False


async def stream_agent(
    agent: AgentRunner,
    input: object,
    *,
    config: RunnableConfig,
    console: Console,
) -> StreamResult:
    """Stream one agent invocation and return its final graph state."""
    renderer = EventRenderer(console)
    final_state: dict[str, object] | None = None
    model_messages: list[AIMessage] = []
    try:
        async for event in agent.astream_events(input, config=config, version="v2"):
            renderer.handle(event)
            output = event["data"].get("output")
            if event["event"] == "on_chat_model_end" and isinstance(output, AIMessage):
                model_messages.append(output)
            if (
                event["event"] == "on_chain_end"
                and not event.get("parent_ids")
                and isinstance(output, Mapping)
            ):
                final_state = dict(cast(Mapping[str, object], output))
    finally:
        renderer.close()

    if final_state is None:
        msg = "The agent stream ended without a final result."
        raise RuntimeError(msg)
    return StreamResult(
        state=final_state,
        model_messages=model_messages,
        text_rendered=renderer.text_rendered,
    )
