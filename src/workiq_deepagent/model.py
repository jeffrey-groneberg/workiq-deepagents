"""Model construction for the Azure-hosted Deep Agent."""

from azure.identity import AzureCliCredential, get_bearer_token_provider
from langchain_openai import ChatOpenAI

from workiq_deepagent.config import Settings


def create_model(settings: Settings) -> ChatOpenAI:
    """Create the selected Foundry model using the current Azure CLI identity."""
    if not settings.model_base_url:
        msg = "WORKIQ_AGENT_MODEL_BASE_URL must be configured."
        raise ValueError(msg)
    if not settings.model_tenant_id:
        msg = "WORKIQ_AGENT_MODEL_TENANT_ID must be configured."
        raise ValueError(msg)

    token_provider = get_bearer_token_provider(
        AzureCliCredential(tenant_id=settings.model_tenant_id),
        settings.model_token_scope,
    )
    return ChatOpenAI(
        model=settings.model,
        base_url=settings.model_base_url,
        api_key=token_provider,
        reasoning={"summary": "auto"},
        streaming=True,
        use_responses_api=True,
        output_version="responses/v1",
    )
