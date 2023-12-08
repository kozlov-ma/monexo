import logging

import aiogram
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.methods import SendMessage
from aiogram.types import Message
from aiogram.utils import markdown
from option import Option, Some, NONE

import app
import domain

next_day_router = Router()


@next_day_router.message(Command("nextday"))
async def command_next_day(message: Message) -> None:
    sender = message.from_user.id
    msg = await _next_day(sender)
    if msg.is_some:
        await message.answer(msg.unwrap())
    else:
        await message.answer("Произошла ошибка..")


async def _next_day(user_id: int) -> Option[str]:
    user = (await app.state.get().users_repo.get_by_id(user_id)).unwrap_or(None)
    if user is None:
        return Some("Сначала введите срок и бюджет с помощью /settings")

    result = (await app.budget.apply_today(user.id)).unwrap_or(None)
    if result is None:
        return NONE

    match result:
        case app.PeriodEnded(saved=float(s)):
            if s <= 1e-3:
                msg = "Период закончился. Начнём сначала? /settings"
            else:
                msg = f"Успех ! Период закончился и удалось сэкономить **{s}**! Начнём сначала? /settings"
            await SendMessage(chat_id=user_id, text=msg)
        case app.DayResults(
            income,
            expense,
            saved,
            new_remaining_budget,
            new_daily_budget,
            new_days_left,
        ):
            msg = "**Начался новый день!**\n"
            if income > 0:
                msg += f"Доходы за день: **{income}**\n"
            if expense > 0:
                msg += f"Расходы за день: **{expense}**\n"
            if saved > 0:
                msg += f"Удалось сэкономить: **{saved}**\n"

            msg += f"Остаток на **{new_days_left}** дней: **{new_remaining_budget}**\n"
            msg += f"Бюджет на завтра: **{new_daily_budget}**"

            return Some(msg)

        case _:
            logging.error(
                f"Unknown result type for 'app.budget.apply_today()': {type(result)}, result: {result}"
            )
            return NONE


async def next_day_for(bot: aiogram.Bot, user_id: int) -> None:
    msg = await _next_day(user_id)
    if msg.is_some:
        await bot.send_message(user_id, msg.unwrap())
