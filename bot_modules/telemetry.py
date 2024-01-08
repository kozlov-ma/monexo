from collections import defaultdict

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import app
from bot_modules import text

telemetry_router = Router()


@telemetry_router.message(Command("telemetry"))
async def command_stats(message: Message) -> None:
    await message.answer(str(app.state.get().telemetry))
