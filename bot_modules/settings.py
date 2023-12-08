import asyncio
import logging
import sys
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)

import app
import domain

settings_router = Router()


class SettingsForm(StatesGroup):
    budget = State()
    days_left = State()


@settings_router.message(Command("settings"))
async def command_settings(message: Message, state: FSMContext) -> None:
    await state.set_state(SettingsForm.budget)
    await message.answer(
        "Сколько денег вы хотите потратить? Введите число, например 1000 или 100.99",
        reply_markup=ReplyKeyboardRemove(),
    )


@settings_router.message(SettingsForm.budget)
async def process_budget(message: Message, state: FSMContext) -> None:
    try:
        budget = float(message.text)
        await state.update_data(budget=budget)
        await state.set_state(SettingsForm.days_left)
        await message.answer("На какой срок вы планируете бюджет? Введите количество дней, например 5")
    except ValueError:
        await message.answer(f"Введите число, например 1000 или 100.99")


@settings_router.message(SettingsForm.days_left)
async def process_days_left(message: Message, state: FSMContext) -> None:
    try:
        days_left = int(message.text)
        await state.update_data(days_left=days_left)

        data = await state.get_data()

        await state.clear()

        user = domain.User(id=message.from_user.id, days_left=data["days_left"],
                           remaining_budget=data["budget"] - data["budget"] / days_left,
                           budget_today=data["budget"] / days_left,
                           )
        await app.state.get().users_repo.add_or_update_user(user)

        await message.answer(f"Отлично! ")
    except ValueError:
        await message.answer(f"Введите число, например 5")
