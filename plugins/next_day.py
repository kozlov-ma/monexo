import asyncio

import loguru
from telethon import events, TelegramClient
from telethon.tl.custom import Message
from telethon.tl.types import User as TgUser

import app.budget
from app import state
from domain import User
from domain.models.budget import DayResults, PeriodEnded

from option import Result


async def init(bot: TelegramClient):
    @bot.on(events.NewMessage(pattern="/nextday"))
    async def next_day(event: Message) -> None:
        sender: TgUser = await event.get_sender()

        user = (await state.get().users_repo.get_by_id(sender.id)).unwrap_or(None)
        if user is None:
            await event.respond("Сначала зарегистрируйтесь с помощью /start")
            return

        await next_day_for(bot, user)

    asyncio.create_task(update_users_periodically(bot, 24 * 60 * 60))


async def update_users_periodically(bot: TelegramClient, duration_secs: float) -> None:
    await asyncio.sleep(duration_secs)
    tasks = []

    users = (await state.get().users_repo.get_all()).unwrap()

    for user in users:
        tasks.append(next_day_for(bot, user))

    await asyncio.gather(*tasks)

    loguru.logger.info(f"Updated all users, next update in {duration_secs} seconds.")


async def next_day_for(bot: TelegramClient, user: User) -> None:
    tg_user = TgUser(user.id)

    result = (await app.budget.apply_today(user.id)).unwrap_or(None)
    if result is None:
        return

    match result:
        case PeriodEnded(saved=float(s)):
            if s <= 1e-3:
                msg = "Период закончился. Начнём сначала? /start"
            else:
                msg = f"Период закончился. Удалось сэкономить **{s}**. Начнём сначала? /start"
            await bot.send_message(tg_user, msg)
        case DayResults(
            income,
            expense,
            saved,
            new_remaining_budget,
            new_daily_budget,
            new_days_left,
        ):
            msg = "**День Закончился!**\n"
            if income > 0:
                msg += f"Доходы за день: **{income}**\n"
            if expense > 0:
                msg += f"Расходы за день: **{expense}**\n"
            if saved > 0:
                msg += f"Удалось сэкономить: **{saved}**\n"

            msg += f"Остаток на **{new_days_left}** дней: **{new_remaining_budget}**\n"
            msg += f"Бюджет на завтра: **{new_daily_budget}**"

            await bot.send_message(tg_user, msg)
        case _:
            loguru.logger.error(
                f"Unknown result type for 'app.budget.apply_today()': {type(result)}, result: {result}"
            )
            await bot.send_message(tg_user, "Произошла ошибка.")
