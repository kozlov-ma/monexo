import logging

import aiogram
from aiogram import Router
from aiogram.filters import Command
from aiogram.methods import SendMessage
from aiogram.types import Message
from option import Option, Some, NONE

import app
from bot_modules import text

next_day_router = Router()


@next_day_router.message(Command("nextday"))
async def command_next_day(message: Message) -> None:
    sender = message.from_user.id
    
    app.state.update_user_partially(id=sender, auto_update=False)
    
    msg = await _next_day(sender)
    if msg.is_some:
        await message.answer(msg.unwrap())
    else:
        await message.answer("Произошла ошибка..")


async def _next_day(user_id: int) -> Option[str]:
    user = (await app.state.get().users_repo.get_by_id(user_id)).unwrap_or(None)
    if user is None:
        return Some(text.must_have_settings_first())

    result = (await app.budget.apply_today(user.id)).unwrap_or(None)
    if result is None:
        return NONE

    match result:
        case app.PeriodEnded(saved=float(s)):
            msg = text.period_ended(s)
            await SendMessage(chat_id=user_id, text=msg)
        case app.DayResults():
            return Some(text.day_results(result))
        case _:
            logging.error(f"Unknown result type for 'app.budget.apply_today()': {type(result)}, result: {result}")
            return NONE


async def next_day_for(bot: aiogram.Bot, user_id: int) -> None:
    msg = await _next_day(user_id)
    if msg.is_some:
        await bot.send_message(user_id, msg.unwrap())
