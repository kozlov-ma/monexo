from abc import ABC, abstractmethod
from dataclasses import replace
from option import Option, Result, Ok, Err

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from redis.commands.search.field import TextField, NumericField, TagField
from json import dumps, loads

from domain.models.user import User, DbUser
import loguru


class UserRepositoryBase(ABC):
    def __init__(self, session: AsyncSession | None = None, redis: Redis | None = None) -> None:
        pass

    @abstractmethod
    async def get_all(self) -> list[User]:
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
    async def add(self, user: User) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def remove_by_id(self, id: int) -> Option[User]:
        pass

    @abstractmethod
    async def update(self, user: User) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def update_partially(self, id: int, **kwargs) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def add_or_update(self, user: User) -> Result[None, Exception]:
        pass


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

    async def add(self, user: User) -> Result[None, Exception]:
        statement = (select(DbUser)
                     .where(DbUser.telegram_id == user.id))

        get_user = await self.session.scalar(statement)

        if get_user is not None:
            return Err(KeyError(f"User with id {user.id} already exists"))

        self.session.add(DbUser.from_user(user))
        await self.session.commit()
        return Ok(None)

    async def remove_by_id(self, id: int) -> Option[User]:
        statement = (select(DbUser)
                     .where(DbUser.telegram_id == id))

        get_user = await self.session.scalar(statement)

        if get_user is None:
            return Option.NONE()

        await self.session.delete(get_user)
        await self.session.commit()

        return Option.Some(get_user.to_user())

    async def update(self, user: User) -> Result[None, Exception]:
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

    async def update_partially(self, id: int,
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

    async def add_or_update(self, user: User) -> Result[None, Exception]:
        statement = (select(DbUser)
                     .where(DbUser.telegram_id == user.id))

        get_user = await self.session.scalar(statement)

        if get_user is not None:
            await self.update(user)
        else:
            await self.add(user)

        return Ok(None)


class RedisUserRepository(UserRepositoryBase):
    def __init__(self, redis: Redis):
        super().__init__()
        self.redis = redis
        self.schema = (

        )

    async def get_all(self) -> list[User]:
        keys = self.redis.hkeys("user")

        result = []
        for key in keys:
            get_user = await self.redis.hgetall(f"user:{key}")
            result.append(User(**get_user))

        return result

    async def get_by_id(self, id: int) -> Option[User]:
        get_user = await self.redis.hgetall(f"user:{id}")
        loguru.logger.info(get_user)

        if get_user == {}:
            return Option.NONE()

        return Option.Some(User(**get_user))

    async def add(self, user: User) -> Result[None, Exception]:
        loguru.logger.info(user.__dict__)
        await self.redis.hset(f"user:{user.id}", mapping=user.__dict__)
        return Result.Ok(None)

    async def remove_by_id(self, id: int) -> Option[User]:
        get_user = await self.redis.hgetall(f"user:{id}")

        if get_user == {}:
            return Option.NONE()

        user = User(**get_user)
        await self.redis.hdel(f"user:{id}")
        return Option.Some(user)

    async def update(self, user: User) -> Result[None, Exception]:
        get_user = await self.redis.hgetall(f"user:{id}")

        if get_user == {}:
            return Result.Err(KeyError())

        await self.redis.hset(f"user:{user.id}", mapping=user.__dict__)
        return Result.Ok(None)

    async def update_partially(self, id: int, **kwargs) -> Result[None, Exception]:
        pass

    async def add_or_update(self, user: User) -> Result[None, Exception]:
        get_user = await self.redis.hgetall(f"user:{user.id}")

        if get_user == {}:
            return await self.add(user)
        else:
            return await self.update(user)


UserRepository: type = RedisUserRepository
