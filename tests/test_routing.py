from __future__ import annotations

import pytest

from app.agents.adaptive_router import run_agent


@pytest.mark.skip(reason="not yet implemented")
async def test_routes_stock_query_to_financial_data() -> None:
    """A query about a stock price should route to financial_data."""
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
async def test_routes_recent_news_to_web_search() -> None:
    """A query about recent news should route to web_search."""
    raise NotImplementedError


@pytest.mark.skip(reason="not yet implemented")
async def test_routes_knowledge_base_query_to_vector_search() -> None:
    """A question about indexed documents should route to vector_search."""
    raise NotImplementedError


# keep the import exercised so the module appears in coverage
__all__ = ["run_agent"]
