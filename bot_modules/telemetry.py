from collections import defaultdict

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import app
from bot_modules import text

telemetry_router = Router()


@telemetry_router.message(Command("telemetry"))
async def command_stats(message: Message) -> None:
    sender = message.from_user.id

    active_users = await app.state.get().users_repo.get_all()
    n_active_users = len(active_users)
    n_categories_users = 0
    avg_budget = 0
    for u in active_users:
        categories = (await app.state.get().bc_repo.get_categories_by_telegram_id(u.id)).unwrap_or([])
        if len(categories) > 0:
            n_categories_users += 0
        avg_budget += u.remaining_budget
    avg_budget /= n_active_users

    await message.answer(text.telemetry(n_active_users, n_categories_users, avg_budget))
