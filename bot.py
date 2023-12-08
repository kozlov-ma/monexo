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

# Bot token can be obtained via https://t.me/BotFather
load_dotenv(".env")
TOKEN = getenv("BOT_TOKEN")


async def main() -> None:
    with open("admins", "r") as f:
        admins = [name.strip() for name in f.readlines()]

    app.state.init(admin_usernames=admins, users_repo=domain.UserRepository())

    # Dispatcher is a root router
    dp = Dispatcher()
    # Register all the routers from bot_modules package
    dp.include_routers(
        start_router,
        settings_router,
        budget_change_router,
        next_day_router
    )

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
