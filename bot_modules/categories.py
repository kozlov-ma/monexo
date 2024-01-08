import uuid

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

import app
import bot_modules
from bot_modules import text, kb
from domain.models.category import Category

categories_router = Router()


class CategoriesForm(StatesGroup):
    categories = State()


@categories_router.message(Command("categories"))
async def categories(message: Message) -> None:
    user_categories = await app.state.get().bc_repo.get_categories_by_telegram_id(message.from_user.id)
    if user_categories.is_none or len(user_categories.unwrap()) == 0:
        msg = text.no_categories_msg()
    else:
        msg = text.categories_msg(map(lambda c: c.name, user_categories.unwrap()))
    await message.answer(msg, reply_markup=kb.change_categories(), parse_mode="HTML")


@categories_router.callback_query(lambda c: c.data == "change_categories")
async def change_categories(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CategoriesForm.categories)
    await callback_query.answer()
    await bot_modules.bot().send_message(callback_query.from_user.id, text.ask_for_categories(), reply_markup=kb.cancel_button())


@categories_router.message(CategoriesForm.categories)
async def process_categories(message: Message, state: FSMContext) -> None:
    try:
        old_categories = (await app.state.get().bc_repo.get_categories_by_telegram_id(message.from_user.id)).unwrap_or([])

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
            new_cat = Category(uuid.uuid4().int % 2 ** 31, message.from_user.id,
                               c_name)  # FIXME Саня сделай получение id
            await app.state.get().bc_repo.add_category(new_cat)

        await state.clear()
        if len(new_categories) >= 7:
            await message.answer(text.too_many_categories(), reply_markup=kb.change_categories(), parse_mode="HTML")

        await message.answer(text.categories_set(created_names, (c.name for c in deleted), (c.name for c in unchanged)),
                             reply_markup=kb.change_categories(), parse_mode="HTML")
    except ValueError:
        await message.answer(text.ask_for_categories(), reply_markup=kb.cancel_button())
