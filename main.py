import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from dotenv import load_dotenv

from pkg import state
from bot.handlers import start, admin, message


async def main() -> None:
    load_dotenv(".env")

    admins: list[str]
    with open('admins', 'r') as f:
        admins = [name.strip() for name in f.readlines()]

    state.init(bot_token=getenv("BOT_TOKEN"), admin_usernames=admins)

    # All handlers should be attached to the Router (or Dispatcher)
    dp = Dispatcher()
    dp.include_routers(start.router, admin.router, message.router)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(state.get().bot_token, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
