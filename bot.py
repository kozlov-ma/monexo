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

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from bot_modules.stats import stats_router

import schedule
from datetime import datetime
from pytz import timezone

# Bot token can be obtained via https://t.me/BotFather
load_dotenv(".env")
TOKEN = getenv("BOT_TOKEN")


async def schedule_cycle():
    while True:
        await schedule.run_pending()


async def update_group_of_users():
    for user in domain.user_repository.get_all():
        if datetime.now(timezone('Europe/Moscow')).hour + user.time_zone_msk() % 24 == 0 and user.auto_update(): #ПРОВЕРИТЬ FIXME
            next_day_router._next_day(user.id) #FIXME проверить метод next_day_to


async def main() -> None:
    with open("admins", "r") as f:
        admins = [name.strip() for name in f.readlines()]



    schedule.every().hour.at(":00").do()

    app.state.init(admin_usernames=admins, users_repo=domain.UserRepository())

    # Dispatcher is a root router
    dp = Dispatcher()
    # Register all the routers from bot_modules package
    dp.include_routers(
        start_router,
        settings_router,
        budget_change_router,
        next_day_router,
        stats_router
    )

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)

    await schedule_cycle()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
