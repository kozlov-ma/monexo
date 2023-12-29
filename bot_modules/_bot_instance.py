import asyncio
from typing import Coroutine

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode

from bot_modules.budget_change import budget_change_router
from bot_modules.categories import categories_router
from bot_modules.next_day import next_day_router
from bot_modules.settings import settings_router
from bot_modules.start import start_router
from bot_modules.stats import stats_router

bot: Bot = None


def set_bot(instance: Bot):
    global bot
    bot = instance
