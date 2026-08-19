# MCP + Deep Agents

This is the smallest useful version of the integration implemented by this repository: start
WorkIQ as a local MCP server, adapt its discovered tools for LangChain, apply policy, and give the
approved tools to a Deep Agent.

<figure class="workiq-diagram workiq-diagram--raster">
    <img src="../assets/images/mcp-deepagents.png" width="2730" height="2188" alt="The user asks a workplace question. A Deep Agent sends an approved call through the MCP adapter and WorkIQ child to Microsoft 365. Permission-trimmed results return through the same boundaries, and the Deep Agent synthesizes the answer for the user.">
</figure>

The Python process never receives the WorkIQ bearer token. The `@microsoft/workiq` child owns its
interactive sign-in and communicates with Python through MCP messages over stdio.

## Run the example

Complete the repository [setup](https://github.com/jeffrey-groneberg/workiq-deepagents#setup), then
run the included read-only example:

```bash
uv run python examples/mcp_deepagents.py \
  "What decisions did my team make yesterday?"
```

## Core integration

```python
async def ask_workiq(question: str) -> str:
    settings = Settings()
    client = MultiServerMCPClient({"workiq": settings.workiq_connection()})

    async with client.session("workiq") as session:
        discovered_tools = await load_mcp_tools(session, server_name="workiq")
        tools = select_workiq_tools(discovered_tools, allow_writes=False)

        agent = create_deep_agent(
            model=create_model(settings),
            tools=tools,
            system_prompt=READ_ONLY_PROMPT,
            checkpointer=InMemorySaver(),
            name="workiq_example",
        )
        state = await agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            config={"configurable": {"thread_id": str(uuid4())}},
        )

    return response_text(state)
```

The MCP session encloses `agent.ainvoke`. Closing it earlier would leave the Deep Agent with tool
descriptors whose underlying stdio transport is gone.

## What each boundary owns

| Boundary | Responsibility |
| --- | --- |
| `Settings.workiq_connection()` | Describes `npx -y @microsoft/workiq mcp` as an MCP stdio server. |
| `load_mcp_tools()` | Converts discovered MCP tools into LangChain tools. |
| `select_workiq_tools()` | Removes mutation and blob tools before the model sees them. |
| `create_model()` | Creates the caller-owned Azure Responses model. |
| `create_deep_agent()` | Runs the model/tool loop and checkpoints thread state. |
| `response_text()` | Extracts display text from the final agent state. |

## Production delta

The full CLI adds streamed model and tool lifecycle events, usage and cost metrics, chat thread
reuse, prerequisite diagnostics, and explicit write enablement. For durable deployment, replace
`InMemorySaver` with a persistent checkpointer and key every thread by tenant and user.

Keep write tools disabled by default. Enabling them requires both WorkIQ tenant/path policy and an
application approval step immediately before mutation.

Sources: [Deep Agents customization](https://docs.langchain.com/oss/python/deepagents/customization),
[LangChain MCP adapters](https://github.com/langchain-ai/langchain-mcp-adapters), and the
[Work IQ MCP overview](https://learn.microsoft.com/microsoft-365/copilot/extensibility/work-iq/mcp/overview).
