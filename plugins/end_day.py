from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User as TgUser

from domain import User
from pkg import state


async def init(bot):
    @bot.on(events.NewMessage(pattern="/nextday"))
    async def next_day(event: Message) -> None:
        sender: TgUser = await event.get_sender()

        old_user = await state.get().users_repo.get_by_id(sender.id)
        if old_user is None:
            await event.respond(
                "Сначала введите укажите срок и бюджет с помощью /start"
            )
            return

        await stats(event)

        user = old_user.apply_today()
        await state.get().users_repo.update_user(user)

        # FIXME: не отправлять это сообщение если срок кончился
        await event.respond(
            f"Начался новый день. Бюджет на сегодня: **{user.budget_today}**"
        )

    @bot.on(events.NewMessage(pattern="/stats"))
    async def stats(event: Message) -> None:
        sender: TgUser = await event.get_sender()

        user = await state.get().users_repo.get_by_id(sender.id)
        if user is None:
            await event.respond(
                "Сначала введите укажите срок и бюджет с помощью /start"
            )
            return

        await event.respond(stats_for_today(user))


def stats_for_today(user: User) -> str:
    msg = """
**Статистика на день**
------------------

    """

    if user.income_today > 0:
        msg += f"""
**Доходы за сегодня**
+ {user.income_today}
---------------------

        """

    if user.expense_today > 0:
        msg += f"""
**Расходы за сегодня**
- {user.expense_today}
------------------

        """

    msg += f"""
**Остаток на сегодня**
{user.budget_today}
--------------------

    """

    # FIXME: не добавлять эту секцию если остался один день
    msg += f"""
**Бюджет на день**
{user.daily_budget}
--------------

    """

    return msg
