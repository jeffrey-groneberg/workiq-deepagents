<section class="field-hero" markdown>

# Three protocols. Three control boundaries.

WorkIQ exposes **MCP**, **A2A**, and **REST**. They reach similar Microsoft 365 context, but
they move orchestration, state, streaming, and recovery to different owners.

[Choose a protocol](#choose-by-ownership){ .md-button .md-button--primary }
[Control model](foundations.md){ .md-button }

<picture class="fold-figure">
  <source media="(max-width: 600px)" srcset="assets/images/fold-sequence-mobile.png">
  <img src="assets/images/fold-sequence-desktop.png" width="1400" height="360" alt="A folded paper sequence moves through Intent, Control, State, Output, and Recovery." fetchpriority="high">
</picture>

</section>

<div class="fold-board" role="img" aria-label="MCP keeps orchestration in the application, A2A delegates a durable task to WorkIQ, and REST delegates one conversational turn to WorkIQ.">
  <div class="fold-track fold-track--header" aria-hidden="true">
    <span></span><span>Intent</span><span>Control</span><span>State</span><span>Output</span><span>Recovery</span>
  </div>
  <div class="fold-track fold-track--mcp">
    <strong>MCP</strong><span>Operation</span><span>Your app</span><span>Outer graph</span><span>Tool result</span><span>Your app</span>
  </div>
  <div class="fold-track fold-track--a2a">
    <strong>A2A</strong><span>Outcome</span><span>WorkIQ agent</span><span>Task + context</span><span>Artifacts</span><span>Get / subscribe</span>
  </div>
  <div class="fold-track fold-track--rest">
    <strong>REST</strong><span>Chat turn</span><span>WorkIQ</span><span>Conversation</span><span>Snapshots</span><span>Continue turn</span>
  </div>
</div>

## Choose by ownership

<div class="protocol-ledger">
  <a class="protocol-row protocol-row--mcp" href="protocols/mcp/">
    <span class="protocol-code">MCP</span>
    <span><strong>You own the loop.</strong> Let an application model select granular WorkIQ tools, combine providers, and compose the answer.</span>
    <span class="protocol-action">Inspect MCP</span>
  </a>
  <a class="protocol-row protocol-row--a2a" href="protocols/a2a/">
    <span class="protocol-code">A2A</span>
    <span><strong>You delegate the outcome.</strong> Track WorkIQ-owned work through task status, artifacts, cancellation, and subscription.</span>
    <span class="protocol-action">Inspect A2A</span>
  </a>
  <a class="protocol-row protocol-row--rest" href="protocols/rest/">
    <span class="protocol-code">REST</span>
    <span><strong>You submit a turn.</strong> Embed a synthesized Microsoft 365 Copilot conversation with streamed snapshots.</span>
    <span class="protocol-action">Inspect REST</span>
  </a>
</div>

## Sixty-second decision

| If the requirement starts with... | Start with | Contract you gain |
| --- | --- | --- |
| "Read this entity, inspect its schema, or perform an approved action" | **MCP** | Composable tools and caller-owned orchestration |
| "Research this outcome, let me cancel it, and reconnect later" | **A2A** | Durable task identity, status, and artifacts |
| "Answer this Microsoft 365 question in my app" | **REST** | The smallest synthesized chat contract |

!!! warning "Reasoning boundary"
    None of the three WorkIQ contracts promises private chain-of-thought. The CLI can show the
    supported reasoning summary from its **outer Azure model** in MCP mode; WorkIQ itself exposes
    public tool results, task events, artifacts, or conversation responses.

## Read evidence by strength

<div class="evidence-strip">
  <div><span class="evidence-mark evidence-mark--documented">D</span><strong>Documented</strong><br>Explicit in Microsoft Learn or a protocol specification.</div>
  <div><span class="evidence-mark evidence-mark--observed">R</span><strong>Repository</strong><br>Visible in this project's current source code.</div>
  <div><span class="evidence-mark evidence-mark--inference">I</span><strong>Inference</strong><br>A consequence of the contract, not a product guarantee.</div>
</div>

The complete guide keeps these categories separate and links every material product claim to its
source. It was last verified on **2026-08-19**.