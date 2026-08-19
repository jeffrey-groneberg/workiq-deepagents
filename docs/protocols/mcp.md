# MCP - Own the loop

Use MCP when the application must control the model, tool policy, orchestration, and final answer.

<div class="fold-board">
  <div class="fold-track fold-track--header" aria-hidden="true">
    <span></span><span>Intent</span><span>Control</span><span>State</span><span>Output</span><span>Recovery</span>
  </div>
  <div class="fold-track fold-track--mcp">
    <strong>MCP</strong><span>Operation</span><span>Your app</span><span>Outer graph</span><span>Tool result</span><span>Your app</span>
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
fetch /me/messages
create_entity /me/events
do_action /me/sendMail
call_function /search/query
```

The outer model consumes each tool result and decides whether to call another tool or answer.

## Ownership

The application owns:

- model and prompt selection;
- the subset of tools exposed to the model;
- retries, approvals, checkpoints, and final synthesis;
- orchestration across WorkIQ and other providers.

WorkIQ owns operation validation, Microsoft 365 access, and tenant policy enforcement.

## State

MCP does not define an agent conversation. The outer agent owns its transcript and checkpoints.
WorkIQ `ask` can separately return a `conversationId`; persist it only when intentional WorkIQ-side
continuation is required.

This repository starts `@microsoft/workiq mcp` over stdio. Its default policy exposes `ask`,
`call_function`, `fetch`, `get_schema`, `list_agents`, and `search_paths`; `--allow-writes` keeps
every tool discovered at runtime, including `fetch_blob` and mutation tools.

## Authentication and writes

For local stdio, the WorkIQ child process authenticates the signed-in user and owns its token. The
Python process receives MCP messages, not the bearer token. Remote MCP uses OAuth protected-resource
discovery and a resource-bound delegated token.

Authorization is cumulative: delegated grant, user ACLs, tenant policy, path/method policy, and
workload controls must all allow the operation. Keep mutations disabled by default and require an
application approval step before exposing them to the model.

[Delegated authentication details](../authentication.md)

## Concrete applications

| Application | Example ask | Why MCP |
| --- | --- | --- |
| Sales account copilot | "Brief me on Contoso, then draft an approved CRM update." | The outer agent combines WorkIQ with CRM tools and gates the write. |
| Incident command assistant | "Correlate the launch discussion with telemetry and open tickets." | The caller composes Microsoft 365 context with operational systems. |
| Governed workplace operator | "Find the source email, verify the date, then schedule the follow-up." | The application can inspect each call and require approval before mutation. |

## Choose MCP for

- raw entities, schema discovery, or caller-controlled writes;
- an application model that combines WorkIQ with other tools;
- application-owned checkpoints, retries, approvals, and synthesis;
- model-level telemetry or reasoning summaries from the outer model.
