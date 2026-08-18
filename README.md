# WorkIQ Deep Agent

A Python CLI that connects [LangChain Deep Agents](https://github.com/langchain-ai/deepagents)
to Microsoft WorkIQ. It uses an Azure-hosted model to answer questions from the signed-in
user's Microsoft 365 context and reports streamed activity, token usage, and estimated cost.

## Work IQ

Work IQ is Microsoft's CLI and MCP server for grounding agents in Microsoft 365 data such
as email, meetings, documents, Teams messages, and people. Its MCP surface provides generic
tools for Copilot reasoning, entity access, and schema discovery; results remain subject to
the signed-in user's permissions and tenant policy.

Official docs: [Work IQ CLI](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/cli),
[MCP overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/mcp/overview),
and [tool reference](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/mcp/tool-reference).

Python runs the agent and launches `npx -y @microsoft/workiq mcp` as a local stdio child
process. That Node.js process authenticates the user and proxies MCP requests to Microsoft's
remote WorkIQ service. Model calls use the Azure Responses API with Azure CLI credentials.

## Prerequisites

- Python 3.11+, Node.js, `npx`, Azure CLI, and [uv](https://docs.astral.sh/uv/)
- A WorkIQ-enabled Microsoft 365 tenant
- An Azure-hosted `gpt-5.6-sol` deployment

See the [WorkIQ CLI documentation](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/cli)
for tenant requirements.

## Setup

```bash
uv sync --python 3.11
az login --tenant <MODEL_TENANT_ID>
npx -y @microsoft/workiq accept-eula
cp .env.example .env
```

Set your Foundry endpoint and model tenant in `.env`:

```dotenv
WORKIQ_AGENT_MODEL_BASE_URL=https://<resource>.services.ai.azure.com/openai/v1/
WORKIQ_AGENT_MODEL_TENANT_ID=<tenant-id>
```

Standard Python also works:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --index-url https://packagefeedproxy.microsoft.io/pypi/simple -e .
```

## Run

```bash
uv run workiq-agent doctor
uv run workiq-agent ask "What decisions did my team make yesterday?"
uv run workiq-agent chat
uv run workiq-agent tools
```

With an activated standard environment, use `workiq-agent` directly or
`python -m workiq_deepagent`. Run `workiq-agent --help` for all options.

WorkIQ tools are read-only by default; `--allow-writes` exposes mutating tools and requires
agent confirmation before use. Tool arguments/results and private model reasoning are not
printed because they may contain workplace data.

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
betterleaks git . --pre-commit --staged --redact
```
