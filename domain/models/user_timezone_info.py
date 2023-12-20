from __future__ import annotations
from dataclasses import dataclass
from domain.models.db_base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Boolean, ForeignKey


@dataclass
class UserTimezoneInfo:
    user_id: int
    timezone: int
    is_updatable: bool


class DbUserTimezoneInfo(Base):
    __tablename__ = "users_timezone_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_telegram_id: Mapped[int] = mapped_column(Integer)
    timezone: Mapped[int] = mapped_column(Integer)
    is_updatable: Mapped[bool] = mapped_column(Boolean)

    def to_timezone(self) -> UserTimezoneInfo:
        return UserTimezoneInfo(self.user_telegram_id, self.timezone, self.is_updatable)

    @staticmethod
    def from_timezone(user_timezone: UserTimezoneInfo) -> DbUserTimezoneInfo:
        return DbUserTimezoneInfo(user_telegram_id=user_timezone.user_id, timezone=user_timezone.timezone,
                                  is_updatable=user_timezone.is_updatable)

    def __repr__(self):
        return \
            f'<User Timezone Info id={self.id} telegram_id={self.user_telegram_id} timezone={
                self.timezone} is_updatable={self.is_updatable}>'

