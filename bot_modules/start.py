from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot_modules import text

start_router = Router()


@start_router.message(Command(commands=['start', 'help']))
async def command_start(message: Message) -> None:
    await message.answer(text.help_msg(), parse_mode="HTML")