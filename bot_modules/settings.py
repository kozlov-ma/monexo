import logging
import uuid

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (Message, ReplyKeyboardRemove, CallbackQuery, )
from option import Option, Some, NONE

import app
import bot_modules
import domain
from bot_modules import text, kb

settings_router = Router()


class SettingsForm(StatesGroup):
    budget = State()
    days_left = State()
    timezone = State()
    categories = State()

    budget_step = State()
    days_left_step = State()
    timezone_step = State()


@settings_router.message(Command("settings"))
async def command_settings(message: Message, state: FSMContext) -> None:
    sender = message.from_user.id
    user = (await app.state.get().users_repo.get_by_id(sender)).unwrap_or(None)

    if user is None:
        await state.clear()
        if (await app.state.get().tz_repo.get_by_id(message.from_user.id)).unwrap_or(None) is None:
            await state.set_state(SettingsForm.timezone_step)
            await message.answer(text.ask_for_timezone(), reply_markup=kb.cancel_button())
        else:
            await state.set_state(SettingsForm.budget_step)
            await message.answer(text.ask_for_budget(), reply_markup=kb.cancel_button())
        return

    app.state.get().telemetry.int_values["Settings used"] += 1
    await message.answer(await get_settings_message(sender), reply_markup=kb.settings())


@settings_router.message(SettingsForm.timezone_step)
async def process_timezone_from_msk_step(message: Message, state: FSMContext) -> None:
    try:
        timezone = int(message.text)
        if abs(timezone) > 24:
            await message.answer(text.timezone_must_be_integer(), reply_markup=kb.cancel_button())
            return
        await state.update_data(timezone_msk=timezone)
        await state.update_data(is_updatable=True)
        await state.set_state(SettingsForm.budget_step)
        await message.answer(text.ask_for_budget(), reply_markup=kb.cancel_button())
    except:
        await message.answer(text.timezone_must_be_integer(), reply_markup=kb.cancel_button())


@settings_router.message(SettingsForm.budget_step)
async def process_budget_step(message: Message, state: FSMContext) -> None:
    try:
        budget = float(message.text.replace("_", ""))
        if budget <= 0:
            await message.answer(text.budget_must_be_positive(budget))
            return
        if budget >= 1_000_000_000:
            await message.answer(text.budget_too_big(budget))
            return
        await state.update_data(budget=budget)
        await state.set_state(SettingsForm.days_left_step)
        await message.answer(text.ask_for_days_left(), reply_markup=kb.cancel_button())
    except ValueError:
        await message.answer(text.budget_must_be_float(), reply_markup=kb.cancel_button())


@settings_router.message(SettingsForm.days_left_step)
async def process_days_left_step(message: Message, state: FSMContext) -> None:
    try:
        days_left = int(message.text)
        if days_left <= 0:
            await message.answer(text.days_left_must_be_positive(days_left), reply_markup=kb.cancel_button())
            return
        if days_left >= 1000:
            await message.answer("Выберите срок менее <b>1000</b> дней")
            return 

        await state.update_data(days_left=days_left)

        data = await state.get_data()

        await state.clear()

        user = domain.User(id=message.from_user.id, days_left=data["days_left"],
                           remaining_budget=data["budget"] - data["budget"] / days_left,
                           budget_today=data["budget"] / days_left, )
        await app.state.get().users_repo.add_or_update_user(user)
        await app.state.get().bc_repo.remove_all_budget_changes_by_tg_id(user.id)

        if "timezone_msk" in data.keys():
            timezone_user = domain.UserTimezoneInfo(user_id=message.from_user.id, timezone=data["timezone_msk"],
                                                    is_updatable=data["is_updatable"])
            await app.state.get().tz_repo.add_or_update(timezone_user)

            await message.answer(text.settings_with_time_saved(autoupdate=data["is_updatable"],
                                                               timezone=data["timezone_msk"],
                                                               budget=data["budget"],
                                                               days_left=data["days_left"]))
        else:
            await message.answer(text.settings_saved(budget=data["budget"],
                                                     days_left=data["days_left"]))

        app.state.get().telemetry.int_values["Total users"] += 1
    except ValueError:
        await message.answer(text.days_left_must_be_int(), reply_markup=kb.cancel_button())


async def get_settings_message(sender: int):
    user = (await app.state.get().users_repo.get_by_id(sender)).unwrap_or(None)
    if user is None:
        logging.exception(f"User {sender} is not exists")
        return """Тебя нет в базе данных:)
Чтобы там оказаться введи команду <b>/start</b>"""

    categories = (await app.state.get().bc_repo.get_categories_by_telegram_id(sender)).unwrap_or(None)
    if categories is None:
        logging.info(f"User {sender} has no categories")

    timezone = (await app.state.get().tz_repo.get_by_id(sender)).unwrap_or(None)
    if timezone is None:
        logging.info(f"User {sender} did not specify the time zone")

    return text.settings_message(user, timezone, categories)


@settings_router.callback_query(lambda c: c.data == "change_budget")
async def change_budget(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsForm.budget)
    await callback_query.answer()
    await bot_modules.bot().send_message(callback_query.from_user.id, text.ask_for_budget(),
                                         reply_markup=kb.cancel_button())


