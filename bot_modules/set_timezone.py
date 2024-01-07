from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import domain

from bot_modules import text

import app

timezone_router = Router()
class TimezoneForm(StatesGroup):
    waiting_for_timezone = State()



@timezone_router.message(Command("timezone"))
async def command_change_timezone(message: Message, state: FSMContext) -> None:
    if (await app.state.get().tz_repo.get_by_id(message.from_user.id)) is None:
        await message.answer(text.must_have_settings_first())
        return

    await state.set_state(TimezoneForm.waiting_for_timezone)
    await message.answer(text.ask_for_timezone(), )


@timezone_router.message(TimezoneForm.waiting_for_timezone)
async def process_timezone_from_msk(message: Message, state: FSMContext) -> None:
    try:
        timezone = int(message.text)
        if abs(timezone) > 24:
            await message.answer(text.timezone_must_be_integer())
            return
        await state.clear()
        timezone_user = domain.UserTimezoneInfo(user_id=message.from_user.id, timezone=timezone,
                                                is_updatable=True)
        await app.state.get().tz_repo.add_or_update(timezone_user)
        await message.answer(text.current_timezone(timezone))

    except:
        await message.answer(text.timezone_must_be_integer())
