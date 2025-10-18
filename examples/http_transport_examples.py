"""
FastMCP 2.12.5 - HTTP Transport Examples

This file demonstrates the recommended ways to implement JSON-RPC over HTTP
using FastMCP 2.12.5.
"""

from fastmcp import FastMCP
import uvicorn


# ============================================================================
# Example 1: Basic HTTP Server (Recommended for most use cases)
# ============================================================================
# This is the simplest and recommended approach for most applications.
# Uses the default "streamable-http" transport with session management.

def example_1_basic_http():
    """
    Recommended: Basic HTTP server with automatic session management.

    - Uses `http_app()` method (streamable_http_app is deprecated)
    - Provides full bidirectional communication
    - Automatically handles session management
    - Default endpoint: /mcp
    """
    app = FastMCP(name="example-basic-http")

    @app.tool()
    async def greet(name: str) -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    # Create HTTP app using recommended method
    # This creates a Starlette ASGI app with StreamableHTTP transport
    http_app = app.http_app()

    # Run with uvicorn
    uvicorn.run(http_app, host="127.0.0.1", port=8000)
    # Server will be available at http://127.0.0.1:8000/mcp


# ============================================================================
# Example 2: Stateless HTTP Server (For serverless/load-balanced environments)
# ============================================================================
# Use this when you need true stateless operation without session persistence.

def example_2_stateless_http():
    """
    Stateless HTTP server for serverless/load-balanced environments.

    - No session persistence between requests
    - Each request creates a new transport
    - Ideal for AWS Lambda, Google Cloud Functions, etc.
    - Session ID is still used for request correlation
    """
    app = FastMCP(name="example-stateless-http")

    @app.tool()
    async def greet(name: str) -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    # Create stateless HTTP app
    http_app = app.http_app(stateless_http=True)

    # Run with uvicorn
    uvicorn.run(http_app, host="127.0.0.1", port=8000)


# ============================================================================
# Example 3: Custom Path Configuration
# ============================================================================
# Customize the endpoint path for the MCP server.

def example_3_custom_path():
    """
    HTTP server with custom endpoint path.

    - Default path is /mcp
    - Can be customized for integration with existing apps
    """
    app = FastMCP(name="example-custom-path")

    @app.tool()
    async def greet(name: str) -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    # Create HTTP app with custom path
    http_app = app.http_app(path="/api/mcp")

    # Run with uvicorn
    uvicorn.run(http_app, host="127.0.0.1", port=8000)
    # Server will be available at http://127.0.0.1:8000/api/mcp


# ============================================================================
# Example 4: Using run() method (Easiest for development)
# ============================================================================
# The simplest way to run a server for development/testing.

def example_4_using_run_method():
    """
    Using the run() method for quick development.

    - Simplest approach
    - Good for development and testing
    - Automatically configures uvicorn
    """
    app = FastMCP(name="example-run-method")

    @app.tool()
    async def greet(name: str) -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    # Run directly with default settings
    # This is equivalent to creating http_app() and running with uvicorn
    app.run(
        transport="http",  # or "streamable-http" (same thing)
        host="127.0.0.1",
        port=8000,
    )


# ============================================================================
# Example 5: Environment Variable Configuration
# ============================================================================
# Configure server using environment variables.

def example_5_env_config():
    """
    Configure server using environment variables.

    Environment variables:
    - FASTMCP_HOST=127.0.0.1
    - FASTMCP_PORT=8000
    - FASTMCP_STREAMABLE_HTTP_PATH=/mcp
    - FASTMCP_STATELESS_HTTP=false
    - FASTMCP_JSON_RESPONSE=false
    """
    import fastmcp

    # These settings are read from environment variables
    print(f"Host: {fastmcp.settings.host}")
    print(f"Port: {fastmcp.settings.port}")
    print(f"Path: {fastmcp.settings.streamable_http_path}")
    print(f"Stateless: {fastmcp.settings.stateless_http}")

    app = FastMCP(name="example-env-config")

    @app.tool()
    async def greet(name: str) -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    # Run with settings from environment
    app.run(transport="http")


# ============================================================================
# Example 6: Integration with existing Starlette/FastAPI app
# ============================================================================
# Mount FastMCP server into existing web application.

