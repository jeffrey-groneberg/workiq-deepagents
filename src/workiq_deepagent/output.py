"""Helpers for rendering LangChain message content in a terminal."""

from collections.abc import Mapping
from typing import Protocol, cast, runtime_checkable


@runtime_checkable
class MessageContent(Protocol):
    """Message shape needed by terminal rendering."""

    @property
    def content(self) -> object: ...


def response_text(result: Mapping[str, object]) -> str:
    """Extract readable text from the final message in an agent result."""
    messages = result.get("messages")
    if not isinstance(messages, list) or not messages:
        return "No response was returned."

    message_list = cast(list[object], messages)
    last_message = message_list[-1]
    content = last_message.content if isinstance(last_message, MessageContent) else ""
    if isinstance(content, str):
        return content or "No response was returned."

    if isinstance(content, list):
        parts: list[str] = []
        for block in cast(list[object], content):
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = cast(dict[object, object], block).get("text")
                if isinstance(text, str):
                    parts.append(text)
        if parts:
            return "\n".join(parts)

    return str(cast(object, content)) if content else "No response was returned."
