from abc import ABC, abstractmethod
from dataclasses import replace
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
    async def update_user_partially(self, id: int, **kwargs):
        pass

    @abstractmethod
    async def add_or_update_user(self, user: User) -> None:
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

    async def update_user_partially(self, id: int,
                                    days_left: int = None, whole_budget: float = None,
                                    expense_today: float = None, income_today: float = None):
        if id not in self.dict:
            raise KeyError(f"User with id {id} does not exist")

        kwargs = {k: v for k, v in {
            'days_left': days_left,
            'whole_budget': whole_budget,
            'expense_today': expense_today,
            'income_today': income_today
        }.items() if v is not None}

        self.dict[id] = replace(self.dict[id], **kwargs)

    async def add_or_update_user(self, user: User) -> None:
        if user.id not in self.dict:
            await self.add_user(user)
        else:
            await self.update_user(user)


UserRepository: type = InMemoryUserRepository