def example_6_fastapi_integration():
    """
    Integrate FastMCP with existing FastAPI/Starlette application.

    - Mount MCP server as a sub-application
    - Keep existing routes and middleware
    - Useful for adding MCP to existing services
    """
    from fastapi import FastAPI
    from starlette.middleware.cors import CORSMiddleware

    # Create FastAPI app
    fastapi_app = FastAPI(title="My API")

    @fastapi_app.get("/")
    async def root():
        return {"message": "Hello from FastAPI"}

    # Create MCP server
    mcp = FastMCP(name="example-integration")

    @mcp.tool()
    async def greet(name: str) -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    # Create MCP HTTP app
    mcp_app = mcp.http_app(path="/mcp")

    # Mount MCP app into FastAPI
    # IMPORTANT: Must use the lifespan from mcp_app
    fastapi_app.mount("/api", mcp_app)

    # Add CORS middleware if needed
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Run FastAPI app
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
    # MCP server available at http://127.0.0.1:8000/api/mcp


# ============================================================================
# Key Differences: http_app() vs streamable_http_app()
# ============================================================================

"""
IMPORTANT: As of FastMCP 2.12.5

1. streamable_http_app() is DEPRECATED (since 2.3.2)
   - Still works but shows deprecation warning
   - Will be removed in future version
   - Use http_app() instead

2. http_app() is RECOMMENDED
   - This is the modern, recommended method
   - Supports both stateful and stateless modes
   - Provides full StreamableHTTP transport functionality

3. Default Behavior
   - By default, http_app() uses stateful mode (stateless_http=False)
   - Session management is handled automatically
   - Sessions are identified by Mcp-Session-Id header

4. Stateless Mode (stateless_http=True)
   - No session persistence between requests
   - Each request creates fresh transport
   - Better for serverless/load-balanced deployments
   - Still uses session ID for request correlation

5. Session Management
   - In stateful mode: Sessions are managed by StreamableHTTPSessionManager
   - In stateless mode: No session state is persisted
   - Session ID header is always respected (Mcp-Session-Id)
"""


# ============================================================================
# Complete Working Example
# ============================================================================

if __name__ == "__main__":
    """
    Run a complete working example with all features.
    """
    import sys

    # Create MCP server
    app = FastMCP(
        name="claude-edit-mcp-http",
        version="0.1.0",
        instructions="A file editing server accessible over HTTP"
    )

    @app.tool()
    async def edit_file(file_path: str, old_text: str, new_text: str) -> dict:
        """
        Edit a file by replacing old_text with new_text.

        Args:
            file_path: Path to the file
            old_text: Text to find
            new_text: Text to replace with

        Returns:
            Success status and message
        """
        from pathlib import Path

        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": "File not found"}

            content = path.read_text(encoding="utf-8")
            if old_text not in content:
                return {"success": False, "error": "Text not found"}

            new_content = content.replace(old_text, new_text, 1)
            path.write_text(new_content, encoding="utf-8")

            return {
                "success": True,
                "message": "File edited successfully",
                "file_path": str(path.resolve())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.tool()
    async def read_file(file_path: str) -> dict:
        """
        Read a file's contents.

        Args:
            file_path: Path to the file

        Returns:
            File contents and metadata
        """
        from pathlib import Path

        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": "File not found"}

            content = path.read_text(encoding="utf-8")
            return {
                "success": True,
                "content": content,
                "file_path": str(path.resolve())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Choose example to run
    example = sys.argv[1] if len(sys.argv) > 1 else "basic"

    if example == "basic":
        print("Running Example 1: Basic HTTP Server")
        print("Server will start at http://127.0.0.1:8000/mcp")
        http_app = app.http_app()
        uvicorn.run(http_app, host="127.0.0.1", port=8000)

    elif example == "stateless":
        print("Running Example 2: Stateless HTTP Server")
        print("Server will start at http://127.0.0.1:8000/mcp")
        http_app = app.http_app(stateless_http=True)
        uvicorn.run(http_app, host="127.0.0.1", port=8000)

    elif example == "run":
        print("Running Example 4: Using run() method")
        print("Server will start at http://127.0.0.1:8000/mcp")
        app.run(transport="http", host="127.0.0.1", port=8000)

    else:
        print("Available examples: basic, stateless, run")
        print("Usage: python http_transport_examples.py [example]")
