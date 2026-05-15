"""BaseAgent: wraps an MCP stdio server + Anthropic tool-use loop."""
import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

MODEL = "claude-sonnet-4-6"
MCP_DIR = Path(__file__).parent.parent / "mcp_servers"


def _mcp_tool_to_anthropic(tool) -> dict:
    """Convert an MCP tool definition to the Anthropic tools format."""
    schema = tool.inputSchema if tool.inputSchema else {"type": "object", "properties": {}}
    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": schema,
    }


class BaseAgent:
    def __init__(self, mcp_server_filename: str, system_prompt: str):
        self.server_path = str(MCP_DIR / mcp_server_filename)
        self.system_prompt = system_prompt
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    async def run(self, user_message: str) -> str:
        """Run the agent: connect to MCP, gather tools, execute the Anthropic tool-use loop."""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_path],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools_response = await session.list_tools()
                anthropic_tools = [_mcp_tool_to_anthropic(t) for t in tools_response.tools]

                messages = [{"role": "user", "content": user_message}]

                system = [
                    {
                        "type": "text",
                        "text": self.system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ]

                while True:
                    response = self.client.messages.create(
                        model=MODEL,
                        max_tokens=4096,
                        system=system,
                        tools=anthropic_tools,
                        messages=messages,
                    )

                    if response.stop_reason == "end_turn":
                        for block in response.content:
                            if hasattr(block, "text"):
                                return block.text
                        return ""

                    if response.stop_reason == "tool_use":
                        messages.append({"role": "assistant", "content": response.content})

                        tool_results = []
                        for block in response.content:
                            if block.type == "tool_use":
                                try:
                                    result = await session.call_tool(block.name, block.input)
                                    content = result.content[0].text if result.content else ""
                                except Exception as exc:
                                    content = json.dumps({"error": str(exc)})

                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": content,
                                })

                        messages.append({"role": "user", "content": tool_results})
                    else:
                        break

        return ""
