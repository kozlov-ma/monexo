from aiogram import Router
from aiogram.types import Message
from aiogram.utils.formatting import Text, Code
from aiogram.filters import Command
from pkg import state

router = Router()


@router.message()
async def echo_with_time(message: Message):
    try:
        result = eval(message.text, {}, {})  # FIXME можно закинуть например 2**298127412 и произойдёт смерть
        await message.answer(f"Пока умею только калькулировать. {result}")
    except:
        await message.answer("Данное выражение содержит арифметическую ошибку.")
