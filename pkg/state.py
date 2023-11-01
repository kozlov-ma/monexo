from dataclasses import dataclass


@dataclass
class ApplicationState:
    bot_token: str = None
    admin_usernames: list[str] = None


_state_instance: ApplicationState | None = None


def init(*args, **kwargs) -> None:
    global _state_instance
    if _state_instance is not None:
        raise RuntimeError("Tried to initialize new Application State, but it already exists.")

    _state_instance = ApplicationState(*args, **kwargs)


def get() -> ApplicationState:
    global _state_instance
    if _state_instance is None:
        raise RuntimeError("Tried to get Application State, but it was not initialized.")

    return _state_instance
