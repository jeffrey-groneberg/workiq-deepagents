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

    ```mermaid
    sequenceDiagram
        participant C as Application
        participant G as Caller model
        participant W as WorkIQ MCP
        C->>G: Prompt + approved tools
        G-->>C: Tool call
        C->>W: tools/call
        W-->>C: Tool result
        C->>G: Continue loop
    ```

    The application owns planning, policy, retries, and final synthesis.

=== "A2A"

    ```mermaid
    sequenceDiagram
        participant C as Caller
        participant W as WorkIQ agent
        C->>W: Outcome-oriented message
        W-->>C: Task + context
        C->>W: Get or cancel task
        W-->>C: Status + artifacts
    ```

    WorkIQ owns execution; the caller owns the public task lifecycle.

=== "REST"

    ```mermaid
    sequenceDiagram
        participant C as Client
        participant W as WorkIQ REST
        C->>W: Conversation turn
        W-->>C: Grounded response
    ```

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
