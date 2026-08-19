# Evidence ledger

The guide separates three evidence strengths so protocol possibility is not mistaken for current
WorkIQ product behavior.

| Mark | Meaning | Appropriate claim |
| --- | --- | --- |
| **Documented** | Explicit in Microsoft Learn or a protocol specification | "WorkIQ documents `GetTask`." |
| **Repository** | Directly visible in this project's source | "The CLI starts WorkIQ over stdio." |
| **Inference** | A consequence of documented contracts | "REST snapshots should be reconciled by message ID." |

## Proof matrix

| Claim | Evidence |
| --- | --- |
| Current WorkIQ MCP details list eleven tools; overview text still says ten | The detailed reference adds `fetch_blob` to the overview's ten-tool summary. [[S1]](#s1) [[S2]](#s2) |
| MCP tools operate on relative resource paths | WorkIQ MCP overview and entity model. [[S1]](#s1) [[S3]](#s3) |
| MCP supports protocol progress notifications | MCP progress contract. [[P1]](#p1) |
| WorkIQ `ask` does not document incremental result events | Its result is completed `TextContent`; no WorkIQ progress event is specified. [[S2]](#s2) |
| WorkIQ A2A advertises streaming | The published Agent Card has `streaming: true`. [[S5]](#s5) |
| WorkIQ supports A2A task management | WorkIQ documents `GetTask`, `CancelTask`, and `SubscribeToTask`. [[S5]](#s5) |
| A2A distinguishes status and artifact updates | A2A defines both event classes plus append/final-chunk fields. [[P2]](#p2) |
| WorkIQ REST has an SSE endpoint | `chatOverStream` returns `text/event-stream`. [[S8]](#s8) |
| REST events are snapshots, not token deltas | SSE data contains `copilotConversation`; examples repeat state. [[S8]](#s8) |
| REST lacks actions and durable long-running tasks | WorkIQ REST known limitations. [[S7]](#s7) |
| Direct WorkIQ agent access is delegated | `WorkIQAgent.Ask` requires admin consent and has no listed application permission. [[S10]](#s10) |
| WorkIQ data is permission-trimmed | WorkIQ tool reference and API overview. [[S2]](#s2) [[S11]](#s11) |
| A hosted caller can use OBO | WorkIQ A2A quickstart prescribes confidential client plus OBO. [[S6]](#s6) |
| Remote MCP uses OAuth protected-resource discovery | MCP authorization and WorkIQ MCP overview. [[P1]](#p1) [[S1]](#s1) |
| MCP mutation is policy-controlled and blocked by default | WorkIQ tool reference and policy governance. [[S2]](#s2) [[S4]](#s4) |

## Microsoft WorkIQ sources

### S1 - WorkIQ MCP overview { #s1 }

[Microsoft Learn: WorkIQ MCP overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/mcp/overview)

Supports the generic path-oriented tool model, OAuth discovery, permission trimming, and the
overview's ten-tool statement.

### S2 - WorkIQ MCP tool reference { #s2 }

[Microsoft Learn: MCP tool reference](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/mcp/tool-reference)

Defines the current eleven listed tools, entity result shapes, `ask` result,
`conversationId`, and policy-controlled mutations.

### S3 - WorkIQ MCP entity model { #s3 }

[Microsoft Learn: MCP entity model](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/mcp/entity-model)

Defines generic operations over relative Microsoft 365 resource paths.

### S4 - WorkIQ MCP policy governance { #s4 }

[Microsoft Learn: policy governance](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/mcp/policy-governance-mcp)

Describes tenant control over paths, methods, and mutations.

### S5 - WorkIQ A2A overview { #s5 }

[Microsoft Learn: WorkIQ A2A overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/a2a/overview)

Defines versions, endpoints, Agent Card capabilities, task methods, streaming, and auth.

### S6 - WorkIQ A2A quickstart { #s6 }

[Microsoft Learn: WorkIQ A2A quickstart](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/a2a/quickstart)

Documents public-client interactive authentication and confidential-client OBO guidance.

### S7 - WorkIQ REST overview { #s7 }

[Microsoft Learn: WorkIQ REST overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/rest/overview)

Defines grounding behavior, context controls, known limitations, and long-running timeout risk.

### S8 - WorkIQ REST chatOverStream { #s8 }

[Microsoft Learn: `chatOverStream`](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/rest/copilotconversation-chatoverstream)

Defines the SSE request and `copilotConversation` snapshot response.

### S9 - REST response message resource { #s9 }

[Microsoft Learn: response message](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/rest/resources/copilotconversationresponsemessage)

Defines text, adaptive cards, references, attributions, and sensitivity metadata.

### S10 - WorkIQ permissions { #s10 }

[Microsoft Learn: WorkIQ API permissions](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/permissions)

Lists delegated `WorkIQAgent.Ask`, required admin consent, and no application-permission
equivalent.

### S11 - WorkIQ API overview { #s11 }

[Microsoft Learn: WorkIQ API overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/api-overview)

Supports user-context and permission-trimming behavior.

## Protocol specifications

### P1 - Model Context Protocol { #p1 }

[Model Context Protocol specification](https://modelcontextprotocol.io/specification/2026-07-28)

Defines transports, JSON-RPC, progress, cancellation, and OAuth protected-resource discovery.

### P2 - Agent2Agent Protocol { #p2 }

[Agent2Agent Protocol specification](https://a2a-protocol.org/latest/specification/)

Defines messages, tasks, artifacts, contexts, SSE events, and artifact reconstruction semantics.

## Repository evidence

### R1 - Agent lifecycle { #r1 }

[`src/workiq_deepagent/agent.py`](https://github.com/jeffrey-groneberg/workiq-deepagents/blob/main/src/workiq_deepagent/agent.py)

### R2 - Stream renderer { #r2 }

[`src/workiq_deepagent/streaming.py`](https://github.com/jeffrey-groneberg/workiq-deepagents/blob/main/src/workiq_deepagent/streaming.py)

### R3 - Azure model configuration { #r3 }

[`src/workiq_deepagent/model.py`](https://github.com/jeffrey-groneberg/workiq-deepagents/blob/main/src/workiq_deepagent/model.py)

### R4 - Tool policy and MCP command { #r4 }

[`src/workiq_deepagent/config.py`](https://github.com/jeffrey-groneberg/workiq-deepagents/blob/main/src/workiq_deepagent/config.py)

## Verification notes

- Microsoft Learn and protocol specifications were queried on **2026-08-19**.
- Product behavior can change independently of protocol standards. Recheck Agent Cards, OAuth
  metadata, scopes, policy, API versions, and preview status during implementation.
- The WorkIQ overview says "10 tools," while the detailed reference currently lists eleven after
  adding `fetch_blob`. Runtime `tools/list` is authoritative.
- Public permission documentation explicitly names `WorkIQAgent.Ask`, but does not prove that it
  authorizes every MCP entity and schema capability. Discover scopes from deployed protected
  resource metadata rather than inventing scope names.
- Examples show contract shape. Production clients still need robust SSE framing, JSON-RPC error
  handling, retry policy, token caching, correlation IDs, cancellation, and sensitive-data controls.