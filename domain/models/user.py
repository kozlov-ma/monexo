from __future__ import annotations

import typing
from dataclasses import dataclass, replace

from sqlalchemy import Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from domain.models.db_base import Base


@dataclass(frozen=True)
class User:
    id: int

    days_left: int

    remaining_budget: float = 0
    budget_today: float = 0

    expense_today: float = 0
    income_today: float = 0


class DbUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer)

    days_left: Mapped[int] = mapped_column(Integer)

    remaining_budget: Mapped[float] = mapped_column(Float)
    budget_today: Mapped[float] = mapped_column(Float)

    expense_today: Mapped[float] = mapped_column(Float)
    income_today: Mapped[float] = mapped_column(Float)

    def to_user(self) -> User:
        return User(self.telegram_id, self.days_left, self.remaining_budget, self.budget_today, self.expense_today,
                    self.income_today)

    @staticmethod
    def from_user(user: User) -> DbUser:
        return DbUser(telegram_id=user.id, days_left=user.days_left, remaining_budget=user.remaining_budget,
                      budget_today=user.budget_today, expense_today=user.expense_today, income_today=user.income_today)

    def __repr__(self):
        return \
            f'<User id={self.id} telegram_id={self.telegram_id} remaining_budget={self.remaining_budget} budget_today={
                self.budget_today} expense_today={self.expense_today} income_today={self.income_today}>'
