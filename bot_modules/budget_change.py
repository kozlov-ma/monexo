import asyncio
import logging
import sys
from typing import Any, Dict
import re

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.types import (
    Message,
)

import app.state

budget_change_router = Router()

MATH_REGEX = re.compile(r"^[+\-\d]([-+/*]?[._\d]+(\._\d+)?)*$", re.A)
SINGLE_OPERAND_REGEX = re.compile(f"^[+\-]([-+/*]?[._\d]+(\._\d+)?)*$", re.A)


@budget_change_router.message(F.text.regexp(MATH_REGEX))
async def budget_change(message: Message) -> None:
    sender_id = message.from_user.id
    try:
        result = eval(message.text.replace("_", ""))
    except Exception as e:
        await message.answer(
            f"Выражение **{message.text}** содержит ошибку и не может быть вычислено"
        )
        return

    amount = abs(result)

    if result == 0:
        await message.answer(f"Нельзя добавить/потратить нулевую сумму.")
        return

    if SINGLE_OPERAND_REGEX.match(message.text) and result > 0:
        change = (await app.add_income(sender_id, amount)).unwrap_or(None)
        if change is None:
            await message.answer(
                "Чтобы использовать бота, зарегистрируйтесь с помощью /start"
            )
            return
        await message.answer(
            f"Добавлено **{change.amount}**. Теперь на сегодня доступно **{change.new_budget_today}**"
        )
    else:
        if not SINGLE_OPERAND_REGEX.match(message.text) and result < 0:
            await message.answer(
                f"Введена отрицательная сумма: **{result}**. Если хотите потратить деньги, введите положительное "
                f"число, например **{abs(result)}**"
            )
            return
        else:
            change = (await app.add_expense(sender_id, amount)).unwrap_or(None)
            if change is None:
                await message.answer(
                    "Чтобы использовать бота, зарегистрируйтесь с помощью /start"
                )
                return

            match change:
                case app.Spent(amount, new_budget_today):
                    await message.answer(
                        f"Потрачено **{amount}**. Теперь на сегодня доступно **{new_budget_today}**"
                    )
                case app.SpentOverDailyBudget(amount, new_budget_today):
                    await message.answer(
                        f"Потрачено **{amount}**. Больше денег нет.")
