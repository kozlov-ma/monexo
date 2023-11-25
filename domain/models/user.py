from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class User:
    id: int

    days_left: int

    whole_budget: float = 0

    expense_today: float = 0
    income_today: float = 0

    @property
    def daily_budget(self) -> float:
        new_whole_budget = self.whole_budget - self.expense_today

        return new_whole_budget / self.days_left

    @property
    def budget_today(self) -> float:
        today_budget = self.whole_budget / self.days_left

        return max(today_budget - self.expense_today, 0)

    def apply_today(self) -> User:
        """
        Applies today's income and expense to the budget.
        :return: User
        """

        return replace(
            self,
            whole_budget=self.whole_budget - self.expense_today,
            expense_today=0,
            income_today=0,
            days_left=self.days_left - 1,
        )

    def add_income(self, amount: float) -> User:
        """
        Adds income to the whole budget
        :return: User
        """

        return replace(
            self,
            income_today=self.income_today + amount,
            whole_budget=self.whole_budget + amount,
        )

    def add_expense(self, amount: float) -> User:
        """
        Applies expense to today's budget, and, if expense is more than today's budget, applies it to the whole budget.
        :return: User
        """

        return replace(
            self,
            expense_today=self.expense_today + amount,
        )
