from __future__ import annotations

from typing import Any

from langchain_core.tools import tool


@tool
def web_search(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Search the web using Tavily for up-to-date information.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.
    """
    raise NotImplementedError
