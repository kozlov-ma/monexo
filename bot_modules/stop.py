import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import app
from bot_modules import text, kb

stop_router = Router()


@stop_router.message(Command("stop"))
async def command_stop(message: Message) -> None:
    await message.answer(text.confirm_stop(), parse_mode="HTML", reply_markup=kb.confirm_stop())


@stop_router.callback_query(lambda c: c.data == "rstop_request")
async def callback_stop(cq: CallbackQuery) -> None:
    app.state.get().telemetry.int_values["Stopped using bot"] += 1
    try:
        await cq.message.edit_text(text.stop_msg(), reply_markup=kb.stop_keyboard())
        await app.state.get().users_repo.remove_user_by_id(cq.from_user.id)  # FIXME result
        await app.state.get().bc_repo.remove_all_budget_changes_by_tg_id(cq.from_user.id)
        await cq.answer("Бот остановлен..")
    except Exception as e:
        logging.exception(e)
        await cq.message.delete()


@stop_router.callback_query(lambda c: c.data.startswith("stop_"))
async def callback_stop_reason(cq: CallbackQuery) -> None:
    d = cq.data
    match d:
        case "stop_useless":
            app.state.get().telemetry.int_values["Stopped using: useless"] += 1
        case "stop_inconvenient":
            app.state.get().telemetry.int_values["Stopped using: inconvenient"] += 1
        case "stop_lacks_functionality":
            app.state.get().telemetry.int_values["Stopped using: lacks functionality"] += 1
        case "stop_competition":
            app.state.get().telemetry.int_values["Stopped using: competition"] += 1

    await cq.answer("Спасибо за отзыв!")
    await cq.message.edit_text(text.thanks_for_review(), reply_markup=None)


@stop_router.message(Command("toall"))
async def command_toall(message: Message) -> None:
    sender_name = message.from_user.username
    if sender_name not in app.state.get().admin_usernames:
        await message.answer(text.you_have_to_be_admin())
    else:
        content = message.text.replace("/toall", "").strip()
        users = await app.state.get().users_repo.get_all()
        for user in users:
            await message.bot.send_message(user.id, content)
        await message.reply("<b>Успех</b>")