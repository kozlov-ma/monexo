from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (Message, ReplyKeyboardRemove, )

import app
import domain
from bot_modules import text

settings_router = Router()


class SettingsForm(StatesGroup):
    budget = State()
    days_left = State()
    timezone_msk = State()
    is_updatable = State()


@settings_router.message(Command("settings"))
async def command_settings(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsForm.timezone_msk)
    await message.answer(text.ask_for_timezone(), reply_markup=ReplyKeyboardRemove(), )


@settings_router.message(SettingsForm.timezone_msk)
async def process_timezone_from_msk(message: Message, state: FSMContext) -> None:
    try:
        timezone = int(message.text)
        if abs(timezone) > 24:
            await message.answer(text.timezone_must_be_integer())
            return
        await state.update_data(timezone_msk=timezone)
        await state.update_data(is_updatable=True)
        await state.set_state(SettingsForm.budget)
        await message.answer(text.ask_for_budget())
    except:
        await message.answer(text.timezone_must_be_integer())


@settings_router.message(SettingsForm.budget)
async def process_budget(message: Message, state: FSMContext) -> None:
    try:
        budget = float(message.text.replace("_", ""))
        if budget <= 0:
            await message.answer(text.budget_must_be_positive(budget))
            return
        if len(message.text) >= 5:
            await message.answer(text.big_numbers_format_hint())
        await state.update_data(budget=budget)
        await state.set_state(SettingsForm.days_left)
        await message.answer(text.ask_for_days_left())
    except ValueError:
        await message.answer(text.budget_must_be_float())


@settings_router.message(SettingsForm.days_left)
async def process_days_left(message: Message, state: FSMContext) -> None:
    try:
        days_left = int(message.text)
        if days_left <= 0:
            await message.answer(text.days_left_must_be_positive(days_left))
            return

        await state.update_data(days_left=days_left)

        data = await state.get_data()

        await state.clear()

        user = domain.User(id=message.from_user.id, days_left=data["days_left"],
                           remaining_budget=data["budget"] - data["budget"] / days_left,
                           budget_today=data["budget"] / days_left, )
        
        timezone_user = domain.UserTimezoneInfo(user_id=message.from_user.id, timezone=data["timezone_msk"], is_updatable=data["is_updatable"])

        await app.state.get().users_repo.add_or_update_user(user)
        await app.state.get().timezone_users_repo.add_or_update(timezone_user)

        await message.answer(text.settings_saved(autoupdate=data["is_updatable"], 
                                                 timezone=data["timezone_msk"], 
                                                 budget=data["budget"], 
                                                 days_left=data["days_left"]))
    except ValueError:
        await message.answer(text.days_left_must_be_int())
