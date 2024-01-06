from abc import ABC
from dataclasses import dataclass


class BudgetChange(ABC):
    pass


@dataclass(frozen=True)
class Added(BudgetChange):
    amount: float
    new_budget_today: float


@dataclass(frozen=True)
class Spent(BudgetChange):
    amount: float
    new_budget_today: float


@dataclass(frozen=True)
class SpentOverDailyBudget(BudgetChange):
    amount: float
    new_daily_budget: float


@dataclass(frozen=True)
class SpentAllBudget(BudgetChange):
    amount: float


@dataclass(frozen=True)
class DayResults(BudgetChange):
    income: float
    expense: float
    saved: float
    new_remaining_budget: float
    new_daily_budget: float
    new_days_left: int


@dataclass(frozen=True)
class PeriodEnded(DayResults):
    income: float
    expense: float
    saved: float
