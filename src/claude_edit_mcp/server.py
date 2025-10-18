"""FastMCP server for handling file editing with UTF-8 support."""

from pathlib import Path
from fastmcp import FastMCP


# Initialize FastMCP app
app = FastMCP(name="claude-edit-mcp", version="0.1.0")


@app.tool()
async def edit_file(
    file_path: str,
    old_string: str,
    new_string: str,
) -> dict:
    """
    Edit a file by replacing old_string with new_string.
    Handles UTF-8 encoding for Japanese and other multibyte characters.

    Args:
        file_path: Path to the file to edit
        old_string: String to find and replace
        new_string: Replacement string

    Returns:
        Dictionary with success status and message
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
            }

        # Read file with UTF-8 encoding
        content = path.read_text(encoding="utf-8")

        if old_string not in content:
            return {
                "success": False,
                "error": f"String not found in file: {repr(old_string)}",
            }

        # Replace the string
        new_content = content.replace(old_string, new_string, 1)

        # Write back with UTF-8 encoding and LF line endings
        path.write_text(new_content, encoding="utf-8", newline='\n')

        return {
            "success": True,
            "message": "File edited successfully",
            "file_path": str(path.resolve()),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.tool()
async def write_file(
    file_path: str,
    content: str,
) -> dict:
    """
    Write contents to a file with UTF-8 encoding.

    Args:
        file_path: Path to the file to write
        content: Content to write

    Returns:
        Dictionary with success status and message
    """
    try:
        path = Path(file_path)

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file with UTF-8 encoding and LF line endings
        path.write_text(content, encoding="utf-8", newline='\n')

        return {
            "success": True,
            "message": "File written successfully",
            "file_path": str(path.resolve()),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# @app.tool()
async def replace_line(
    file_path: str,
    start_line: int,
    end_line: int,
    new_content: str,
) -> dict:
    """
    Replace lines in a file with UTF-8 encoding.

    Args:
        file_path: Path to the file
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)
        new_content: New content to replace the lines

    Returns:
        Dictionary with success status and message
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
            }

        # Read the entire content
        content = path.read_text(encoding="utf-8")

        # Split into lines to find positions
        lines = content.splitlines(keepends=True)

        if start_line < 1 or end_line < start_line or end_line > len(lines):
            return {
                "success": False,
                "error": f"Line numbers out of range: start={start_line}, end={end_line}",
            }

        # Find the start and end positions
        start_pos = sum(len(line) for line in lines[:start_line-1])
        end_pos = sum(len(line) for line in lines[:end_line])

        # Check if the original range ends with a newline
        ends_with_newline = end_pos > 0 and content[end_pos-1] == '\n'

        # If original ends with newline, ensure new_content does too
        if ends_with_newline and not new_content.endswith('\n'):
            new_content += '\n'

        # Replace
        new_content_full = content[:start_pos] + new_content + content[end_pos:]

        path.write_text(new_content_full, encoding="utf-8", newline='\n')

        return {
            "success": True,
            "message": f"Lines {start_line} to {end_line} replaced successfully",
            "file_path": str(path.resolve()),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def run_http_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the MCP server as an HTTP server using StreamableHTTP transport.

    Uses the recommended http_app() method (streamable_http_app is deprecated).
    The server provides JSON-RPC over HTTP with automatic session management.

    Args:
        host: Host address to bind to
        port: Port number to bind to

    Server will be available at: http://{host}:{port}/mcp
    """
    import uvicorn

    # Create HTTP app using recommended method (FastMCP 2.12.5+)
    # This uses StreamableHTTP transport with automatic session management
    # For stateless mode (e.g., serverless), use: app.http_app(stateless_http=True)
    http_app = app.http_app()

    uvicorn.run(
        http_app,
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    run_http_server()
