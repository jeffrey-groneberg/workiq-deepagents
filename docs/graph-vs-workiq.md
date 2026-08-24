# WorkIQ vs Microsoft Graph

Microsoft Graph is a resource API, not an answer engine. It is excellent when the application needs
deterministic entities and mutations. For a natural-language ask spanning mail, meetings, Teams, and
files, the application must turn those resources into an answer. WorkIQ supplies that intelligence
layer through MCP, A2A, or REST.

## Executive architecture view

<figure class="workiq-diagram workiq-diagram--raster">
  <img src="../assets/images/graph-vs-workiq.png" width="2560" height="2660" alt="A natural-language workplace ask branches into two integration paths. Direct Microsoft Graph requires the application to plan source-specific calls, retrieve term- or KQL-based search hits or semantic chunks from Copilot Retrieval for supported file sources, and perform synthesis. Those selected payloads create caller-model tokens when inserted into the application's prompt. WorkIQ natural-language surfaces manage cross-workload retrieval, ranking, reasoning, and synthesis inside the service, then return a compact grounded result. MCP entity tools remain raw-data operations.">
</figure>

**Executive takeaway:** WorkIQ reduces the custom build and operating surface for grounded workplace
answers. Direct Graph maximizes control, but the application funds and owns the answer pipeline and
typically sends substantially more context into its own model.

**Architect takeaway:** Both enforce user permissions. Direct Graph leaves intent decomposition,
cross-workload retrieval, and synthesis to the application. WorkIQ can own those steps through MCP
`ask`, A2A, or REST; MCP entity tools retain more caller control.

!!! info "Caller-model token boundary"
    A Graph response is not measured in LLM tokens by itself. It becomes model input when the
    application serializes selected messages, meetings, files, content, and metadata into a prompt
    for synthesis. Cross-workload fan-out can make that caller-owned context large and variable.
    With WorkIQ `ask`, A2A, or REST, retrieval and ranking context stays inside WorkIQ and synthesized
    output crosses back to the caller.

    This is a directional architecture comparison, not a published multiplier or a claim about
    WorkIQ's internal processing. Careful `$select`, filtering, ranking, truncation, and caching can
    reduce Graph input tokens. MCP entity tools return raw data and have the same Graph-like token
    profile when their results are inserted into an outer model context.

    The orange callouts separate the token-producing stages:

    1. **Planning tokens:** the outer model receives its prompt, tool schemas, and call arguments.
    2. **Payload tokens:** each Graph response contributes raw JSON, content, and metadata when the
       application inserts it into model context.
    3. **Loop tokens:** later reasoning turns can resend conversation history and prior tool results.
    4. **Multipliers:** paging, retries, and additional source calls can repeat arguments and results.

    On the WorkIQ lane, request and compact-result tokens cross the caller boundary. Retrieval calls,
    source payloads, ranking, and reasoning are still processed, but remain inside WorkIQ rather than
    being assembled in the caller's outer model context.

## Does direct Graph provide semantic retrieval?

**Not through one uniform search contract.** Direct Microsoft Graph includes resource endpoints,
the Microsoft Search API, and newer Copilot APIs with different source coverage and retrieval
behavior. "Graph search" therefore needs a qualifier.

| Surface | Documented scope | Retrieval contract |
| --- | --- | --- |
| Resource APIs and Microsoft Search `POST /search/query` | A defined set that includes Outlook messages and events, Teams messages, SharePoint and OneDrive items, people, and connector content; not every Graph entity. | Free text, KQL, properties, and entity-specific relevance ranking. Microsoft does not document a semantic or vector query mode for this surface. Ranking orders the matches returned for the supplied query; it is not a semantic-match guarantee. |
| Copilot Retrieval `POST /v1.0/copilot/retrieval` | SharePoint, OneDrive, and Copilot connectors. | Natural-language retrieval from the Copilot hybrid index, including query transformation and relevant text chunks. Semantic and hybrid retrieval apply only to documented file types; other supported formats are lexical. |
| Copilot Search API (preview) | A personalized working set of OneDrive for work or school content. | Hybrid lexical and semantic file discovery. It does not currently add Outlook, Teams, or general SharePoint search coverage. |
| WorkIQ `ask`, A2A, and REST | Supported organizational context across Microsoft 365 and connected systems. | Interprets the workplace request, assembles grounding context, and returns a synthesized answer or artifact. WorkIQ documents semantic understanding, but this should not be read as identical semantic coverage for every entity type. |

