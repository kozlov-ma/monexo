from collections import defaultdict

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import app
from bot_modules import text

stats_router = Router()


@stats_router.message(Command("stats"))
async def command_stats(message: Message) -> None:
    sender = message.from_user.id
    stats = (await app.stats(user_id=sender)).unwrap_or(None)
    if stats is None:
        await message.answer(text.must_have_settings_first())
    else:
        await message.answer(text.stats(stats))
        cat_stats = await category_stats(sender)
        if cat_stats is not None:
            await message.answer(cat_stats)


async def category_stats(user_id: int) -> str | None:
    bc_repo = app.state.get().bc_repo
    budget_changes = await bc_repo.get_budget_changes_by_telegram_id(user_id)
    expenses = defaultdict(float)
    for bc in budget_changes:
        if bc.is_income:
            continue
        if bc.category_id is None:
            continue

        category = await bc_repo.get_category_by_id(bc.category_id)
        expenses[category] += bc.value

    if any(expenses):
        return text.cat_stats(expenses)
    else:
        return None
