from __future__ import annotations
from dataclasses import dataclass
from domain.models.db_base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Boolean, ForeignKey


@dataclass
class UserTimezoneInfo:
    id: int
    timezone: int
    is_updatable: bool


class DbUserTimezoneInfo(Base):
    __tablename__ = "users_timezone_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'))
    timezone: Mapped[int] = mapped_column(Integer)
    is_updatable: bool = mapped_column(Boolean)

    def to_timezone(self) -> UserTimezoneInfo:
        return UserTimezoneInfo(self.telegram_id, self.timezone, self.is_updatable)

    @staticmethod
    def from_timezone(user_timezone: UserTimezoneInfo) -> DbUserTimezoneInfo:
        return DbUserTimezoneInfo(telegram_id=user_timezone.id, timezone=user_timezone.timezone,
                                  is_updatable=user_timezone.is_updatable)

    def __repr__(self):
        return \
            f'<User Timezone Info id={self.id} telegram_id={self.telegram_id} timezone={
                self.timezone} is_updatable={self.is_updatable}>'

