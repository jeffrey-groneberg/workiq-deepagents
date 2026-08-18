from decimal import Decimal

from langchain_core.messages import AIMessage

from workiq_deepagent.metrics import MetricsTracker, ModelPricing


def test_tracker_collects_usage_tools_and_cost_without_double_counting() -> None:
    message = AIMessage(
        id="message-1",
        content="done",
        usage_metadata={
            "input_tokens": 1_000_000,
            "output_tokens": 100_000,
            "total_tokens": 1_100_000,
            "input_token_details": {"cache_read": 200_000},
        },
        tool_calls=[{"name": "fetch", "args": {}, "id": "call-1", "type": "tool_call"}],
    )
    result: dict[str, object] = {"messages": [message]}
    tracker = MetricsTracker()
    pricing = ModelPricing(
        input=Decimal("5.00"),
        cached_input=Decimal("0.50"),
        output=Decimal("30.00"),
    )

    turn = tracker.update(result)
    duplicate = tracker.update(result)

    assert turn.input_tokens == 1_000_000
    assert turn.cached_input_tokens == 200_000
    assert turn.output_tokens == 100_000
    assert turn.model_calls == 1
    assert turn.tool_calls == {"fetch": 1}
    assert turn.estimated_cost_usd(pricing) == Decimal("7.10")
    assert duplicate.total_tokens == 0
    assert tracker.total.estimated_cost_usd(pricing) == Decimal("7.10")
