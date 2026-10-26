from app.mcp_server.tools.weather_tools import get_weather
from app.mcp_server.tools.math_tools import add
from fastmcp import FastMCP

mcp = FastMCP("Tools")

mcp.tool(add)
mcp.tool(get_weather)
