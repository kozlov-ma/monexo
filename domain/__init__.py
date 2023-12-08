from domain.models.user import User
from domain.repositories.user_repository import UserRepository
from domain.models.db_base import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


__user_repository = None


async def init_db(db_url: str) -> None:
    global __user_repository

    engine = create_async_engine(db_url, echo=True, query_cache_size=0)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    session = AsyncSession(engine)
    __user_repository = UserRepository(session)


def user_repository() -> UserRepository | None:
    return __user_repository
