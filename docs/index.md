<section class="field-hero" markdown>

# Three protocols. Three control boundaries.

WorkIQ exposes **MCP**, **A2A**, and **REST**. They reach similar Microsoft 365 context, but
they assign orchestration, state, and recovery to different owners.

[Choose a protocol](#choose-by-ownership){ .md-button .md-button--primary }
[Control model](foundations.md){ .md-button }

<picture class="fold-figure">
  <source media="(max-width: 600px)" srcset="assets/images/fold-sequence-mobile.png">
  <img src="assets/images/fold-sequence-desktop.png" width="1400" height="360" alt="A folded paper sequence moves through Intent, Control, State, Output, and Recovery." fetchpriority="high">
</picture>

</section>

<div class="fold-board" role="img" aria-label="MCP exposes caller-invoked tools, A2A delegates a task to WorkIQ, and REST exposes a direct conversational turn.">
  <div class="fold-track fold-track--header" aria-hidden="true">
    <span></span><span>Intent</span><span>Control</span><span>State</span><span>Output</span><span>Recovery</span>
  </div>
  <div class="fold-track fold-track--mcp">
    <strong>MCP</strong><span>Ask / operation</span><span>MCP host</span><span>Host + optional WorkIQ chat</span><span>Answer / result</span><span>MCP host</span>
  </div>
  <div class="fold-track fold-track--a2a">
    <strong>A2A</strong><span>Outcome</span><span>WorkIQ agent</span><span>Task + context</span><span>Artifacts</span><span>Get / subscribe</span>
  </div>
  <div class="fold-track fold-track--rest">
    <strong>REST</strong><span>Chat turn</span><span>WorkIQ</span><span>Conversation</span><span>Response</span><span>Continue turn</span>
  </div>
</div>

## Choose by ownership

<div class="protocol-ledger">
  <a class="protocol-row protocol-row--mcp" href="protocols/mcp/">
    <span class="protocol-code">MCP</span>
    <span><strong>You own the loop.</strong> Let an LLM-based client call WorkIQ <code>ask</code> for a synthesized answer or compose entity, schema, and action tools.</span>
    <span class="protocol-action">Inspect MCP</span>
  </a>
  <a class="protocol-row protocol-row--a2a" href="protocols/a2a/">
    <span class="protocol-code">A2A</span>
    <span><strong>You delegate the outcome.</strong> Track WorkIQ-owned work through task status, artifacts, cancellation, and subscription.</span>
    <span class="protocol-action">Inspect A2A</span>
  </a>
  <a class="protocol-row protocol-row--rest" href="protocols/rest/">
    <span class="protocol-code">REST</span>
    <span><strong>You submit a turn.</strong> Embed a synthesized Microsoft 365 Copilot conversation.</span>
    <span class="protocol-action">Inspect REST</span>
  </a>
</div>

## Sixty-second decision

Question complexity does not choose the protocol. The same complex Microsoft 365 question can be
submitted through MCP `ask`, A2A `SendMessage`, or REST chat. Start with the caller and the contract
the application needs; these are recommendations, not capability boundaries.

| If the architecture starts with... | Start with | Contract you gain |
| --- | --- | --- |
| "My LLM-based client should invoke WorkIQ as a tool" | **MCP** | Synthesized `ask` responses or composable operations inside a caller-owned loop |
| "My agent should delegate work and manage it as a task" | **A2A** | Task identity, status, artifacts, cancellation, and subscription |
| "My app or backend needs a direct Copilot conversation API" | **REST** | Multiturn synthesized chat without an MCP host or task lifecycle |

!!! warning "Reasoning boundary"
    None of the three WorkIQ contracts promises private chain-of-thought. The CLI can show the
    supported reasoning summary from its **outer Azure model** in MCP mode; WorkIQ itself exposes
    public tool results, task events, artifacts, or conversation responses.