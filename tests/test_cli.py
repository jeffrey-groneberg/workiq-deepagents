import pytest
from typer.testing import CliRunner

from workiq_deepagent import __version__
from workiq_deepagent.cli import app

runner = CliRunner()


def executable_path(_: str) -> str:
    return "/usr/bin/tool"


def test_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_doctor_passes_when_prerequisites_are_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "WORKIQ_AGENT_MODEL_BASE_URL",
        "https://example.openai.azure.com/openai/v1/",
    )
    monkeypatch.setenv("WORKIQ_AGENT_MODEL_TENANT_ID", "model-tenant-id")
    monkeypatch.setattr("workiq_deepagent.cli.shutil.which", executable_path)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "MISSING" not in result.stdout
