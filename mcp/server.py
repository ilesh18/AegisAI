"""
AegisAI MCP Server — wraps key AegisAI endpoints as Model Context Protocol tools.
Copyright (C) 2024 Sarthak Doshi (github.com/SdSarthak)
SPDX-License-Identifier: AGPL-3.0-only

What is MCP?
  Model Context Protocol (MCP) lets AI assistants (editors, coding tools) call
  external services as structured tools. See https://modelcontextprotocol.io.

TODO (help wanted — scaffold):
  1. Install the MCP Python SDK: `pip install mcp`
  2. Implement three tools below:
       - `classify_ai_system`: calls POST /api/v1/classification/classify
       - `scan_prompt`: calls POST /api/v1/guard/scan
       - `query_regulations`: calls POST /api/v1/rag/query
  3. Run with: `python mcp/server.py`
  4. Configure your MCP client to connect to this server.

TODO (high priority — publish):
  - Add mcp/server.py to the docs so users know how to run it.
  - Add a mcp/requirements.txt with pinned dependencies.
  - Acceptance criteria: an MCP client can call scan_prompt("ignore all...")
    and receive a structured response with decision, confidence, and patterns.
"""

import os
import httpx

AEGISAI_BASE_URL = os.getenv("AEGISAI_BASE_URL", "http://localhost:8000")
AEGISAI_API_TOKEN = os.getenv("AEGISAI_API_TOKEN", "")

# TODO (help wanted): implement using the MCP SDK
# Example structure:
#
# from mcp.server import Server
# from mcp.server.stdio import stdio_server
# from mcp import Tool, CallToolResult, TextContent
#
# server = Server("aegisai")
#
# @server.list_tools()
# async def list_tools():
#     return [
#         Tool(
#             name="scan_prompt",
#             description="Scan a prompt for injection risks using AegisAI Guard",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "prompt": {"type": "string", "description": "The prompt to scan"}
#                 },
#                 "required": ["prompt"],
#             },
#         ),
#         Tool(
#             name="classify_ai_system",
#             description="Classify an AI system's risk level under the EU AI Act",
#             inputSchema={...},  # TODO: mirror RiskClassificationRequest schema
#         ),
#         Tool(
#             name="query_regulations",
#             description="Ask a regulatory question grounded in EU AI Act / GDPR",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "question": {"type": "string"}
#                 },
#                 "required": ["question"],
#             },
#         ),
#     ]
#
# @server.call_tool()
# async def call_tool(name: str, arguments: dict):
#     headers = {"Authorization": f"Bearer {AEGISAI_API_TOKEN}"}
#     async with httpx.AsyncClient(base_url=AEGISAI_BASE_URL) as client:
#         if name == "scan_prompt":
#             r = await client.post("/api/v1/guard/scan", json=arguments, headers=headers)
#             return CallToolResult(content=[TextContent(type="text", text=r.text)])
#         # TODO: implement classify_ai_system and query_regulations
#     raise ValueError(f"Unknown tool: {name}")
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(stdio_server(server))

if __name__ == "__main__":
    print("MCP server scaffold — implement the TODO blocks above before running.")
