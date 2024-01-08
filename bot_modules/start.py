from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import app.state
import domain
from bot_modules import text

start_router = Router()


@start_router.message(Command(commands=['help', 'start']))
async def command_start(message: Message) -> None:
    app.state.get().telemetry.int_values["Start or Help used"] += 1
    await message.answer(text.help_msg(), parse_mode="HTML")
