import asyncio
import logging
from os import getenv

from dotenv import load_dotenv

import app
import domain
from bot_modules.start import start_router
from bot_modules.settings import settings_router
from bot_modules.budget_change import budget_change_router
from bot_modules.next_day import next_day_router
from bot_modules.toggle_autoupdate import autoupdate_router

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from datetime import datetime
import time
from pytz import timezone

from bot_modules.stats import stats_router


# Bot token can be obtained via https://t.me/BotFather
load_dotenv(".env")
TOKEN = getenv("BOT_TOKEN")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")


async def schedule_cycle():
    while True:
        if datetime.now().second == 0:
            await update_group_of_users()
            time.sleep(2)

async def update_group_of_users():
    users = await app.state.get().timezone_users_repo.get_all()
    for user in users:
        if datetime.now(timezone('Europe/Moscow')).minute + user.timezone() % 3 == 0 and user.is_updatable(): 
            next_day_router._next_day(user.user_id)


async def main() -> None:
    with open("admins", "r") as f:
        admins = [name.strip() for name in f.readlines()]

    await domain.init_db(f"postgresql+asyncpg://postgres:{POSTGRES_PASSWORD}@db/postgres")

    app.state.init(admin_usernames=admins, users_repo=domain.user_repository(), timezone_users_repo = domain.user_timezone_info_repository())

    # Dispatcher is a root router
    dp = Dispatcher()
    # Register all the routers from bot_modules package
    dp.include_routers(
        start_router,
        settings_router,
        autoupdate_router,
        budget_change_router,
        next_day_router,
        stats_router
    )

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


    await schedule_cycle()
    # And the run events dispatching
    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
