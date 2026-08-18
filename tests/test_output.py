from dataclasses import dataclass
from typing import Any

import pytest

from workiq_deepagent.output import response_text


@dataclass
class Message:
    content: Any


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        ({}, "No response was returned."),
        ({"messages": []}, "No response was returned."),
        ({"messages": [Message("Hello")]}, "Hello"),
        (
            {"messages": [Message([{"type": "text", "text": "First"}, "Second"])]},
            "First\nSecond",
        ),
    ],
)
def test_response_text(result: dict[str, Any], expected: str) -> None:
    assert response_text(result) == expected
