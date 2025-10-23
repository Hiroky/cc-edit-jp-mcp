"""FastMCP server for handling file editing with UTF-8 support."""

from pathlib import Path
from fastmcp import FastMCP
import logging
from .indent_converter import tabs_to_spaces, spaces_to_tabs


# Configure logging to output to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('claude_edit_mcp.log', encoding='utf-8')  # File output
    ]
)


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
    
    Implicitly converts indentation:
    - Input: 4 spaces are converted to tabs
    - The file content with tabs is normalized to 4 spaces for replacement
    - Output: Tabs are converted back to 4 spaces

    Args:
        file_path: Path to the file to edit
        old_string: String to find and replace (using 4 spaces for indentation)
        new_string: Replacement string (using 4 spaces for indentation)

    Returns:
        Dictionary with success status (and error message on failure)
    """
    try:
        path = Path(file_path)

        if not path.exists():
            logging.warning(f"File not found: {file_path}")
            return {
                "success": False,
                "error": f"File not found: {file_path}",
            }

        # Read file with UTF-8 encoding
        content = path.read_text(encoding="utf-8")

        # Convert tabs to spaces for search and replace
        content_normalized = tabs_to_spaces(content)

        # Log file content for debugging
        # logging.warning(f"File content (normalized): {repr(content_normalized)}")

        if old_string not in content_normalized:
            logging.warning(f"String not found in file {file_path}: {repr(old_string)}")
            return {
                "success": False,
                "error": f"String not found in file: {repr(old_string)}",
            }

        # Replace the string in normalized content
        new_content_normalized = content_normalized.replace(old_string, new_string, 1)

        # Log the old string being replaced
        logging.info(f"Replacing old string: {repr(old_string)}")

        # Convert spaces back to tabs
        new_content = spaces_to_tabs(new_content_normalized)

        # Write back with UTF-8 encoding and LF line endings
        path.write_text(new_content, encoding="utf-8", newline='\n')

        return {
            "success": True,
        }
    except Exception as e:
        logging.error(f"Error editing file {file_path}: {str(e)}")
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
    
    Implicitly converts indentation:
    - Input: Content with 4 spaces for indentation
    - Output: Spaces are converted to tabs before writing

    Args:
        file_path: Path to the file to write
        content: Content to write (using 4 spaces for indentation)

    Returns:
        Dictionary with success status and message
    """
    try:
        path = Path(file_path)

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert spaces to tabs in content
        content_with_tabs = spaces_to_tabs(content)

        # Write file with UTF-8 encoding and LF line endings
        path.write_text(content_with_tabs, encoding="utf-8", newline='\n')

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


async def _read_file_impl(file_path: str, start_line: int = 1, num_lines: int = None) -> dict:
    """Read file with line range support and implicit tab-to-space conversion."""
    try:
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        total = len(lines)

        if start_line < 1 or start_line > total:
            return {"success": False, "error": f"start_line out of range: {start_line}"}
        if num_lines is not None and num_lines < 1:
            return {"success": False, "error": f"num_lines must be >= 1"}

        end = total if num_lines is None else min(start_line + num_lines - 1, total)
        content = ''.join(lines[start_line - 1:end])

        return {
            "success": True,
            "content": tabs_to_spaces(content),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.tool()
async def read_file(
    file_path: str,
    start_line: int = 1,
    num_lines: int = None,
) -> dict:
    """
    Read a file with UTF-8 encoding.
    
    Implicitly converts indentation:
    - Tabs in the file are converted to 4 spaces for readability

    Args:
        file_path: Path to the file to read
        start_line: Starting line number (1-indexed, default: 1)
        num_lines: Number of lines to read (default: None for entire file)

    Returns:
        Dictionary with file content and metadata
    """
    return await _read_file_impl(file_path, start_line, num_lines)


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
