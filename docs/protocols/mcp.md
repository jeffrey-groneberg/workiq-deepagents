# MCP - Invoke WorkIQ as tools

Use MCP when an LLM-based client should invoke WorkIQ as tools. Call `ask` with a natural-language
question for a synthesized Microsoft 365 Copilot response, or use entity, schema, and action tools
inside caller-owned orchestration.

<div class="fold-board">
  <div class="fold-track fold-track--header" aria-hidden="true">
    <span></span><span>Intent</span><span>Control</span><span>State</span><span>Output</span><span>Recovery</span>
  </div>
  <div class="fold-track fold-track--mcp">
    <strong>MCP</strong><span>Ask / operation</span><span>MCP host</span><span>Host + optional WorkIQ chat</span><span>Answer / result</span><span>MCP host</span>
  </div>
</div>

## Contract

| Category | Tools | Role |
| --- | --- | --- |
| Entity | `fetch`, `fetch_blob`, `create_entity`, `update_entity`, `delete_entity`, `do_action`, `call_function` | Resource-path operations |
| Copilot | `ask`, `list_agents` | Agent invocation and discovery |
| Schema | `get_schema`, `search_paths` | Runtime contract discovery |

Treat runtime `tools/list` as authoritative. The tool is the verb and the relative Microsoft 365
path is the object:

```text
ask "Brief me for my next customer call"
fetch /me/messages
create_entity /me/events
do_action /me/sendMail
call_function /search/query
```

The MCP host decides whether and when to call a tool, then consumes its result. `ask` is not a raw
retrieval primitive: it invokes Microsoft 365 Copilot and returns a synthesized `response` plus a
`conversationId`. The host can render that response directly, incorporate it into an outer model,
or continue the WorkIQ conversation.

## Ownership

The MCP host owns:

- which tools are available and when they are invoked;
- the outer model and prompt, when an outer model is used;
- retries, approvals, checkpoints, and result handling;
- orchestration across WorkIQ and other providers.

WorkIQ owns operation validation, Microsoft 365 access, and tenant policy enforcement. For `ask`,
WorkIQ also owns Microsoft 365 grounding and synthesis inside that tool call.

## State

MCP does not define the host's agent conversation. If the host uses an outer agent, that agent owns
its transcript and checkpoints. WorkIQ `ask` separately returns a `conversationId`. Discard it for
a one-shot call; persist it with the tenant, user, and host thread only when a later `ask` should
continue that same WorkIQ conversation.

This repository starts `@microsoft/workiq mcp` over stdio. Its default policy exposes `ask`,
`call_function`, `fetch`, `get_schema`, `list_agents`, and `search_paths`; `--allow-writes` keeps
every tool discovered at runtime, including `fetch_blob` and mutation tools.

## Authentication and writes

For local stdio, the WorkIQ child process authenticates the signed-in user and owns its token. The
Python process receives MCP messages, not the bearer token. Remote MCP uses OAuth protected-resource
discovery and a resource-bound delegated token.

Authorization is cumulative: delegated grant, user ACLs, tenant policy, path/method policy, and
workload controls must all allow the operation. Keep mutation tools unavailable by default.
Enabling them is not approval: an application-controlled interrupt must show the exact operation
and arguments, then require fresh user confirmation immediately before invocation. Model-generated
text cannot satisfy that gate.

[Delegated authentication details](../authentication.md)

## Concrete applications

| Application | Example ask | Why MCP |
| --- | --- | --- |
| Sales account copilot | "Brief me on Contoso, then draft an approved CRM update." | The outer agent combines WorkIQ with CRM tools and gates the write. |
| Incident command assistant | "Correlate the launch discussion with telemetry and open tickets." | The caller composes Microsoft 365 context with operational systems. |
| Governed workplace operator | "Find the source email, verify the date, then schedule the follow-up." | The application can inspect each call and require approval before mutation. |

## Choose MCP for

- a natural-language Microsoft 365 question invoked as `ask` by an LLM-based client;
- raw entities, schema discovery, or caller-controlled writes;
- an application model that combines WorkIQ with other tools;
- application-owned checkpoints, retries, approvals, or cross-provider synthesis;
- model-level telemetry or reasoning summaries from the outer model.

[Build the MCP + Deep Agents example](../mcp-deepagents.md)