!!! info "Application and backend cost scope"

    These prices apply when an application or backend calls the APIs, not to use of the Copilot user
    interface. Copilot Retrieval and Copilot Search calls are made on behalf of a signed-in user. The
    represented user's license determines whether the integration's call is included or billable.

    | Call made by the integration | Incremental API charge |
    | --- | --- |
    | Copilot Retrieval for a user with a Microsoft 365 Copilot add-on license | **$0 per call.** API access is included in that user's license. |
    | Copilot Retrieval for a user without the add-on license | **$0.10 per API call** in the pay-as-you-go preview, billed to the tenant's linked Azure subscription. For example, 1,000 backend calls cost $100. This route covers SharePoint and Copilot connectors, not OneDrive. |
    | Copilot Search API (preview) | **$0 per call**, but only for users with the add-on license. There is no unlicensed pay-as-you-go route. |
    | WorkIQ API used by a custom application or agent | Consumption billing through Copilot Credits; this is separate from Retrieval and Search API pricing. |

    The meter counts API requests, not end-user prompts. One user action can therefore produce several
    billable calls if the backend fans out, retries, or invokes retrieval repeatedly. These prices also
    exclude the application's own model inference and tokens, agent or backend hosting, storage,
    networking, and observability.

For example, standard Graph search can find mail, Teams messages, or documents containing `Project
Atlas` and relevance-rank those matches. If an item only discusses "the migration cutover and
residency risk," conceptual matching is not a documented guarantee of `POST /search/query`. For
SharePoint or OneDrive files, the application can instead call Copilot Retrieval. For mail, Teams,
events, and a final answer spanning workloads, it must still expand terms, classify candidates, and
orchestrate the sources itself, or delegate that intelligence work to WorkIQ.

The key distinction is therefore not **Graph is lexical, WorkIQ is semantic**. It is **direct APIs
return source-scoped hits or chunks that the application must orchestrate; WorkIQ natural-language
surfaces manage cross-workload context and synthesis**. MCP entity tools remain raw resource
operations. Semantic retrieval improves discovery, not certainty, so callers should still verify
the returned evidence.

## Where direct Graph adds work

<div class="comparison-table" markdown>

| Concern | Direct Microsoft Graph | WorkIQ |
| --- | --- | --- |
| Query planning | Select endpoints, entity types, OData or KQL, fields, and date windows. | MCP `ask`, A2A, and REST accept natural-language asks; MCP entity tools expose paths for direct control. |
| Topic discovery | Standard Search matches free text or KQL and applies entity-specific ranking. Copilot Retrieval adds semantic/hybrid chunks for SharePoint, OneDrive, and connectors. | Natural-language surfaces interpret the topic and use available lexical, semantic, and organizational context across supported sources. |
| Cross-workload retrieval | Select the appropriate resource, Search, or Copilot Retrieval API per source, then normalize, deduplicate, rank, and combine the outputs. | WorkIQ assembles permission-trimmed work context across supported sources. |
| Caller-model context tokens | Raw records, content, and metadata selected for synthesis become input tokens; cross-workload fan-out makes the load high and variable. | MCP `ask`, A2A, and REST keep retrieval material inside WorkIQ, so caller context consists mainly of the ask and synthesized output. MCP entity tools return raw data and therefore behave like direct Graph when their results enter an outer model. |
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

!!! info "WorkIQ API price examples"
  This section prices calls made by a custom application, agent, or harness. Those WorkIQ API
  calls use Copilot Credits even when the represented user has Microsoft 365 E7. Native WorkIQ
  use inside Microsoft 365 Copilot is included in E7 and has no incremental WorkIQ charge.

  The published pay-as-you-go price is **$0.01 per Copilot Credit**. The WorkIQ Tools API uses
  **0.1 credit per explicit API call ($0.001)**. WorkIQ Chat and Context consumption, including
  MCP `ask`, REST, and A2A, is variable. Microsoft does not publish a fixed per-query credit rate,
  so the examples below use planning bands rather than a rate-card guarantee:

  | Planning band | Credits per query | Cost per query | Cost per 1,000 queries |
  | --- | ---: | ---: | ---: |
  | Light | 20-40 | **$0.20-$0.40** | **$200-$400** |
  | Medium | 30-75 | **$0.30-$0.75** | **$300-$750** |
  | Heavy | 50-150 | **$0.50-$1.50** | **$500-$1,500** |

  Actual credits depend on models, runtime, retrieved context, reasoning, and tools. These figures
  exclude the caller's own model, hosting, telemetry services, and any separately invoked WorkIQ
  Tool API calls.

<div class="comparison-table comparison-table--wide" markdown>

