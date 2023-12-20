from abc import ABC, abstractmethod
from dataclasses import replace
from option import Option, Result, Ok, Err

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.user import User, DbUser


class UserRepositoryBase(ABC):
    def __init__(self, session: AsyncSession | None = None) -> None:
        pass

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
        super().__init__()

        self.dict: dict[int, User] = {}

    async def get_all(self) -> list[User]:
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


class PostgresUserRepository(UserRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session: AsyncSession = session

    async def get_all(self) -> list[User]:
        statement = select(DbUser)

        return list(user.to_user() for user in await self.session.scalars(statement))

    async def get_by_id(self, id: int) -> Option[User]:
        statement = (select(DbUser)
                     .where(DbUser.telegram_id == id))

        user = await self.session.scalar(statement)

        if user is None:
            return Option.NONE()

        return Option.Some(user.to_user())

    async def add_user(self, user: User) -> Result[None, Exception]:
        statement = (select(DbUser)
                     .where(DbUser.telegram_id == user.id))

        get_user = await self.session.scalar(statement)

        if get_user is not None:
            return Err(KeyError(f"User with id {user.id} already exists"))

        self.session.add(DbUser.from_user(user))
        await self.session.commit()
        return Ok(None)

    async def remove_user_by_id(self, id: int) -> Option[User]:
        statement = (select(DbUser)
                     .where(DbUser.telegram_id == id))

        get_user = await self.session.scalar(statement)

        if get_user is None:
            return Option.NONE()

        await self.session.delete(get_user)
        await self.session.commit()

        return Option.Some(get_user.to_user())

    async def update_user(self, user: User) -> Result[None, Exception]:
        statement = (select(DbUser)
                     .where(DbUser.telegram_id == user.id))

        get_user = await self.session.scalar(statement)

        if get_user is None:
            return Err(KeyError(f"User with id {user.id} already exists"))

        get_user.days_left = user.days_left
        get_user.remaining_budget = user.remaining_budget
        get_user.budget_today = user.budget_today
        get_user.expense_today = user.expense_today
        get_user.income_today = user.income_today

        await self.session.commit()

        return Ok(None)

    async def update_user_partially(self, id: int,
                                    days_left: int = None, remaining_budget: float = None, budget_today: float = None,
                                    expense_today: float = None, income_today: float = None
                                    ) -> Result[None, Exception]:
        statement = (select(DbUser)
                     .where(DbUser.telegram_id == id))

        get_user = await self.session.scalar(statement)

        if get_user is None:
            return Err(KeyError(f"User with id {id} is not exists"))

        if days_left is not None:
            get_user.days_left = days_left
        if remaining_budget is not None:
            get_user.remaining_budget = remaining_budget
        if budget_today is not None:
            get_user.budget_today = budget_today
        if expense_today is not None:
            get_user.expense_today = expense_today
        if income_today is not None:
            get_user.income_today = income_today

        await self.session.commit()

        return Ok(None)

    async def add_or_update_user(self, user: User) -> Result[None, Exception]:
        statement = (select(DbUser)
                     .where(DbUser.telegram_id == user.id))

        get_user = await self.session.scalar(statement)

        if get_user is not None:
            await self.update_user(user)
        else:
            await self.add_user(user)

        return Ok(None)


UserRepository: type = PostgresUserRepository
