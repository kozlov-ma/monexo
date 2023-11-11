from abc import ABC, abstractmethod
from typing import Iterator
from uuid import UUID
from domain.models.user import User


class UserRepositoryBase(ABC):
    @abstractmethod
    def get_all(self) -> Iterator[User]:
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> User:
        pass

    @abstractmethod
    def get_by_telegram_id(self, telegram_id: str) -> User:
        pass

    @abstractmethod
    def add_user(self, user: User) -> None:
        pass

    @abstractmethod
    def remove_user_by_id(self, id: UUID) -> None:
        pass

    @abstractmethod
    def update_user(self, user: User) -> None:
        pass


class InMemoryUserRepository(UserRepositoryBase):
    def __init__(self):
        self.dict: dict[UUID, User] = {}

    def get_all(self) -> Iterator[User]:
        for user in self.dict.values():
            yield user

    def get_by_id(self, id: UUID) -> User:
        if id not in self.dict:
            raise KeyError

        return self.dict[id]

    def get_by_telegram_id(self, telegram_id: str) -> User:
        for user in self.dict.values():
            if user.telegram_id == telegram_id:
                return user

        raise KeyError

    def add_user(self, user: User) -> None:
        if user.id in self.dict:
            raise KeyError

        self.dict[user.id] = user

    def remove_user_by_id(self, id: UUID) -> None:
        if id not in self.dict:
            raise KeyError

        self.dict.pop(id)

    def update_user(self, user: User) -> None:
        if user.id not in self.dict:
            raise KeyError

        self.dict[user.id] = user


UserRepository: type = InMemoryUserRepository
