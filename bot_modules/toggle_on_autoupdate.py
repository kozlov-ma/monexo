from aiogram import Router
from aiogram.types import Message

from bot_modules import text

import domain

start_router = Router()


@start_router.message("/autoupdate")
async def command_start(message: Message) -> None: #TODO мб не хватает проверки на существования юзера
    domain.user_repository.update_user_partially(id=message.from_user.id, auto_update=True)
    await message.answer(text.TODO(), parse_mode="HTML")


@start_router.message("/untoupdate")
async def command_start(message: Message) -> None: #TODO мб не хватает проверки на существования юзера
    domain.user_repository.update_user_partially(id=message.from_user.id, auto_update=False)
    await message.answer(text.TODO(), parse_mode="HTML")