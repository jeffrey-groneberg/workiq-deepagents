"""Usage and estimated model-cost metrics."""

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from hashlib import sha256
from typing import cast

from langchain_core.messages import AIMessage

from workiq_deepagent.config import Settings

TOKENS_PER_MILLION = Decimal(1_000_000)


@dataclass(frozen=True)
class ModelPricing:
    """USD prices per million tokens."""

    input: Decimal
    cached_input: Decimal
    output: Decimal

    @classmethod
    def from_settings(cls, settings: Settings) -> "ModelPricing":
        """Load pricing from application settings."""
        return cls(
            input=settings.pricing_input_per_million_usd,
            cached_input=settings.pricing_cached_input_per_million_usd,
            output=settings.pricing_output_per_million_usd,
        )


@dataclass
class UsageMetrics:
    """Aggregated usage for one turn or session."""

    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    model_calls: int = 0
    tool_calls: Counter[str] = field(default_factory=lambda: Counter[str]())

    @property
    def total_tokens(self) -> int:
        """Return input plus output tokens."""
        return self.input_tokens + self.output_tokens

    @property
    def tool_call_count(self) -> int:
        """Return the number of tool invocations requested by the model."""
        return self.tool_calls.total()

    def estimated_cost_usd(self, pricing: ModelPricing) -> Decimal:
        """Estimate model cost, accounting for discounted cached input."""
        cached_tokens = min(self.cached_input_tokens, self.input_tokens)
        uncached_tokens = self.input_tokens - cached_tokens
        return (
            Decimal(uncached_tokens) * pricing.input
            + Decimal(cached_tokens) * pricing.cached_input
            + Decimal(self.output_tokens) * pricing.output
        ) / TOKENS_PER_MILLION

    def add(self, other: "UsageMetrics") -> None:
        """Add another metric set in place."""
        self.input_tokens += other.input_tokens
        self.cached_input_tokens += other.cached_input_tokens
        self.output_tokens += other.output_tokens
        self.model_calls += other.model_calls
        self.tool_calls.update(other.tool_calls)


class MetricsTracker:
    """Collect new AI-message usage while ignoring repeated graph history."""

    def __init__(self) -> None:
        self.total = UsageMetrics()
        self._seen_messages: set[str] = set()

    def update(self, result: Mapping[str, object]) -> UsageMetrics:
        """Collect metrics newly observed in an agent result."""
        turn = UsageMetrics()
        messages = result.get("messages")
        if not isinstance(messages, list):
            return turn

        for message in cast(list[object], messages):
            if not isinstance(message, AIMessage):
                continue

            identity = _message_identity(message)
            if identity in self._seen_messages:
                continue
            self._seen_messages.add(identity)

            if usage := message.usage_metadata:
                turn.input_tokens += usage["input_tokens"]
                turn.output_tokens += usage["output_tokens"]
                turn.cached_input_tokens += usage.get("input_token_details", {}).get(
                    "cache_read", 0
                )
                turn.model_calls += 1

            turn.tool_calls.update(call["name"] for call in message.tool_calls)

        self.total.add(turn)
        return turn


def _message_identity(message: AIMessage) -> str:
    if message.id:
        return message.id

    return sha256(message.model_dump_json().encode()).hexdigest()
