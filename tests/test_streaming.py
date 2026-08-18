from collections.abc import AsyncIterator
from io import StringIO
from typing import Literal, cast

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.schema import StreamEvent
from rich.console import Console

from workiq_deepagent.streaming import EventRenderer, stream_agent


def make_event(
    event: str,
    *,
    run_id: str,
    name: str,
    data: dict[str, object],
    parent_ids: list[str] | None = None,
) -> StreamEvent:
    return cast(
        StreamEvent,
        {
            "event": event,
            "run_id": run_id,
            "name": name,
            "data": data,
            "parent_ids": parent_ids or [],
        },
    )


def test_renderer_shows_progress_without_tool_payloads() -> None:
    output = StringIO()
    renderer = EventRenderer(Console(file=output, color_system=None))

    renderer.handle(
        make_event(
            "on_chat_model_start",
            run_id="model-1",
            name="ChatOpenAI",
            data={"input": {}},
        )
    )
    renderer.handle(
        make_event(
            "on_chat_model_stream",
            run_id="model-1",
            name="ChatOpenAI",
            data={"chunk": AIMessageChunk(content="Checking")},
        )
    )
    renderer.handle(
        make_event(
            "on_chat_model_end",
            run_id="model-1",
            name="ChatOpenAI",
            data={"output": AIMessage(content="Checking")},
        )
    )
    renderer.handle(
        make_event(
            "on_tool_start",
            run_id="tool-1",
            name="fetch",
            data={"input": {"secret": "do-not-print"}},
        )
    )
    renderer.handle(
        make_event(
            "on_tool_end",
            run_id="tool-1",
            name="fetch",
            data={"output": "private-result"},
        )
    )
    renderer.close()

    rendered = output.getvalue()
    assert "assistant> Checking" in rendered
    assert "Model step 1 completed" in rendered
    assert "Tool fetch started" in rendered
    assert "Tool fetch completed" in rendered
    assert "do-not-print" not in rendered
    assert "private-result" not in rendered


class StubAgent:
    async def ainvoke(
        self,
        input: object,
        config: RunnableConfig | None = None,
    ) -> dict[str, object]:
        raise AssertionError("stream_agent must not call ainvoke")

    def astream_events(
        self,
        input: object,
        config: RunnableConfig | None = None,
        *,
        version: Literal["v2"],
    ) -> AsyncIterator[StreamEvent]:
        async def events() -> AsyncIterator[StreamEvent]:
            yield make_event(
                "on_chat_model_stream",
                run_id="model-1",
                name="ChatOpenAI",
                data={"chunk": AIMessageChunk(content="Done")},
                parent_ids=["root"],
            )
            yield make_event(
                "on_chat_model_end",
                run_id="model-1",
                name="ChatOpenAI",
                data={"output": AIMessage(content="Done")},
                parent_ids=["root"],
            )
            yield make_event(
                "on_chain_end",
                run_id="root",
                name="workiq_assistant",
                data={"output": {"messages": [AIMessage(content="Done")]}},
            )

        return events()


@pytest.mark.asyncio
async def test_stream_agent_returns_root_output() -> None:
    output = StringIO()

    result = await stream_agent(
        StubAgent(),
        {"messages": []},
        config={"configurable": {"thread_id": "test"}},
        console=Console(file=output, color_system=None),
    )

    assert result.text_rendered is True
    assert len(result.model_messages) == 1
    assert len(cast(list[object], result.state["messages"])) == 1
    assert output.getvalue().count("Done") == 1
