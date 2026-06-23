from __future__ import annotations

from typing import Any

import pytest
from langchain_core.tools import ToolException

from app.agents.tools.financial_data import budget_calc

_fn = budget_calc.func  # type: ignore[attr-defined]


# ─── Input validation ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "income",
    [0.0, -1.0, -1000.0, -0.01],
    ids=["zero", "negative-one", "large-negative", "tiny-negative"],
)
def test_non_positive_income_raises(income: float) -> None:
    with pytest.raises(ToolException, match="Income must be a positive number"):
        _fn(income=income, expenses={"rent": 500.0})


def test_empty_expenses_raises() -> None:
    with pytest.raises(ToolException, match="must not be empty"):
        _fn(income=5000.0, expenses={})


# ─── Monthly surplus ───────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("income", "expenses", "expected_surplus"),
    [
        (5000.0, {"rent": 1500.0, "food": 500.0}, 3000.0),
        (3000.0, {"rent": 1500.0, "food": 500.0, "transport": 200.0}, 800.0),
        (2000.0, {"rent": 2500.0}, -500.0),  # overspend — valid, surplus goes negative
        (1000.0, {"misc": 1000.0}, 0.0),  # exact break-even
        (5000.0, {"rent": 1234.56, "food": 765.44}, 3000.0),  # float precision
    ],
    ids=["normal", "multi-category", "overspend", "break-even", "float-amounts"],
)
def test_monthly_surplus(
    income: float, expenses: dict[str, float], expected_surplus: float
) -> None:
    result = _fn(income=income, expenses=expenses)

    assert result["monthly_surplus"] == pytest.approx(expected_surplus, abs=0.01)


# ─── Savings rate ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("income", "expenses", "expected_rate"),
    [
        (5000.0, {"rent": 1500.0, "food": 500.0}, 60.0),  # 3000/5000
        (4000.0, {"rent": 4000.0}, 0.0),  # exact break-even → 0 %
        (3000.0, {"rent": 3500.0}, pytest.approx(-16.67, abs=0.01)),  # overspend
        (10000.0, {"misc": 1000.0}, 90.0),  # high saver
    ],
    ids=["normal", "break-even", "overspend", "high-saver"],
)
def test_savings_rate_pct(income: float, expenses: dict[str, float], expected_rate: Any) -> None:
    result = _fn(income=income, expenses=expenses)

    assert result["savings_rate_pct"] == expected_rate


# ─── Per-category breakdown ────────────────────────────────────────────────────


def test_breakdown_contains_all_categories() -> None:
    expenses = {"rent": 1500.0, "food": 400.0, "transport": 100.0}
    result = _fn(income=5000.0, expenses=expenses)

    assert set(result["breakdown"].keys()) == set(expenses.keys())


def test_breakdown_amount_matches_input() -> None:
    result = _fn(income=5000.0, expenses={"rent": 1500.0})

    assert result["breakdown"]["rent"]["amount"] == pytest.approx(1500.0)


def test_breakdown_pct_of_income_correct() -> None:
    result = _fn(income=5000.0, expenses={"rent": 1000.0})

    assert result["breakdown"]["rent"]["pct_of_income"] == pytest.approx(20.0)


def test_breakdown_pct_of_income_multiple_categories() -> None:
    result = _fn(income=4000.0, expenses={"rent": 2000.0, "food": 400.0})

    assert result["breakdown"]["rent"]["pct_of_income"] == pytest.approx(50.0)
    assert result["breakdown"]["food"]["pct_of_income"] == pytest.approx(10.0)


def test_single_category_breakdown() -> None:
    result = _fn(income=3000.0, expenses={"rent": 900.0})

    assert len(result["breakdown"]) == 1
    assert result["breakdown"]["rent"]["amount"] == pytest.approx(900.0)
    assert result["breakdown"]["rent"]["pct_of_income"] == pytest.approx(30.0)


# ─── Return shape ──────────────────────────────────────────────────────────────


def test_result_has_required_keys() -> None:
    result = _fn(income=5000.0, expenses={"rent": 1000.0})

    assert set(result.keys()) == {"monthly_surplus", "savings_rate_pct", "breakdown"}


def test_monthly_surplus_is_float() -> None:
    result = _fn(income=5000.0, expenses={"rent": 1000.0})

    assert isinstance(result["monthly_surplus"], float)


def test_savings_rate_pct_is_float() -> None:
    result = _fn(income=5000.0, expenses={"rent": 1000.0})

    assert isinstance(result["savings_rate_pct"], float)


def test_breakdown_is_dict() -> None:
    result = _fn(income=5000.0, expenses={"rent": 1000.0})

    assert isinstance(result["breakdown"], dict)
