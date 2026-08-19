import pytest

from workiq_deepagent.config import Settings
from workiq_deepagent.model import create_model


def test_model_uses_streaming_responses_api() -> None:
    model = create_model(
        Settings(
            model_base_url="https://example.openai.azure.com/openai/v1/",
            model_tenant_id="tenant-id",
        )
    )

    assert model.streaming is True
    assert model.use_responses_api is True
    assert model.output_version == "responses/v1"
    assert model.reasoning == {"summary": "auto"}


def test_model_requires_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKIQ_AGENT_MODEL_BASE_URL", raising=False)

    with pytest.raises(ValueError, match="WORKIQ_AGENT_MODEL_BASE_URL"):
        create_model(
            Settings(
                model_base_url="",
                model_tenant_id="tenant-id",
            )
        )
