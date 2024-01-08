import logging

from domain.models.user import User
from domain.models.user_timezone_info import UserTimezoneInfo
from domain.models.budget_change import BudgetChange
from domain.models.category import Category
from domain.repositories.user_repository import UserRepository
from domain.models.db_base import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from domain.repositories.user_timezone_info_repository import UserTimezoneInfoRepository
from domain.repositories.budget_change_repository import BudgetChangeRepository

__user_repository = None
__user_timezone_info_repository = None
__budget_change_repository = None


async def init_db(db_url: str) -> None:
    global __user_repository
    global __user_timezone_info_repository
    global __budget_change_repository

    engine = create_async_engine(db_url, echo=True, query_cache_size=0)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(bind=engine)
    session = Session()
    __user_repository = UserRepository(session)
    __user_timezone_info_repository = UserTimezoneInfoRepository(session)
    __budget_change_repository = BudgetChangeRepository(session)


def user_repository() -> UserRepository | None:
    return __user_repository


def user_timezone_info_repository() -> UserTimezoneInfoRepository | None:
    return __user_timezone_info_repository


def budget_change_repository() -> BudgetChangeRepository | None:
    return __budget_change_repository
