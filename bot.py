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

# Bot token can be obtained via https://t.me/BotFather
load_dotenv(".env")
TOKEN = getenv("BOT_TOKEN")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")


async def main() -> None:
    with open("admins", "r") as f:
        admins = [name.strip() for name in f.readlines()]

    await domain.init_db(f"postgresql+asyncpg://postgres:{POSTGRES_PASSWORD}@172.18.0.2/postgres")

    app.state.init(admin_usernames=admins, users_repo=domain.user_repository(),
                   bc_repo=domain.budget_change_repository(), tz_repo=domain.user_timezone_info_repository())

    await bot_modules.init_bot(TOKEN)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
