from collections import OrderedDict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app


def change_categories() -> InlineKeyboardMarkup:
    btn = InlineKeyboardButton(text="Редактировать", callback_data="change_categories")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn]])

    return keyboard


async def categories_for_expense(user_id: int, message_id: int) -> InlineKeyboardMarkup | None:
    categories = (await app.state.get().bc_repo.get_categories_by_telegram_id(user_id)).unwrap_or(None)
    if categories is None:
        return None

    msg_bc = (await app.state.get().bc_repo.get_budget_changes_by_message_id(message_id)).unwrap_or(None)
    if msg_bc is None:
        return None

    buttons = []
    for cat in categories:
        if msg_bc.category_id == cat.id: #FIXME BUDGETCHANGE
            buttons.append(InlineKeyboardButton(text=f"{cat.name} ✅", callback_data=f"bc_{cat.id}"))
        else:
            buttons.append(InlineKeyboardButton(text=cat.name, callback_data=f"bc_{cat.id}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])
