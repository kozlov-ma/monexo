import re

from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User

from pkg import state

MATH_REGEX = re.compile(r"(?!.*([^\d\s])(?:.*\1))(^[\-\+\*\(\)\/\d\s.]+$)", re.A)
SINGLE_OPERAND_REGEX = re.compile(f"[\+\-]\d+$", re.A)


async def init(bot):
    @bot.on(events.NewMessage(pattern=MATH_REGEX))
    async def budget_change(event: Message) -> None:
        sender: User = await event.get_sender()

        user = await state.get().users_repo.get_by_id(sender.id)

        if user is None:
            await event.respond(
                "Чтобы использовать бота, зарегистрируйтесь с помощью /start"
            )
            return

        try:
            result = eval(event.text, {}, {})
            if SINGLE_OPERAND_REGEX.match(event.text):
                new_user = None

                if result > 0:
                    new_user = user.add_income(result)
                else:
                    new_user = user.add_expense(abs(result))

                action = "Потрачено" if result < 0 else "Добавлено"
                await state.get().users_repo.update_user(new_user)

                await event.respond(
                    f"{action} {abs(result)}, теперь остаток на сегодня {new_user.budget_today}."
                )
            elif result < 0:
                await event.respond(
                    f"Введена отрицательная сумма: **{result}**. Если хотите потратить деньги, введите положительное "
                    f"число, например **{abs(result)}**"
                )
            else:
                new_user = user.add_expense(result)

                await state.get().users_repo.update_user(new_user)

                await event.respond(
                    f"Потрачено {result}, остаток на сегодня {new_user.budget_today}. До {new_user.period} осталось {new_user.whole_budget - new_user.expense_today}"
                )

        except Exception as e:
            await event.respond(f"Выражение содержит ошибку {e}.")
