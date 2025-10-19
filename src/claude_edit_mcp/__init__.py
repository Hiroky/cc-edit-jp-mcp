"""Claude Edit MCP - File editing MCP server with UTF-8 Japanese support."""

from .indent_converter import tabs_to_spaces, spaces_to_tabs

__version__ = "0.1.0"

__all__ = [
    "tabs_to_spaces",
    "spaces_to_tabs",
]
