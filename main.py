import asyncio
from os import getenv

from dotenv import load_dotenv
from telethon import TelegramClient

import bot
from domain.repositories.user_repository import UserRepository
from app import state


async def main():
    load_dotenv(".env")
    admins: list[str]
    with open("admins", "r") as f:
        admins = [name.strip() for name in f.readlines()]

    state.init(admin_usernames=admins, users_repo=UserRepository())

    bot = TelegramClient("bot", int(getenv("API_ID")), getenv("API_HASH"))
    await bot.start(bot_token=getenv("BOT_TOKEN"))

    try:
        await bot.init(bot)
        await bot.run_until_disconnected()
    finally:
        await bot.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
