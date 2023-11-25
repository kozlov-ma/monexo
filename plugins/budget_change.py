import datetime
import re

import loguru
from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User

from app import state
from app.budget import add_income, add_expense
from domain.models.budget import Spent, SpentOverDailyBudget, SpentAllBudget
from plugins import settings

MATH_REGEX = re.compile(r"^\d*([-+/*]\d+(\.\d+)?)*$", re.A)
SINGLE_OPERAND_REGEX = re.compile(f"[+\-][1-9]\d+(\.\d+)?$", re.A)


async def init(bot):
    @bot.on(events.NewMessage(pattern=MATH_REGEX))
    async def budget_change(event: Message) -> None:
        sender: User = await event.get_sender()

        if await settings.is_message_settings_change(event):
            return

        user = (await state.get().users_repo.get_by_id(sender.id)).unwrap_or(None)

        if user is None:
            await event.respond(
                "Чтобы использовать бота, зарегистрируйтесь с помощью /start"
            )
            return

        try:
            result = eval(event.text)
        except Exception as e:
            await event.respond(
                f"Выражение **{event.text}** содержит ошибку и не может быть вычислено"
            )
            return

        amount = abs(result)

        if result == 0:
            await event.respond(f"Нельзя добавить/потратить нулевую сумму.")
            return

        if SINGLE_OPERAND_REGEX.match(event.text) and result > 0:
            change = (await add_income(user, amount)).expect("checked before")
            await event.respond(
                f"Добавлено **{change.amount}**. Теперь на сегодня доступно **{change.new_budget_today}**"
            )
        else:
            if not SINGLE_OPERAND_REGEX.match(event.text) and result < 0:
                await event.respond(
                    f"Введена отрицательная сумма: **{result}**. Если хотите потратить деньги, введите положительное "
                    f"число, например **{abs(result)}**"
                )
                return
            else:
                change = (await add_expense(user, amount)).expect("checked before")
                match change:
                    case Spent(amount, new_budget_today):
                        await event.respond(
                            f"Потрачено **{amount}**. Остаток на сегодня: **{new_budget_today}**"
                        )
                    case SpentOverDailyBudget(amount, new_daily_budget):
                        await event.respond(
                            f"Потрачено **{amount}**. Остаток на сегодня: **0**. Теперь новый бюджет на день: **{new_daily_budget}**."
                        )
                    case SpentAllBudget(amount):
                        await event.respond(
                            f"Потрачено **{amount}**. Больше денег нет."
                        )
                    case _:
                        await event.respond(
                            f"Произошла ошибка, повторите попытку позднее.."
                        )
                        loguru.logger.error(
                            f"Unknown type for change: {type(change)}, change: {change}"
                        )
