from __future__ import annotations

from typing import Any

import pytest
from langchain_core.tools import ToolException

from app.agents.tools.financial_data import categorise_expense

_fn = categorise_expense.func  # type: ignore[attr-defined]


# ─── Input validation ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "description",
    ["", "   ", "\t", "\n"],
    ids=["empty", "spaces", "tab", "newline"],
)
def test_empty_description_raises(description: str) -> None:
    with pytest.raises(ToolException, match="must not be empty"):
        _fn(description=description, amount=100.0)


def test_negative_amount_raises() -> None:
    with pytest.raises(ToolException, match="must be non-negative"):
        _fn(description="rent", amount=-1.0)


# ─── Keyword classification ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("description", "expected_category"),
    [
        ("monthly rent payment", "housing"),
        ("grocery store visit", "food"),
        ("uber ride to airport", "transport"),
        ("netflix subscription", "entertainment"),
        ("doctor visit co-pay", "healthcare"),
        ("401k contribution", "savings"),
    ],
    ids=["housing", "food", "transport", "entertainment", "healthcare", "savings"],
)
def test_keyword_classification(description: str, expected_category: str) -> None:
    result = _fn(description=description, amount=50.0)
    assert result["category"] == expected_category


def test_unknown_description_returns_other() -> None:
    result = _fn(description="random unclassified thing xyz", amount=20.0)
    assert result["category"] == "other"


# ─── Return shape ──────────────────────────────────────────────────────────────


def test_result_has_required_keys() -> None:
    result = _fn(description="rent payment", amount=1500.0)
    assert set(result.keys()) == {"category", "description", "amount"}


def test_amount_rounded_to_two_decimal_places() -> None:
    result = _fn(description="grocery run", amount=49.999)
    assert result["amount"] == pytest.approx(50.0, abs=0.001)


def test_description_is_stripped() -> None:
    result = _fn(description="  rent payment  ", amount=1000.0)
    assert result["description"] == "rent payment"


def test_zero_amount_is_valid() -> None:
    result = _fn(description="rent payment", amount=0.0)
    assert result["amount"] == 0.0


def test_category_field_is_str() -> None:
    result = _fn(description="rent payment", amount=1000.0)
    assert isinstance(result["category"], str)


def test_amount_field_is_float() -> None:
    result: dict[str, Any] = _fn(description="rent payment", amount=1000.0)
    assert isinstance(result["amount"], float)
