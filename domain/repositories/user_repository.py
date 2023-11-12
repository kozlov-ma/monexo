from abc import ABC, abstractmethod
from uuid import UUID
from domain.models.user import User


class UserRepositoryBase(ABC):
    @abstractmethod
    async def get_all(self) -> list[User]:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> User:
        pass

    @abstractmethod
    async def exists_id(self, id: UUID) -> bool:
        pass

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User:
        pass

    @abstractmethod
    async def exists_telegram_id(self, telegram_id: int) -> bool:
        pass

    @abstractmethod
    async def add_user(self, user: User) -> None:
        pass

    @abstractmethod
    async def remove_user_by_id(self, id: UUID) -> None:
        pass

    @abstractmethod
    async def update_user(self, user: User) -> None:
        pass


class InMemoryUserRepository(UserRepositoryBase):
    def __init__(self):
        self.dict: dict[UUID, User] = {}

    async def get_all(self) -> list[User]:
        return list(self.dict.values())

    async def get_by_id(self, id: UUID) -> User:
        if id not in self.dict:
            raise KeyError(f"User with id {id} does not exist")

        return self.dict[id]

    async def exists_id(self, id: UUID) -> bool:
        return id in self.dict

    async def get_by_telegram_id(self, telegram_id: int) -> User:
        for user in self.dict.values():
            if user.telegram_id == telegram_id:
                return user

        raise KeyError(f"User with telegram_id {telegram_id} does not exist")

    async def exists_telegram_id(self, telegram_id: int) -> bool:
        for user in self.dict.values():
            if user.telegram_id == telegram_id:
                return True

        return False

    async def add_user(self, user: User) -> None:
        if user.id in self.dict:
            raise KeyError(f"User with id {user.id} already exists")

        self.dict[user.id] = user

    async def remove_user_by_id(self, id: UUID) -> None:
        if id not in self.dict:
            raise KeyError(f"User with id {id} does not exist")

        self.dict.pop(id)

    async def update_user(self, user: User) -> None:
        if user.id not in self.dict:
            raise KeyError(f"User with id {user.id} does not exist")

        self.dict[user.id] = user


UserRepository: type = InMemoryUserRepository
