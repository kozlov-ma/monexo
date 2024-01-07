from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


from bot_modules import text

import app

autoupdate_router = Router()


@autoupdate_router.message(Command("autoupdate_on"))
async def command_start(message: Message) -> None: #TODO мб не хватает проверки на существования юзера
    await app.state.get().tz_repo.update_partially(id=message.from_user.id, is_updatable=True)
    await message.answer(text.autoupdate_enabled(), parse_mode="HTML")


@autoupdate_router.message(Command("autoupdate_off"))
async def command_start(message: Message) -> None: #TODO мб не хватает проверки на существования юзера
    await app.state.get().tz_repo.update_partially(id=message.from_user.id, is_updatable=False)
    await message.answer(text.autoupdate_disabled(), parse_mode="HTML")