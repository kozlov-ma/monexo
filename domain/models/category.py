from __future__ import annotations

import typing
from dataclasses import dataclass, replace

from sqlalchemy import Float, Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.models.db_base import Base


@dataclass(frozen=True)
class Category:
    id: int

    user_id: int
    name: str


class DbCategory(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_telegram_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    name: Mapped[str] = mapped_column(String)

    def to_category(self) -> Category:
        return Category(self.id, self.user_telegram_id, self.name)

    @staticmethod
    def from_category(category: Category) -> DbCategory:
        return DbCategory(id=category.id, user_telegram_id=category.user_id, name=category.name)

    def __repr__(self):
        return \
            f'<Category id={self.id} user_id={self.user_telegram_id} name={self.name}>'
