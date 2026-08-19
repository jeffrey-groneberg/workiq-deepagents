# Control and state

MCP, A2A, and REST expose different integration contracts with overlapping ability to answer
natural-language questions. Query complexity does not distinguish them.

## Architecture matrix

| Concern | MCP | A2A | REST |
| --- | --- | --- | --- |
| Public abstraction | Tool | Task | Conversation turn |
| Recommended caller | LLM-based client | Another agent | Application or backend |
| Natural-language answer | `ask` response | Task artifact | Chat response |
| Orchestration owner | MCP host; WorkIQ inside `ask` | WorkIQ agent | WorkIQ |
| Granular entity operations | Yes | No public primitive | No |
| Caller-controlled writes | Yes, policy gated | Agent-dependent | No |
| Work identity | Caller-defined | `task.id` | No task object |
| Conversation state | Outer graph, optional WorkIQ `conversationId` | `contextId` | `conversationId` |
| Recovery owner | Caller | WorkIQ task contract | Caller resubmits or continues |

## Control planes

=== "MCP"

    <figure class="workiq-diagram workiq-diagram--raster">
    <img src="../assets/images/mcp-control-plane.png" width="2482" height="1740" alt="The MCP host can optionally use an outer model to select a tool, then calls WorkIQ MCP. WorkIQ returns either a synthesized answer from ask or an operation result; continuing an outer model loop is optional.">
    </figure>

    The MCP host owns policy, invocation, retries, and result handling. WorkIQ owns Microsoft 365
    grounding and synthesis inside an `ask` call; an outer model is optional.

=== "A2A"

    <figure class="workiq-diagram workiq-diagram--raster">
    <img src="../assets/images/a2a-control-plane.png" width="2472" height="1680" alt="The caller sends an outcome-oriented message to the WorkIQ agent and receives a task and context. The caller can get or cancel the task and receives status and artifacts.">
    </figure>

    WorkIQ owns execution; the caller owns the public task lifecycle.

=== "REST"

    <figure class="workiq-diagram workiq-diagram--raster">
    <img src="../assets/images/rest-control-plane.png" width="2482" height="1324" alt="The client sends a conversation turn to WorkIQ REST with a solid arrow. WorkIQ REST returns a grounded response to the client with a dashed arrow.">
    </figure>

    WorkIQ owns the turn. The client owns conversation persistence and presentation.

## State invariants

| Identifier | Keep with |
| --- | --- |
| Deep Agent checkpoint | Application thread |
| MCP `ask` `conversationId` | Tenant + user + outer thread |
| A2A `contextId` | Tenant + user + workflow |
| A2A `task.id` | Tenant + user + delegated operation |
| REST `conversationId` | Tenant + user + chat |

These are application storage boundaries, not service retention guarantees. Transport sessions are
not conversation state, and identifiers are not credentials. Persist every identifier within the
delegated user's identity boundary.

MCP has one additional trap: the outer graph and WorkIQ `ask` can each maintain context. Reusing an
inner `conversationId` introduces state that may not be visible in the outer transcript.
