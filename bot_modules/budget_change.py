import re
import re

from aiogram import F, Router
from aiogram.types import (Message, )

import app.state
from bot_modules import text

budget_change_router = Router()

MATH_REGEX = re.compile(r"^[+\-\d](\s?[-+/*]?\s?[._\d]+\s?(\._\d+)?)*$", re.A)
SINGLE_OPERAND_REGEX = re.compile(f"^[+\-]\d+$", re.A)


@budget_change_router.message(F.text.regexp(MATH_REGEX))
async def budget_change(message: Message) -> None:
    sender_id = message.from_user.id
    try:
        result = eval(message.text.replace("_", ""))
    except Exception as e:
        await message.answer(text.arithmetic_error(message.text), parse_mode="HTML")
        return

    amount = abs(result)

    if result == 0:
        await message.answer(text.cannot_spend_zero_sum(), parse_mode="HTML")
        return

    if SINGLE_OPERAND_REGEX.match(message.text) and result > 0:
        change = (await app.add_income(sender_id, amount)).unwrap_or(None)
        if change is None:
            await message.answer(text.must_have_settings_first(), parse_mode="HTML")
            return
        await message.answer(text.added_money(change), parse_mode="HTML")
    else:
        if not SINGLE_OPERAND_REGEX.match(message.text) and result < 0:
            await message.answer(text.cannot_enter_negative_sum(result), parse_mode="HTML")
            return
        else:
            change = (await app.add_expense(sender_id, amount)).unwrap_or(None)
            match change:
                case app.Spent():
                    await message.answer(text.spent_money(change), parse_mode="HTML")
                case app.SpentOverDailyBudget():
                    await message.answer(text.spent_over_daily_budget(change), parse_mode="HTML")
                case app.SpentAllBudget():
                    await message.answer(text.spent_all_budget(change), parse_mode="HTML")
                case None:
                    await message.answer(text.must_have_settings_first(), parse_mode="HTML")
                case _:
                    raise ValueError(f"Unknown change type: {type(change)}")
