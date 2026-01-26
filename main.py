"""
AI Image Tools MCP Server - Nano Banana Edition
Provides image generation capabilities using Google's Gemini models:
- Gemini 3 Pro Image (nano_banana_pro) - Professional quality with 4K, Google Search, Thinking mode
AND background removal using Freepik API
"""

import sys
import os
import logging
import warnings

# CRITICAL: Windows binary mode for proper JSON-RPC over stdio
# Fixes "invalid trailing data at the end of stream" error in Antigravity/MCP
if sys.platform == "win32":
    import msvcrt
    # Set stdin and stdout to binary mode to prevent CRLF translation
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

# Enforce unbuffered output for stderr to ensure logs appear immediately
# (stdout is handled by FastMCP or kept strictly for JSON-RPC)
sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

# Suppress ALL warnings that might leak to stdout
warnings.filterwarnings("ignore")

# CRITICAL: Suppress pydantic validation warnings that pollute stdout
os.environ["PYDANTIC_ERRORS_INCLUDE_URL"] = "0"
os.environ["PYTHONWARNINGS"] = "ignore"

# Silence ALL loggers that might write anywhere
for logger_name in ["mcp", "pydantic", "httpx", "httpcore", "uvicorn", "anyio", 
                    "google", "grpc", "urllib3", "PIL", "asyncio"]:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).handlers = []

# Redirect stdout to stderr globally to prevent ANY pollution
# This ensures that library initialization logs don't break the MCP JSON-RPC stream
# We will only restore it immediately before starting the server loop
original_stdout = sys.stdout
sys.stdout = sys.stderr

try:
    from mcp.server.fastmcp import FastMCP
    from src.nano_banana_pro import nano_banana_pro
    from src.icon_generator import icon_generator
    from src.batch_icon_generator import batch_icon_generator
    from src.svg_converter import svg_converter
    from src.veo_banana import veo_banana
    from src.video_editor import video_editor
    from src.video_analyzer import video_analyzer
    from src.doc_analyzer import doc_analyzer
    from src.deep_research import deep_research
    from src.video_to_lottie import video_to_lottie

    # Initialize FastMCP server
    mcp = FastMCP("Nano Banana")

    # Register tools with MCP
    mcp.tool()(nano_banana_pro)
    mcp.tool()(icon_generator)
    mcp.tool()(batch_icon_generator)
    mcp.tool()(svg_converter)
    mcp.tool()(veo_banana)
    mcp.tool()(video_editor)
    mcp.tool()(video_analyzer)
    mcp.tool()(doc_analyzer)
    mcp.tool()(deep_research)
    mcp.tool()(video_to_lottie)

except Exception as e:
    # If imports or setup fail, we want to see the error in stderr
    print(f"Error initializing MCP server: {e}", file=sys.stderr)
    raise

if __name__ == "__main__":
    # Restore stdout ONLY when we are ready to run the server
    # This guarantees that the transport stream is clean
    sys.stdout = original_stdout
    
    # Custom runner to force LF-only line endings on Windows
    # This bypasses FastMCP's default stdio_server which uses platform default (CRLF on Windows)
    import anyio
    from mcp.server.stdio import stdio_server
    from io import TextIOWrapper

    async def run_custom_stdio():
        # Wrap stdin/stdout with explicit newline='\n' to prevent CRLF injection
        # Antigravity/MCP is extremely strict about trailing \r characters
        stdin_wrapper = TextIOWrapper(sys.stdin.buffer, encoding="utf-8", newline="\n")
        stdout_wrapper = TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
        
        async_stdin = anyio.wrap_file(stdin_wrapper)
        async_stdout = anyio.wrap_file(stdout_wrapper)

        async with stdio_server(stdin=async_stdin, stdout=async_stdout) as (read_stream, write_stream):
            await mcp._mcp_server.run(
                read_stream,
                write_stream,
                mcp._mcp_server.create_initialization_options(),
            )

    try:
        anyio.run(run_custom_stdio)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        sys.stderr.write(f"Fatal error in MCP server: {e}\n")
