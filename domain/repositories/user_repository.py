from abc import ABC, abstractmethod

from domain.models.user import User


class UserRepositoryBase(ABC):
    @abstractmethod
    async def get_all(self) -> list[User]:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> User:
        """
        Возвращает пользователя по его id
        :param id: id пользователя в telegram
        :return: возвращает User, если пользователя с таким id нет, возвращает None
        """
        pass

    @abstractmethod
    async def add_user(self, user: User) -> None:
        pass

    @abstractmethod
    async def remove_user_by_id(self, id: int) -> None:
        pass

    @abstractmethod
    async def update_user(self, user: User) -> None:
        pass

    @abstractmethod
    async def insert_user(self, user: User) -> None:
        pass


class InMemoryUserRepository(UserRepositoryBase):
    def __init__(self):
        self.dict: dict[int, User] = {}

    async def get_all(self) -> list[User]:
        return list(self.dict.values())

    async def get_by_id(self, id: int) -> User | None:
        if id in self.dict:
            return self.dict[id]

        return None

    async def add_user(self, user: User) -> None:
        if user.id in self.dict:
            raise KeyError(f"User with id {user.id} already exists")

        self.dict[user.id] = user

    async def remove_user_by_id(self, id: int) -> None:
        if id not in self.dict:
            raise KeyError(f"User with id {id} does not exist")

        self.dict.pop(id)

    async def update_user(self, user: User) -> None:
        if user.id not in self.dict:
            raise KeyError(f"User with id {user.id} does not exist")

        self.dict[user.id] = user

    async def insert_user(self, user: User) -> None:
        self.dict[user.id] = user


UserRepository: type = InMemoryUserRepository
