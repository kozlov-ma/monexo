from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode

from bot_modules.budget_change import budget_change_router
from bot_modules.categories import categories_router
from bot_modules.next_day import next_day_router
from bot_modules.settings import settings_router
from bot_modules.start import start_router
from bot_modules.stats import stats_router

bot: Bot = None


async def init_bot(token: str):
    global bot

    # Dispatcher is a root router
    dp = Dispatcher()
    # Register all the routers from bot_modules package
    dp.include_routers(start_router, settings_router, budget_change_router, next_day_router, stats_router,
                       categories_router)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(token, parse_mode=ParseMode.HTML)

    assert bot is not None
    # And the run events dispatching
    await dp.start_polling(bot, skip_updates=True)
