from abc import ABC, abstractmethod
from dataclasses import replace
from option import Option, Result, Ok, Err

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.user_timezone_info import UserTimezoneInfo, DbUserTimezoneInfo


class UserTimezoneInfoRepositoryBase(ABC):
    def __init__(self, session: AsyncSession | None = None) -> None:
        pass

    @abstractmethod
    async def get_all(self) -> Option[list[UserTimezoneInfo]]:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Option[UserTimezoneInfo]:
        pass

    @abstractmethod
    async def add(self, timezone: UserTimezoneInfo) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def remove_by_id(self, id: int) -> Option[UserTimezoneInfo]:
        pass

    @abstractmethod
    async def update(self, timezone: UserTimezoneInfo) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def update_partially(self, id: int, **kwargs) -> Result[None, Exception]:
        pass

    @abstractmethod
    async def add_or_update(self, timezone: UserTimezoneInfo) -> Result[None, Exception]:
        pass


class PostgresUserTimezoneInfoRepository(UserTimezoneInfoRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session: AsyncSession = session

    async def get_all(self) -> Option[list[UserTimezoneInfo]]:
        statement = select(DbUserTimezoneInfo)

        return Option.Some(list(await self.session.scalars(statement)))

    async def get_by_id(self, id: int) -> Option[UserTimezoneInfo]:
        statement = (select(DbUserTimezoneInfo)
                     .where(DbUserTimezoneInfo.user_telegram_id == id))

        timezone = await self.session.scalar(statement)

        if timezone is None:
            return Option.NONE()

        return Option.Some(timezone.to_timezone())

    async def add(self, timezone: UserTimezoneInfo) -> Result[None, Exception]:
        statement = (select(DbUserTimezoneInfo)
                     .where(DbUserTimezoneInfo.user_telegram_id == timezone.user_id))

        get_user = await self.session.scalar(statement)

        if get_user is not None:
            return Err(KeyError(f"Timezone with id {timezone.user_id} already exists"))

        self.session.add(DbUserTimezoneInfo.from_timezone(timezone))
        await self.session.commit()
        return Ok(None)

    async def remove_by_id(self, id: int) -> Option[UserTimezoneInfo]:
        statement = (select(DbUserTimezoneInfo)
                     .where(DbUserTimezoneInfo.user_telegram_id == id))

        get_timezone = await self.session.scalar(statement)

        if get_timezone is None:
            return Option.NONE()

        await self.session.delete(get_timezone)
        await self.session.commit()

        return Option.Some(get_timezone.to_timezone())

    async def update(self, timezone: UserTimezoneInfo) -> Result[None, Exception]:
        statement = (select(DbUserTimezoneInfo)
                     .where(DbUserTimezoneInfo.user_telegram_id == timezone.user_id))

        get_timezone = await self.session.scalar(statement)

        if get_timezone is None:
            return Err(KeyError(f"Timezone with id {timezone.user_id} already exists"))

        get_timezone.timezone = timezone.timezone
        get_timezone.is_updatable = timezone.is_updatable

        await self.session.commit()

        return Ok(None)

    async def update_partially(self, id: int, timezone: int = None, is_updatable: bool = None
                               ) -> Result[None, Exception]:
        statement = (select(DbUserTimezoneInfo)
                     .where(DbUserTimezoneInfo.user_telegram_id == id))

        get_timezone = await self.session.scalar(statement)

        if get_timezone is None:
            return Err(KeyError(f"Timezone with id {id} is not exists"))

        if timezone is not None:
            get_timezone.timezone = timezone
        if is_updatable is not None:
            get_timezone.is_updatable = is_updatable

        await self.session.commit()

        return Ok(None)

    async def add_or_update(self, timezone: UserTimezoneInfo) -> Result[None, Exception]:
        statement = (select(DbUserTimezoneInfo)
                     .where(DbUserTimezoneInfo.user_telegram_id == timezone.user_id))

        get_timezone = await self.session.scalar(statement)

        if get_timezone is not None:
            await self.update(timezone)
        else:
            await self.add(timezone)

        return Ok(None)


UserTimezoneInfoRepository: type = PostgresUserTimezoneInfoRepository
