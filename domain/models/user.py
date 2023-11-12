import dataclasses
import typing
from dataclasses import dataclass
from uuid import UUID
from datetime import date


@dataclass
class User:  # TODO переделать в неизменяемый класс
    id: UUID

    telegram_id: int
    period: date
    budget: float

    expense_today: float
    income_today: float

    @property
    def budget_today(self) -> float:
        return self.daily_budget - self.expense_today

    @property
    def today_diff(self) -> float:
        return self.income_today - self.expense_today

    @property
    def daily_budget(self) -> float:
        return self.budget / (self.period - date.today()).days

    def apply_today(self) -> typing.Self:
        pass
