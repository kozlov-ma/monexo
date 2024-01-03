import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv

import app
import bot_modules
import domain
from bot_modules.budget_change import budget_change_router
from bot_modules.categories import categories_router
from bot_modules.next_day import next_day_router
from bot_modules.settings import settings_router
from bot_modules.start import start_router
from bot_modules.stats import stats_router
from bot_modules.telemetry import telemetry_router

load_dotenv(".env")
TOKEN = getenv("BOT_TOKEN")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")


async def main() -> None:
    with open("admins", "r") as f:
        admins = [name.strip() for name in f.readlines()]

    await domain.init_db(f"postgresql+asyncpg://postgres:{POSTGRES_PASSWORD}@db/postgres")

    app.state.init(admin_usernames=admins, users_repo=domain.user_repository(),
                   bc_repo=domain.budget_change_repository(), tz_repo=domain.user_timezone_info_repository())

    dp = Dispatcher()
    # Register all the routers from bot_modules package
    dp.include_routers(start_router, settings_router, budget_change_router, next_day_router, stats_router,
                       categories_router, telemetry_router)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    bot_modules.set_bot(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
