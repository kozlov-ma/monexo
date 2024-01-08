import dataclasses
import enum
from dataclasses import dataclass
from functools import cache

from app.telemetry import TelemetryData
from domain.models.user import User
from domain.repositories.budget_change_repository import BudgetChangeRepositoryBase
from domain.repositories.user_repository import UserRepositoryBase
from domain.repositories.user_timezone_info_repository import UserTimezoneInfoRepositoryBase


class SettingsConversationState(enum.Enum):
    STARTED = enum.auto()
    WAIT_FOR_SUM = enum.auto()
    WAIT_FOR_DATE = enum.auto()
    ENDED = enum.auto()  # TODO костыль -- нужно исправить


@dataclass
class ApplicationState:
    admin_usernames: list[str] = None
    users_repo: UserRepositoryBase = None
    bc_repo: BudgetChangeRepositoryBase = None
    tz_repo: UserTimezoneInfoRepositoryBase = None
    telemetry: TelemetryData = dataclasses.field(default_factory=TelemetryData)


_state_instance: ApplicationState | None = None


def init(*args, **kwargs) -> None:
    global _state_instance
    if _state_instance is not None:
        raise RuntimeError(
            "Tried to initialize new Application State, but it already exists."
        )

    _state_instance = ApplicationState(*args, **kwargs)


def get() -> ApplicationState:
    global _state_instance
    if _state_instance is None:
        raise RuntimeError(
            "Tried to get Application State, but it was not initialized."
        )

    return _state_instance
