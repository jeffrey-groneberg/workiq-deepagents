# REST - Delegate a turn

Use REST when the product needs a grounded Microsoft 365 Copilot conversation without an external
model, tool graph, or task lifecycle.

<div class="fold-board">
  <div class="fold-track fold-track--header" aria-hidden="true">
    <span></span><span>Intent</span><span>Control</span><span>State</span><span>Output</span><span>Recovery</span>
  </div>
  <div class="fold-track fold-track--rest">
    <strong>REST</strong><span>Chat turn</span><span>WorkIQ</span><span>Conversation</span><span>Response</span><span>Continue</span>
  </div>
</div>

## Contract

1. Create a conversation.
2. Persist its `conversationId` by tenant, user, and owning chat.
3. Submit chat turns.
4. Render answer text and grounding metadata.

WorkIQ owns enterprise and web grounding plus synthesis. Responses can include references,
attributions, adaptive cards, and sensitivity metadata.

## Per-turn controls

| Control | Purpose |
| --- | --- |
| `locationHint` (required) | Time-zone-sensitive grounding |
| `contextualResources` | Explicit OneDrive or SharePoint files |
| Web-grounding toggle | Disable web grounding for the turn |
| `additionalContext` | Application-supplied context |

Do not assume per-turn controls become conversation defaults.

REST chat and MCP `ask` can both accept complex natural-language questions and return synthesized
answers, and either can sit behind an application backend. Choose REST for an explicit HTTP
conversation-resource contract: create a conversation, submit turns, and render responses. Choose
MCP when an existing MCP host should discover and invoke WorkIQ alongside other tools. Question
complexity and caller location are not the differentiators.

## Boundaries

REST Chat does not expose:

- caller-facing entity primitives;
- action skills such as sending mail or scheduling meetings;
- caller-controlled tools or model selection;
- task identity, cancellation, or task recovery.

Use A2A for delegated work with a lifecycle. Use MCP for tool-based invocation, including `ask`,
precise reads, writes, or caller-owned cross-provider orchestration.

## Authentication

REST requires a delegated token for the WorkIQ audience with `WorkIQAgent.Ask`. Local clients use a
public-client PKCE flow; hosted backends exchange the frontend user assertion through OBO.

No app-only equivalent is currently published for this endpoint. Conversation IDs remain scoped to
the authorized tenant, user, and owning chat.

[Delegated authentication details](../authentication.md)

## Concrete applications

| Application | Example turn | Why REST |
| --- | --- | --- |
| Intranet workplace chat | "What changed in Project Atlas this week?" | The app renders a grounded answer without hosting another model. |
| CRM meeting-prep panel | "Brief me for my next call with Contoso." | A small backend can submit a turn and display references beside the record. |
| Employee mobile assistant | "Summarize the decisions from yesterday's meetings." | Conversation continuity is useful, but no task lifecycle or writes are needed. |

## Choose REST for

- direct application or backend chat;
- synthesized Microsoft 365 Copilot answers;
- minimal orchestration and infrastructure;
- references, attributions, and sensitivity metadata;
- read-only conversational experiences.
