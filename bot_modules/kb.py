from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def change_categories() -> InlineKeyboardMarkup:
    btn = InlineKeyboardButton(text="Редактировать", callback_data="change_categories")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn]])

    return keyboard
