"""Entry point for Claude Edit MCP server."""

import argparse
from .server import run_http_server, app


def main_stdio():
    """Entry point for stdio mode."""
    print("Starting Claude Edit MCP server in stdio mode")
    # Run the MCP server in stdio mode
    import asyncio
    asyncio.run(app.run())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Edit MCP - File editing MCP server with UTF-8 support"
    )
    parser.add_argument(
        "--mode",
        choices=["http", "stdio"],
        default="http",
        help="Server mode: http (default) or stdio",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1) - only used in http mode",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000) - only used in http mode",
    )

    args = parser.parse_args()

    if args.mode == "http":
        print(f"Starting Claude Edit MCP server on {args.host}:{args.port}")
        run_http_server(host=args.host, port=args.port)
    elif args.mode == "stdio":
        print("Starting Claude Edit MCP server in stdio mode")
        # Run the MCP server in stdio mode
        import asyncio
        asyncio.run(app.run())


if __name__ == "__main__":
    main()
