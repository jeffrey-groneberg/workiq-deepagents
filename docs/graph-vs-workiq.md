# WorkIQ vs Microsoft Graph

Microsoft Graph is a resource API, not an answer engine. It is excellent when the application needs
deterministic entities and mutations. For a natural-language ask spanning mail, meetings, Teams, and
files, the application must turn those resources into an answer. WorkIQ supplies that intelligence
layer through MCP, A2A, or REST.

## Executive architecture view

<figure class="workiq-diagram workiq-diagram--raster">
  <img src="../assets/images/graph-vs-workiq.png" width="2560" height="2528" alt="A natural-language workplace ask branches into two paths. Direct Graph retrieves raw cross-workload payloads and serializes selected records and metadata into a high and variable caller-model token load. WorkIQ ask, A2A, or REST keeps retrieval and ranking context inside WorkIQ and returns synthesized output with a lower caller-model token load. Both paths produce a grounded result.">
</figure>

**Executive takeaway:** WorkIQ reduces the custom build and operating surface for grounded workplace
answers. Direct Graph maximizes control, but the application funds and owns the answer pipeline and
typically sends substantially more context into its own model.

**Architect takeaway:** Both enforce user permissions. Direct Graph leaves intent decomposition,
cross-workload retrieval, and synthesis to the application. WorkIQ can own those steps through MCP
`ask`, A2A, or REST; MCP entity tools retain more caller control.

!!! info "Caller-model token boundary"
  A Graph response is data, not automatically an LLM token charge. The token increase happens when
  the application serializes selected messages, meetings, files, content, and metadata into its
  model context for synthesis. Cross-workload fan-out often makes that input substantially larger
  and more variable than WorkIQ `ask`, A2A, or REST, where retrieval and ranking context stays
  inside WorkIQ and synthesized output crosses back to the caller.

  This is a directional architecture comparison, not a published multiplier or a claim about
  WorkIQ's internal processing. Careful `$select`, filtering, ranking, truncation, and caching can
  reduce Graph input tokens. MCP entity tools return raw data and have the same Graph-like token
  profile when their results are inserted into an outer model context.

## Where direct Graph adds work

<div class="comparison-table" markdown>

| Concern | Direct Microsoft Graph | WorkIQ |
| --- | --- | --- |
| Query planning | Select endpoints, entity types, OData or KQL, fields, and date windows. | MCP `ask`, A2A, and REST accept natural-language asks; MCP entity tools expose paths for direct control. |
| Cross-workload retrieval | Use workload endpoints or supported Search API entity combinations, then normalize, deduplicate, and rank results. | WorkIQ assembles permission-trimmed work context across supported sources. |
| Caller-model context tokens | Raw records, content, and metadata selected for synthesis become input tokens; cross-workload fan-out makes the load high and variable. | MCP `ask`, A2A, and REST return synthesized output after internal grounding, usually producing a much smaller caller context. MCP entity tools are the exception. |
| Permissions | Request the least-privileged scope for every workload and operation. | Use delegated WorkIQ permissions plus tenant and path policy. |
| Reliability | Implement paging, `429`/`503` backoff, partial batch retries, and workload-specific errors. | MCP `ask`, A2A, and REST avoid caller-managed retrieval fan-out; MCP entity-tool callers own their operation loop. |
| Synthesis | Choose a model, constrain context, produce citations, and evaluate answer quality. | MCP `ask`, A2A, and REST return synthesized WorkIQ output; MCP entity tools leave composition to the caller. |
| Persistent data | If local state is required, operate change notifications, delta tokens, retention, and deletion. | Typical grounded asks use Microsoft 365's existing index without copying workplace data. |

</div>

These are disadvantages only when the product requirement is **an answer**. Graph remains the
stronger primitive when the requirement is an exact payload, a stable CRUD workflow, app-only
execution, or independent control over storage and models.

## Effort by example

The labels compare production integration surface, not elapsed developer time.

<div class="comparison-table comparison-table--wide" markdown>

| Ask | Direct Graph implementation | WorkIQ route | Relative effort |
| --- | --- | --- | --- |
| "What meetings do I have today?" | Query `calendarView`, handle time zones, recurrence, fields, and paging. | Call MCP `ask`, submit one REST turn, or send an A2A message with required location metadata. | **Low / low.** Prefer Graph for structured events; WorkIQ for a prose answer. |
| "Brief me for my Contoso call." | Search mail, Teams, files, and events with separate scopes and requests; fetch details; merge, rank, and summarize. | Submit the ask through MCP `ask`, REST chat, or A2A according to the caller contract. | **High / low-medium.** |
| "Summarize project risks and correlate them with incident telemetry." | Build Microsoft 365 retrieval, an external telemetry integration, and a model/tool loop. | Give an outer agent WorkIQ MCP and telemetry tools. | **High / medium.** |
| "Investigate the regression; let me cancel and reconnect later." | Add retrieval and synthesis plus a job queue, state store, status API, cancellation, and artifact persistence. | Send an A2A task; persist `task.id` and `contextId`; get, subscribe, or cancel while retained. | **Very high / medium.** |
| "Create this exact approved calendar event." | Call the calendar endpoint with a narrow schema and explicit authorization. | Use an approval-gated MCP `create_entity` call. | **Low / medium.** Graph is usually the cleaner contract. |

</div>

The second row is the important Graph-versus-WorkIQ dividing line, not a protocol boundary. The
[Microsoft Search API](https://learn.microsoft.com/graph/api/resources/search-api-overview?view=graph-rest-1.0)
provides permission-trimmed hits, but mail, events, Teams messages, and files have different scopes,
result shapes, paging limits, and supported combinations. Search does not perform the final
cross-source synthesis.

## Production implications

- Graph clients must always account for paging and throttling; Microsoft documents `@odata.nextLink`,
  `Retry-After`, and separate retry handling for throttled batch members.
- A locally maintained Graph corpus also needs change notifications and delta queries, including
  token expiry and resynchronization behavior.
- WorkIQ reduces that retrieval and synthesis surface, but it is delegated-only, usage billed, and
  AI-generated output still requires verification. REST has no writes or long-running task contract.
- Compare caller-model input tokens separately from WorkIQ service usage. Reducing outer context does
  not mean WorkIQ performs no internal retrieval, reasoning, or billable processing.
- Both approaches enforce the signed-in user's access. WorkIQ does not grant access to content the
  user cannot already reach.

## Microsoft Learn references

- [Work IQ API overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/api-overview)
- [Work IQ overview - Context](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/#context)
- [Work IQ MCP overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/mcp/overview)
- [Work IQ A2A overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/a2a/overview)
- [Work IQ REST overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/rest/overview)
- [Microsoft Search API query guidance](https://learn.microsoft.com/graph/api/resources/search-api-overview?view=graph-rest-1.0)
- [Microsoft Graph best practices](https://learn.microsoft.com/graph/best-practices-concept)
- [Microsoft Graph delta query](https://learn.microsoft.com/graph/delta-query-overview)