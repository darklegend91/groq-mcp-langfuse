from app import config
from langfuse import observe


@observe(name='ask-remote')
def ask_remote(question: str) -> str:
    # Import lazily so the API and health endpoint can start when the optional
    # remote integration is not configured.
    from langfuse.openai import OpenAI

    if not config.GROQ_API_KEY:
        raise RuntimeError('GROQ_API_KEY is required for the remote endpoint')
    if not config.MCP_PUBLIC_URL:
        raise RuntimeError('MCP_PUBLIC_URL is required for the remote endpoint')

    client = OpenAI(
        api_key=config.GROQ_API_KEY,
        base_url='https://api.groq.com/openai/v1',
    )
    resp = client.responses.create(
        model=config.GROQ_MODEL,
        input=question,
        tools=[{
            'type': 'mcp',
            'server_label': 'my_tools',
            'server_url': config.MCP_PUBLIC_URL,
            'require_approval': 'never',
            # 'allowed_tools': ['add', 'get_weather'],
            # 'headers': {'Authorization': 'Bearer <token>'},
        }],
    )
    return resp.output_text
