import dataclasses
import enum
from dataclasses import dataclass
from functools import cache

from domain.models.user import User
from domain.repositories.user_repository import UserRepositoryBase


class SettingsConversationState(enum.Enum):
    WAIT_FOR_SUM = enum.auto()
    WAIT_FOR_DATE = enum.auto()


@dataclass
class ApplicationState:
    admin_usernames: list[str] = None
    users_repo: UserRepositoryBase = None
    conversation_states: dict[int, SettingsConversationState] = None


_state_instance: ApplicationState | None = None


def init(*args, **kwargs) -> None:
    global _state_instance
    if _state_instance is not None:
        raise RuntimeError(
            "Tried to initialize new Application State, but it already exists."
        )

    _state_instance = ApplicationState(*args, **kwargs, conversation_states={})


def get() -> ApplicationState:
    global _state_instance
    if _state_instance is None:
        raise RuntimeError(
            "Tried to get Application State, but it was not initialized."
        )

    return _state_instance