| Ask | Direct Graph implementation | WorkIQ route | WorkIQ planning cost | Relative effort |
| --- | --- | --- | ---: | --- |
| "What meetings do I have today?" | Query `calendarView`, handle time zones, recurrence, fields, and paging. | Call MCP `ask`, submit one REST turn, or send an A2A message with required location metadata. | **Light: $0.20-$0.40 per query.** | **Low / low.** Prefer Graph for structured events; WorkIQ for a prose answer. |
| "Brief me for my Contoso call." | Search mail, Teams, files, and events with separate scopes and requests; fetch details; merge, rank, and summarize. | Submit the ask through MCP `ask`, REST chat, or A2A according to the caller contract. | **Medium: $0.30-$0.75 per query.** | **High / low-medium.** |
| "Find everything related to Project Atlas, including items that never use that name." | Search mail, Teams, and events with source-specific queries; use Copilot Retrieval for eligible SharePoint, OneDrive, or connector content; then classify and synthesize across outputs. | Submit the cross-workload topic ask through MCP `ask`, REST, or A2A and verify the grounded evidence. | **Medium-heavy: $0.30-$1.50 per query.** | **High / low-medium.** |
| "Summarize project risks and correlate them with incident telemetry." | Build Microsoft 365 retrieval, an external telemetry integration, and a model/tool loop. | Give an outer agent WorkIQ MCP and telemetry tools. | **Medium-heavy: $0.30-$1.50 for the WorkIQ query; external telemetry and model costs are additional.** | **High / medium.** |
| "Investigate the regression; let me cancel and reconnect later." | Add retrieval and synthesis plus a job queue, state store, status API, cancellation, and artifact persistence. | Send an A2A task; persist `task.id` and `contextId`; get, subscribe, or cancel while retained. | **Heavy baseline: $0.50-$1.50+; long-running or multi-turn work can cost more.** | **Very high / medium.** |
| "Create this exact approved calendar event." | Call the calendar endpoint with a narrow schema and explicit authorization. | Use an approval-gated MCP `create_entity` call. | **Tool API: $0.001 per explicit call; approval and outer-model costs are additional.** | **Low / medium.** Graph is usually the cleaner contract. |

</div>

The briefing and cross-workload topic rows are the important Graph-versus-WorkIQ dividing line, not
a protocol boundary. The
[Microsoft Search API](https://learn.microsoft.com/graph/api/resources/search-api-overview?view=graph-rest-1.0)
provides permission-trimmed hits, and Copilot Retrieval provides relevant chunks for its supported
sources. Mail, events, Teams messages, files, and connectors still have different scopes, result
shapes, paging limits, and supported combinations. Neither surface performs the final cross-source
synthesis.

## Production implications

- Graph clients must always account for paging and throttling; Microsoft documents `@odata.nextLink`,
  `Retry-After`, and separate retry handling for throttled batch members.
- A locally maintained Graph corpus also needs change notifications and delta queries, including
  token expiry and resynchronization behavior.
- WorkIQ reduces that retrieval and synthesis surface, but it is delegated-only, usage billed, and
  AI-generated output still requires verification. The WorkIQ REST surface has no writes or
  long-running task contract; A2A supplies the task lifecycle.
- Compare caller-model input tokens separately from WorkIQ service usage. Reducing outer context does
  not mean WorkIQ performs no internal retrieval, reasoning, or billable processing.
- Both approaches enforce the signed-in user's access. WorkIQ does not grant access to content the
  user cannot already reach.

## Microsoft Learn references

- [Work IQ API overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/api-overview)
- [Work IQ API general availability and pricing](https://www.microsoft.com/en-us/licensing/news/work-iq-general-availability)
- [Microsoft Copilot Credits Guide](https://go.microsoft.com/fwlink/?linkid=2368800)
- [Copilot Credits usage-based billing](https://learn.microsoft.com/microsoft-365/copilot/usage-based-billing-overview-copilot-credits)
- [Work IQ overview - Context](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/#context)
- [Work IQ MCP overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/mcp/overview)
- [Work IQ A2A overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/a2a/overview)
- [Work IQ REST overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/rest/overview)
- [Microsoft Search API query guidance](https://learn.microsoft.com/graph/api/resources/search-api-overview?view=graph-rest-1.0)
- [Microsoft Search API for Outlook messages](https://learn.microsoft.com/graph/search-concept-messages)
- [Microsoft Search API for Teams messages](https://learn.microsoft.com/graph/search-concept-chat-messages)
- [Microsoft Search API for OneDrive and SharePoint](https://learn.microsoft.com/graph/search-concept-files)
- [Microsoft 365 Copilot Retrieval API](https://learn.microsoft.com/microsoft-365/copilot/extensibility/api/ai-services/retrieval/overview)
- [Copilot Retrieval API pay-as-you-go pricing](https://learn.microsoft.com/microsoft-365/copilot/extensibility/api/ai-services/retrieval/paygo-retrieval)
- [Microsoft 365 Copilot Search API (preview)](https://learn.microsoft.com/microsoft-365/copilot/extensibility/api/ai-services/search/overview)
- [Semantic indexing for Microsoft Copilot](https://learn.microsoft.com/microsoftsearch/semantic-index-for-copilot)
- [Microsoft Graph best practices](https://learn.microsoft.com/graph/best-practices-concept)
- [Microsoft Graph delta query](https://learn.microsoft.com/graph/delta-query-overview)