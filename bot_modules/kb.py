import uuid

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app
import domain


def change_categories() -> InlineKeyboardMarkup:
    btn = InlineKeyboardButton(text="Редактировать", callback_data="change_categories")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn]])

    return keyboard


async def categories_for_expense(user_id: int, message_id: int, value: float) -> InlineKeyboardMarkup | None:
    categories = (await app.state.get().bc_repo.get_categories_by_telegram_id(user_id)).unwrap_or(None)
    if categories is None:
        return None

    msg_bc = (await app.state.get().bc_repo.get_budget_changes_by_message_id(message_id)).unwrap_or(None)
    if msg_bc is None:
        id = uuid.uuid4().int % 2 ** 31
        msg_bc = domain.BudgetChange(id, user_id, None, message_id, value)
        await app.state.get().bc_repo.add_budget_change(msg_bc)

    buttons = []
    for cat in categories:
        if msg_bc.category_id == cat.id:  # FIXME BUDGETCHANGE && SQLALCHEMY cat.id
            buttons.append(InlineKeyboardButton(text=f"{cat.name} ✅", callback_data=f"bc_{cat.id}"))
        else:
            buttons.append(InlineKeyboardButton(text=cat.name, callback_data=f"bc_{cat.id}"))

    return InlineKeyboardMarkup(inline_keyboard=[[b] for b in buttons])


def settings():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить бюджет", callback_data="change_budget")],
            [InlineKeyboardButton(text="Изменить количество дней", callback_data="change_days_left")],
            [InlineKeyboardButton(text="Изменить часовой пояс", callback_data="change_timezone")],
            [InlineKeyboardButton(text="Изменить категории", callback_data="change_categories")]
        ]
    )


def cancel_button() -> InlineKeyboardMarkup:
    btn = InlineKeyboardButton(text="Отменить", callback_data="cancel")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn]])

    return keyboard


def stop_keyboard() -> InlineKeyboardMarkup:
    functionality_useless = InlineKeyboardButton(text="Функции мне не подходят", callback_data="stop_useless")
    inconvenient = InlineKeyboardButton(text="Ботом неудобно пользоваться", callback_data="stop_inconvenient")
    lack_of_functionality = InlineKeyboardButton(text="Нет нужных мне функций",
                                                 callback_data="stop_lacks_functionality")
    competition = InlineKeyboardButton(text="Другой бот/приложение лучше", callback_data="stop_competition")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[functionality_useless], [inconvenient], [lack_of_functionality], [competition]])
    return keyboard


def confirm_stop() -> InlineKeyboardMarkup:
    stop_request = InlineKeyboardButton(text="Да, выключить бота", callback_data="rstop_request")
    cancel = InlineKeyboardButton(text="Нет, отменить", callback_data="cancel")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[stop_request], [cancel]])
    return keyboard
