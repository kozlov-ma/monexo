from abc import ABC, abstractmethod
from dataclasses import replace
from option import Option, Result, Ok, Err
from domain.models.user import User


class UserRepositoryBase(ABC):
    @abstractmethod
    async def get_all(self) -> Option[list[User]]:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Option[User]:
        """
        Возвращает пользователя по его id
        :param id: id пользователя в telegram
        :return: возвращает User, если пользователя с таким id нет, возвращает None
        """
        pass

    @abstractmethod
    async def add_user(self, user: User) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def remove_user_by_id(self, id: int) -> Option[User]:
        pass

    @abstractmethod
    async def update_user(self, user: User) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def update_user_partially(self, id: int, **kwargs) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def add_or_update_user(self, user: User) -> Result[None, Exception]:
        pass


class InMemoryUserRepository(UserRepositoryBase):
    def __init__(self):
        self.dict: dict[int, User] = {}

    async def get_all(self) -> Option[list[User]]:
        return Option.Some(list(self.dict.values()))

    async def get_by_id(self, id: int) -> Option[User]:
        if id in self.dict:
            return Option.Some(self.dict[id])

        return Option.NONE()

    async def add_user(self, user: User) -> Result[None, Exception]:
        if user.id in self.dict:
            return Err(KeyError(f"User with id {user.id} already exists"))

        self.dict[user.id] = user
        return Ok(None)

    async def remove_user_by_id(self, id: int) -> Option[User]:
        if id not in self.dict:
            return Option.NONE()

        return Option.Some(self.dict.pop(id))

    async def update_user(self, user: User) -> Result[None, Exception]:
        if user.id not in self.dict:
            return Err(KeyError(f"User with id {user.id} does not exist"))

        self.dict[user.id] = user
        return Ok(None)

    async def update_user_partially(self, id: int,
                                    days_left: int = None, whole_budget: float = None,
                                    expense_today: float = None, income_today: float = None
                                    ) -> Result[None, Exception]:
        if id not in self.dict:
            return Err(KeyError(f"User with id {id} does not exist"))

        kwargs = {k: v for k, v in {
            'days_left': days_left,
            'whole_budget': whole_budget,
            'expense_today': expense_today,
            'income_today': income_today
        }.items() if v is not None}

        self.dict[id] = replace(self.dict[id], **kwargs)
        return Ok(None)

    async def add_or_update_user(self, user: User) -> Result[None, Exception]:
        if user.id not in self.dict:
            await self.add_user(user)
        else:
            await self.update_user(user)
        return Ok(None)


UserRepository: type = InMemoryUserRepository
