import asyncio
import logging
from os import getenv


from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import app
import bot_modules
import domain
from bot_modules.budget_change import budget_change_router
from bot_modules.categories import categories_router
from bot_modules.next_day import next_day_router, next_day_for

from bot_modules.toggle_autoupdate import autoupdate_router

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode



from datetime import datetime, timedelta
import time
from pytz import timezone

from bot_modules.settings import settings_router
from bot_modules.start import start_router
from bot_modules.stats import stats_router
from bot_modules.telemetry import telemetry_router


load_dotenv(".env")
TOKEN = getenv("BOT_TOKEN")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")


async def update_group_of_users():
    users = await app.state.get().tz_repo.get_all()
    for user in users:
        if (datetime.now(timezone('Europe/Moscow')).hour + user.timezone) % 24 == 0 and user.is_updatable:
            await next_day_for(bot_modules.bot(), user.user_id)


async def main() -> None:
    with open("admins", "r") as f:
        admins = [name.strip() for name in f.readlines()]

    await domain.init_db(f"postgresql+asyncpg://postgres:{POSTGRES_PASSWORD}@db/postgres")

    app.state.init(admin_usernames=admins, users_repo=domain.user_repository(),
                   bc_repo=domain.budget_change_repository(), tz_repo=domain.user_timezone_info_repository())


    dp = Dispatcher()
    # Register all the routers from bot_modules package

    dp.include_routers(
        start_router,
        settings_router,
        autoupdate_router,
        budget_change_router,
        next_day_router,
        categories_router,
        stats_router,
        telemetry_router
    )

    now = datetime.now()
    next_hour = now.replace(microsecond=0, second=0, minute=0) + timedelta(hours=1)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_group_of_users, "interval", hours=1, start_date=next_hour)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    bot_modules.set_bot(bot)

    scheduler.start()
    await dp.start_polling(bot, skip_updates=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
