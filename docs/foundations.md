# Control and state

MCP, A2A, and REST expose different ownership models, not interchangeable wrappers around one
WorkIQ API.

## Architecture matrix

| Concern | MCP | A2A | REST |
| --- | --- | --- | --- |
| Public abstraction | Tool | Task | Conversation turn |
| Orchestration owner | Caller | WorkIQ agent | WorkIQ |
| Execution model selected by caller | Yes | No | No |
| Granular entity operations | Yes | No public primitive | No |
| Caller-controlled writes | Yes, policy gated | Agent-dependent | No |
| Work identity | Caller-defined | `task.id` | No task object |
| Conversation state | Outer graph, optional WorkIQ `conversationId` | `contextId` | `conversationId` |
| Recovery owner | Caller | WorkIQ task contract | Caller resubmits or continues |

## Control planes

=== "MCP"

    <figure class="workiq-diagram workiq-diagram--raster">
    <img src="../assets/images/mcp-control-plane.png" width="2482" height="1740" alt="The application sends a prompt and approved tools to the caller model. The model returns a tool call. The application calls WorkIQ MCP, receives a tool result, and continues the model loop.">
    </figure>

    The application owns planning, policy, retries, and final synthesis.

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
