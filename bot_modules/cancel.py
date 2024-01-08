from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.state
from bot_modules import text

cancel_router = Router()


@cancel_router.message(Command('cancel'))
async def command_cancel(message: Message, state: FSMContext) -> None:
    app.state.get().telemetry.int_values["Cancel used"] += 1
    await state.clear()
    await message.answer(text.cancelled(), parse_mode="HTML")


@cancel_router.callback_query(lambda c: c.data == "cancel")
async def callback_cancel(cq: CallbackQuery, state: FSMContext) -> None:
    app.state.get().telemetry.int_values["Cancel used"] += 1
    await state.clear()
    await cq.message.delete()
    await cq.answer(text.cancelled_for_callback())
