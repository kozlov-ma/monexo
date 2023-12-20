from __future__ import annotations

import typing
from dataclasses import dataclass, replace

from sqlalchemy import Float, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from domain.models.db_base import Base


@dataclass(frozen=True)
class BudgetChange:
    id: int

    user_id: int
    category_id: int
    message_id: int

    value: float
    is_income: bool


class DbBudgetChange(Base):
    __tablename__ = "budget_changes"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_telegram_id: Mapped[int] = mapped_column(Integer)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    message_telegram_id: Mapped[int] = mapped_column(Integer)

    value: Mapped[float] = mapped_column(Float)
    is_income: Mapped[bool] = mapped_column(Boolean)

    def to_budget_change(self) -> BudgetChange:
        return BudgetChange(self.id, self.user_telegram_id, self.category_id,
                            self.message_telegram_id, self.value, self.is_income)

    @staticmethod
    def from_budget_change(budget_change: BudgetChange) -> DbBudgetChange:
        return DbBudgetChange(id=budget_change.id, user_telegram_id=budget_change.user_id,
                              category_id=budget_change.category_id, message_telegram_id=budget_change.message_id,
                              value=budget_change.value, is_income=budget_change.is_income)

    def __repr__(self):
        return \
            f'<Category id={self.id} user_telegram_id={self.user_telegram_id} category_id={
            self.category_id} value={self.value} is_income={self.is_income}>'