@settings_router.message(SettingsForm.budget)
async def process_budget(message: Message, state: FSMContext) -> None:
    try:
        sender = message.from_user.id
        budget = float(message.text.replace("_", ""))
        if budget <= 0:
            await message.answer(text.budget_must_be_positive(budget))
            return
        if budget >= 1_000_000_000:
            await message.answer(text.budget_too_big(budget))
            return

        user = (await app.state.get().users_repo.get_by_id(sender)).unwrap_or(None)
        if user is None:
            logging.error(f"User {sender} is not exists")
            return

        await app.state.get().users_repo.update_user_partially(sender, remaining_budget=budget,
                                                               budget_today=budget / user.days_left)
        await state.clear()
        await message.answer(f"""{text.budget_saved(budget)}

{await get_settings_message(sender)}""", reply_markup=kb.settings())
    except ValueError:
        await message.answer(text.budget_must_be_float(), reply_markup=kb.cancel_button())


@settings_router.callback_query(lambda c: c.data == "change_days_left")
async def change_days_left(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsForm.days_left)
    await callback_query.answer()
    await bot_modules.bot().send_message(callback_query.from_user.id, text.ask_for_days_left(),
                                         reply_markup=kb.cancel_button())


@settings_router.message(SettingsForm.days_left)
async def process_days_left(message: Message, state: FSMContext) -> None:
    try:
        sender = message.from_user.id
        days_left = int(message.text)
        if days_left <= 0:
            await message.answer(text.days_left_must_be_positive(days_left), reply_markup=kb.cancel_button())
            return
        if days_left >= 1000:
            await message.answer("Выберите срок менее <b>1000</b> дней")
            return
        
        user = (await app.state.get().users_repo.get_by_id(sender)).unwrap_or(None)
        if user is None:
            logging.error(f"User {sender} is not exists")
            return

        await app.state.get().users_repo.update_user_partially(sender, days_left=days_left,
                                                               budget_today=user.remaining_budget / days_left)

        await state.clear()
        await message.answer(f"""{text.days_left_saved(days_left)}

{await get_settings_message(sender)}""", reply_markup=kb.settings())
    except ValueError:
        await message.answer(text.days_left_must_be_int(), reply_markup=kb.cancel_button())


@settings_router.callback_query(lambda c: c.data == "change_timezone")
async def change_timezone(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsForm.timezone)
    await callback_query.answer()
    await bot_modules.bot().send_message(callback_query.from_user.id, text.ask_for_timezone(),
                                         reply_markup=kb.cancel_button())


@settings_router.message(SettingsForm.timezone)
async def process_timezone_from_msk(message: Message, state: FSMContext) -> None:
    try:
        sender = message.from_user.id
        timezone = int(message.text)
        if abs(timezone) > 24:
            await message.answer(text.timezone_must_be_integer(), reply_markup=kb.cancel_button())
            return

        timezone_info = domain.UserTimezoneInfo(user_id=message.from_user.id, timezone=timezone,
                                                is_updatable=True)
        await app.state.get().tz_repo.add_or_update(timezone_info)
        await state.clear()
        await message.answer(f"""{text.timezone_saved(timezone)}
        
{await get_settings_message(sender)}""", reply_markup=kb.settings())
    except:
        await message.answer(text.timezone_must_be_integer(), reply_markup=kb.cancel_button())


@settings_router.callback_query(lambda c: c.data == "change_categories")
async def change_categories(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsForm.categories)
    await callback_query.answer()
    await bot_modules.bot().send_message(callback_query.from_user.id, text.ask_for_categories(),
                                         reply_markup=kb.cancel_button())


@settings_router.message(SettingsForm.categories)
async def process_categories(message: Message, state: FSMContext) -> None:
    try:
        sender = message.from_user.id

        old_categories = (await app.state.get().bc_repo.get_categories_by_telegram_id(sender)).unwrap_or([])

        if message.text == "_":
            for c in old_categories:
                await app.state.get().bc_repo.remove_category_by_id(c.id)
            await message.answer(text.no_categories_msg(), reply_markup=kb.change_categories(), parse_mode="HTML")
            await state.clear()
            return

        new_categories = {c_name.strip() for c_name in message.text.split("\n")}
        if any("_" in c for c in new_categories):
            await message.answer(text.underscore_in_category_name(), reply_markup=kb.cancel_button())
            return

        old_names = {c.name for c in old_categories}
        created_names = {c for c in new_categories if c not in old_names}
        deleted = {c for c in old_categories if c.name not in new_categories}
        unchanged = {c for c in old_categories if c not in deleted}

        for c in deleted:
            await app.state.get().bc_repo.remove_category_by_id(c.id)

        for c_name in created_names:
            new_cat = domain.Category(uuid.uuid4().int % 2 ** 31, sender,
                                      c_name)  # FIXME Саня сделай получение id
            await app.state.get().bc_repo.add_category(new_cat)

        await state.clear()
        if len(new_categories) >= 7:
            await message.answer(text.too_many_categories(), reply_markup=kb.change_categories(), parse_mode="HTML")

        await message.answer(
            f"""{text.categories_set(created_names, (c.name for c in deleted), (c.name for c in unchanged))}
{await get_settings_message(sender)}
""",
            reply_markup=kb.settings(), parse_mode="HTML")

        app.state.get().telemetry.int_values["Categories users"] += 1
    except ValueError:
        await message.answer(text.ask_for_categories(), reply_markup=kb.cancel_button())
