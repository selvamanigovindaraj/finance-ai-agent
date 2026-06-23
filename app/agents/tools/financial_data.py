from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import yfinance as yf
from langchain_core.tools import ToolException, tool


@tool
def get_quote(ticker: str) -> dict[str, Any]:
    """Fetch the latest quote for a stock ticker."""
    if not isinstance(ticker, str):
        raise ToolException("Ticker symbol must be a string.")
    symbol = ticker.strip().upper()
    if not symbol:
        raise ToolException("Ticker symbol must be a non-empty string.")

    try:
        stock = yf.Ticker(symbol)
        info: dict[str, Any] = stock.info or {}

        market_price = info.get("regularMarketPrice")
        price = market_price if market_price is not None else info.get("previousClose")
        currency = info.get("currency") or "USD"
        timestamp = info.get("regularMarketTime")

        if price is None:
            raise ToolException(f'Unable to fetch a live price for ticker "{symbol}".')

        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(int(timestamp), UTC).isoformat()
        elif isinstance(timestamp, datetime):
            timestamp = timestamp.astimezone(UTC).isoformat()
        else:
            timestamp = datetime.now(UTC).isoformat()

        return {
            "ticker": symbol,
            "price": float(price),
            "currency": currency,
            "timestamp": timestamp,
        }
    except ToolException:
        raise
    except Exception as exc:
        raise ToolException(f'Failed to fetch quote for ticker "{symbol}": {exc}') from exc


@tool
def get_financial_statements(ticker: str, period: str = "annual") -> dict[str, Any]:
    """Retrieve income statement, balance sheet, and cash flow data."""
    raise ToolException("get_financial_statements is not yet implemented.")


@tool
def get_market_news(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Fetch recent market news articles matching the query."""
    raise ToolException("get_market_news is not yet implemented.")


@tool
def budget_calc(income: float, expenses: dict[str, float]) -> dict[str, Any]:
    """Compute monthly surplus, savings rate, and per-category expense breakdown."""
    if income <= 0:
        raise ToolException("Income must be a positive number.")
    if not expenses:
        raise ToolException("Expenses dict must not be empty.")

    total_expenses = sum(expenses.values())
    monthly_surplus = income - total_expenses
    savings_rate_pct = round((monthly_surplus / income) * 100, 2)

    breakdown: dict[str, dict[str, float]] = {
        category: {
            "amount": round(amount, 2),
            "pct_of_income": round((amount / income) * 100, 2),
        }
        for category, amount in expenses.items()
    }

    return {
        "monthly_surplus": round(monthly_surplus, 2),
        "savings_rate_pct": savings_rate_pct,
        "breakdown": breakdown,
    }
