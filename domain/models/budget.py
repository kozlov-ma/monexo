from abc import ABC
from dataclasses import dataclass


class BudgetChange(ABC):
    pass


@dataclass(frozen=True)
class Added(BudgetChange):
    amount: float
    new_daily_budget: float


@dataclass(frozen=True)
class Spent(BudgetChange):
    amount: float


@dataclass(frozen=True)
class SpentOverDailyBudget(BudgetChange):
    amount: float
    new_daily_budget: float
