import json

from fastmcp import Client
from langfuse import observe
from langfuse.openai import AsyncOpenAI  # type: ignore

from app import config
from app.mcp_server.server import mcp

groq = AsyncOpenAI(
    api_key=config.GROQ_API_KEY or None,
    base_url='https://api.groq.com/openai/v1',
)


@observe(name='ask-local')
async def ask_local(question: str) -> str:
    # In-memory transport. Use Client('http://localhost:8000/mcp-server/mcp')
    # to go through the running HTTP endpoint instead.
    async with Client(mcp) as mcp_client:
        mcp_tools = await mcp_client.list_tools()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.input_schema,
                },
            }
            for t in mcp_tools
        ]
        messages = [{"role": "user", "content": question}]

        while True:
            resp = await groq.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=messages, # type: ignore
                tools=tools,       # type: ignore
                tool_choice="auto",
            )
            msg = resp.choices[0].message
            messages.append(msg)   # type: ignore

            if not msg.tool_calls:
                return msg.content or ""

            for call in msg.tool_calls:
                args = json.loads(call.function.arguments or "{}") # type: ignore
                result = await mcp_client.call_tool(call.function.name, args) # type: ignore
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result.content[0].text, # type: ignore
                    }
                )
