import logging
import uuid

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import app.state
import domain
from bot_modules import text, kb

start_router = Router()


class StartForm(StatesGroup):
    budget = State()
    days_left = State()
    timezone = State()
    categories = State()


def budget_request() -> str:
    msg = "<b>Начнём с настройки часового пояса.</b>"
    msg += "Сначала нужно ввести бюджет — "


def introduction() -> str:
    msg = "<b>Базовое взаимодействие с ботом выглядит так:</b>\n"
    msg += "- Вы вводите бюджет и срок, за который хотите потратить деньги\n"
    msg += "- Вы записываете траты в бота\n"
    msg += "- В конце дня бот даёт статистику по тратам\n"

    return msg


def settings_finished() -> str:
    return "<b>Отлично! Бот настроен.</b> Теперь можете пользоваться им: запишите трату, например <b>50</b>.\n<b>Подробнее про использование бота —</b> /help\n<b>Изменить настройки</b> можно с помощью /settings."


def ask_for_categories() -> str:
    return (
        "<b>Редактирование категорий</b>\nВведите названия <b>всех</b> категорий в одном сообщении, каждое с новой строки, "
        "например:\n\nЕда\nТранспорт\nРазвлечения\n\n")


def begin_tutorial_kb() -> InlineKeyboardMarkup:
    yes = InlineKeyboardButton(text="Начать пользоваться", callback_data="start_inter")
    kbd = InlineKeyboardMarkup(inline_keyboard=[[yes]])
    return kbd


def ask_categories_kb() -> InlineKeyboardMarkup:
    yes = InlineKeyboardButton(text="Настроить", callback_data="setup_categories")
    no = InlineKeyboardButton(text="Пропустить", callback_data="skip_categories_setup")
    kbd = InlineKeyboardMarkup(inline_keyboard=[[yes, no]])
    return kbd


def skip_categories_kb() -> InlineKeyboardMarkup:
    no = InlineKeyboardButton(text="Пропустить", callback_data="skip_categories_setup")
    kbd = InlineKeyboardMarkup(inline_keyboard=[[no]])
    return kbd


@start_router.message(Command(commands="help"))
async def command_help(message: Message) -> None:
    app.state.get().telemetry.int_values["Help used"] += 1
    await message.answer(text.help_msg(), parse_mode="HTML")


@start_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    sender = message.from_user.id
    await state.clear()
    msg = await message.answer(introduction())
    await msg.reply(
        "<b>Начнём с бюджета.</b> Подумайте, сколько денег вы хотите потратить (например, <b>1000</b>) и отправьте это число боту:")
    await state.set_state(StartForm.budget)


@start_router.message(StartForm.budget)
async def process_budget_step(message: Message, state: FSMContext) -> None:
    try:
        budget = float(message.text.replace("_", ""))
        if budget <= 1e-2:
            await message.answer(text.budget_must_be_positive(budget))
            return
        if budget >= 1_000_000_000:
            await message.answer(text.budget_too_big(budget))
            return
        await state.update_data(budget=budget)
        await state.set_state(StartForm.days_left)
        await message.answer("<b>На какой срок вы планируете бюджет?</b> Введите количество дней, например, <b>5</b>:")
    except ValueError:
        await message.answer(text.budget_must_be_float())


@start_router.message(StartForm.days_left)
async def process_days_left_step(message: Message, state: FSMContext) -> None:
    try:
        days_left = int(message.text)
        if days_left <= 0:
            await message.answer(text.days_left_must_be_positive(days_left))
            return
        if days_left >= 1000:
            await message.answer("<b>Выберите срок менее 1000 дней.</b>")
            return 

        await state.update_data(days_left=days_left)
        await message.answer(
            "<b>Теперь укажите ваш часовой пояс.</b> Это нужно, чтобы бот каждый день давал статистику и рассчитывал "
            "бюджет на следующий день.\n\nВведите <b>разницу в часах между вашим часовым поясом и московским "
            "временем</b>. Например, для Екатеринбурга это <b>2</b>, для Якутска — <b>6</b>  а для Калининграда — "
            "<b>-1</b>")
        await state.set_state(StartForm.timezone)
    except ValueError:
        await message.answer(text.days_left_must_be_int())


