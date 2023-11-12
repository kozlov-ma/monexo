from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import date


@dataclass(frozen=True)
class User:
    id: int
    period: date
    whole_budget: float
    expense_today: float
    income_today: float

    @property
    def daily_budget(self) -> float:
        return self.whole_budget / (self.period - date.today()).days

    @property
    def budget_today(self) -> float:
        return max(self.daily_budget - self.expense_today, 0)

    @property
    def today_diff(self) -> float:
        return self.income_today - self.expense_today

    def apply_today(self) -> User:
        """
        Applies today's income and expense to the budget.
        :return: User
        """

        return replace(
            self,
            whole_budget=self.whole_budget + self.today_diff,
            expense_today=0,
            income_today=0,
        )

    def add_income(self, amount: float) -> User:
        """
        Adds income to the whole budget
        :return: User
        """

        return replace(
            self,
            income_today=self.income_today + amount,
        )

    def add_expense(self, amount: float) -> User:
        """
        Applies expense to today's budget, and, if expense is more than today's budget, applies it to the whole budget.
        :return: User
        """

        return replace(
            self,
            expense_today=self.expense_today + amount
        )
