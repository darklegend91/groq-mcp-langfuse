# Groq + FastAPI + FastMCP

A small example service that connects Groq models to tools exposed through [FastMCP](https://gofastmcp.com/). It includes a FastAPI HTTP API, an in-process agent, and an MCP endpoint that can be used by Groq's remote MCP integration.

## What it includes

- `POST /ask/local`: asks Groq a question and lets the model call MCP tools over an in-memory FastMCP client.
- `POST /ask/remote`: asks Groq to use a publicly reachable MCP server through the OpenAI-compatible Responses API.
- `GET /health`: a simple health check.
- MCP tools at `/mcp-server/mcp`:
  - `add(a, b)`: adds two integers.
  - `get_weather(city)`: returns sample weather text (not a live forecast).
- Optional Langfuse tracing for the local and remote ask flows.

Configure tracing keys in the [Langfuse dashboard](https://cloud.langfuse.com/project/cmvkrb27q06hmad0j410q4i95).

## Requirements

- Python 3.10 or newer
- A Groq API key for the ask endpoints
- A public HTTPS deployment of the MCP endpoint to use `/ask/remote`

## Set up

```bash
git clone <repository-url>
cd groq-fastmcp-fastapi
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Set `GROQ_API_KEY` in `.env`. You can also change `GROQ_MODEL`; the default is `openai/gpt-oss-120b`.

## Run the API

From the project root, start the development server:

```bash
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

Check that the service is running:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"ok":true}
```

## Ask a question

The local route connects to the MCP tools in the same process, so it works without a public MCP deployment:

```bash
curl -X POST http://127.0.0.1:8000/ask/local \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is 17 + 25?"}'
```

You can also run the local agent directly from the project root:

```bash
python -m scripts.run_local_agent "What is 17 + 25?"
```

The remote route uses Groq's Responses API with a remote MCP tool. Deploy the app first, then set `MCP_PUBLIC_URL` in `.env` to the publicly accessible MCP URL, including the `/mcp-server/mcp` path. For example, if your app is hosted at `https://example.com`, use:

```dotenv
MCP_PUBLIC_URL=https://example.com/mcp-server/mcp
```

Then call the remote route:

```bash
curl -X POST http://127.0.0.1:8000/ask/remote \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is the weather in Paris?"}'
```

The remote route requires both `GROQ_API_KEY` and `MCP_PUBLIC_URL`. The MCP server must be reachable over public HTTPS by Groq.

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | For ask endpoints | API key used to call Groq. |
| `GROQ_MODEL` | No | Groq model name; defaults to `openai/gpt-oss-120b`. |
| `MCP_PUBLIC_URL` | For `/ask/remote` | Public HTTPS URL for the MCP endpoint, usually ending in `/mcp-server/mcp`. |
| `LANGFUSE_PUBLIC_KEY` | No | Langfuse public key for tracing. |
| `LANGFUSE_SECRET_KEY` | No | Langfuse secret key for tracing. |
| `LANGFUSE_BASE_URL` | No | Langfuse host; defaults to `https://cloud.langfuse.com`. |

Keep secrets in `.env`; do not commit that file. `.env.example` contains placeholders for local setup.

## Run the tests

```bash
pytest
```