@start_router.message(StartForm.timezone)
async def process_timezone_from_msk(message: Message, state: FSMContext) -> None:
    try:
        sender = message.from_user.id
        timezone = int(message.text)
        if abs(timezone) >= 24:
            await message.answer(text.timezone_must_be_integer())
            return

        timezone_info = domain.UserTimezoneInfo(user_id=message.from_user.id, timezone=timezone, is_updatable=True)
        await app.state.get().tz_repo.add_or_update(timezone_info)
        await state.update_data(timezone=timezone)
        msg = await message.answer(text.timezone_saved(timezone))
        await msg.reply("<b>Отлично, базовая настройка окончена!</b>\n\nРасходы можно учитывать по категориям. Это "
                        "необязательная функция, и её настройку можно пропустить. Настроить сейчас?",
                        reply_markup=ask_categories_kb())
    except:
        await message.answer(text.timezone_must_be_integer())


@start_router.callback_query(lambda c: c.data == "setup_categories")
async def setup_categories(cq: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(StartForm.categories)
    await cq.answer()
    await cq.bot.send_message(cq.from_user.id, ask_for_categories(), reply_markup=skip_categories_kb())


@start_router.callback_query(lambda c: c.data == "skip_categories_setup")
async def skip_categories(cq: CallbackQuery, state: FSMContext) -> None:
    try:
        data = await state.get_data()
        id = cq.from_user.id
        budget = data["budget"]
        days_left = data["days_left"]
        await save_user(id, budget, days_left)
        await state.clear()
        await cq.message.edit_text(settings_finished(), reply_markup=None)
        app.state.get().telemetry.int_values["Start used"] += 1
    except Exception as e:
        logging.exception(e)
        await cq.bot.send_message(cq.message.chat.id, "<b>Неизвестная ошибка..</b> Попробуйте использовать /start ещё раз.")
    await cq.answer()

@start_router.message(StartForm.categories)
async def process_categories(message: Message, state: FSMContext) -> None:
    try:
        sender = message.from_user.id

        old_categories = (await app.state.get().bc_repo.get_categories_by_telegram_id(sender)).unwrap_or([])

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
            new_cat = domain.Category(uuid.uuid4().node % 2 ** 31, sender,
                                      c_name)  # FIXME Саня сделай получение id
            await app.state.get().bc_repo.add_category(new_cat)

        if len(new_categories) >= 7:
            await message.answer(text.too_many_categories(), reply_markup=kb.change_categories(), parse_mode="HTML")

        await message.answer(text.categories_set(created_names, (c.name for c in deleted), (c.name for c in unchanged)),
                             reply_markup=None, parse_mode="HTML")
        app.state.get().telemetry.int_values["Categories users"] += 1

        try:
            data = await state.get_data()
            id = sender
            budget = data["budget"]
            days_left = data["days_left"]
            await save_user(id, budget, days_left)
            await message.answer(settings_finished())
            await state.clear()
            app.state.get().telemetry.int_values["Start used"] += 1
        except Exception as e:
            logging.exception(e)
            await message.answer("<b>Неизвестная ошибка..</b> Попробуйте использовать /start ещё раз.")
        await state.clear()
    except ValueError:
        await message.answer(text.ask_for_categories(), reply_markup=kb.cancel_button())


async def save_user(id: int, budget: float, days_left: int):
    user = domain.User(id=id, days_left=days_left,
                       remaining_budget=budget - budget / days_left,
                       budget_today=budget / days_left, )
    await app.state.get().users_repo.add_or_update_user(user)
    await app.state.get().bc_repo.remove_all_budget_changes_by_tg_id(user.id)
