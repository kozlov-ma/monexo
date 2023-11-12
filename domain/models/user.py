import dataclasses
import typing
from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass
class User:  # TODO переделать в неизменяемый класс
    id: UUID

    telegram_id: int
    period: date
    whole_budget: float

    expense_today: float
    income_today: float

    @property
    def budget_today(self) -> float:
        return max(self.daily_budget - self.expense_today, 0)

    @property
    def today_diff(self) -> float:
        return self.income_today - self.expense_today

    @property
    def daily_budget(self) -> float:
        return self.whole_budget / (self.period - date.today()).days

    def apply_today(self) -> typing.Self:
        """
        Applies today's income and expense to the budget.
        :return: User
        """

        return dataclasses.replace(
            self,
            whole_budget=self.whole_budget + self.today_diff,
            expense_today=0,
            income_today=0,
        )

    def add_income_today(self, amount: float) -> typing.Self:
        """
        Adds income to today's budget
        :return: User
        """

        d = self.expense_today - amount

        if self.expense_today == 0:
            return dataclasses.replace(self, income_today=self.income_today + amount)
        if d >= 0:
            return dataclasses.replace(
                self,
                expense_today=d,
            )
        if d < 0:
            return dataclasses.replace(
                self,
                expense_today=0,
                income_today=self.income_today + abs(d),
            )

    def add_income(self, amount: float) -> typing.Self:
        """
        Adds income to the whole budget
        :return: User
        """

        return dataclasses.replace(
            self,
            income_today=self.income_today + amount,
            whole_budget=self.whole_budget + amount,
        )

    def add_expense(self, amount: float) -> typing.Self:
        """
        Applies expense to today's budget, and, if expense is more than today's budget, applies it to the whole budget.
        :return: User
        """

        d = self.budget_today - amount

        if self.budget_today == 0:
            return dataclasses.replace(self, expense_today=self.expense_today + amount)
        if d >= 0:
            return dataclasses.replace(
                self,
                expense_today=self.expense_today + amount,
            )
        if d < 0:
            return dataclasses.replace(
                self,
                expense_today=self.expense_today + amount,
                whole_budget=self.whole_budget + d,
            )
