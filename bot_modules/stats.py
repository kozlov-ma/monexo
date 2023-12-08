from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import app
from bot_modules import text

stats_router = Router()


@stats_router.message(Command("stats"))
async def command_stats(message: Message) -> None:
    sender = message.from_user.id
    stats = (await app.stats(user_id=sender)).unwrap_or(None)
    if stats is None:
        await message.answer(text.must_have_settings_first())
    else:
        await message.answer(text.stats(stats))
