from datetime import datetime, timedelta

from telethon import events, TelegramClient
from telethon.tl.custom import Message
from telethon.tl.types import User as TgUser

from domain import User
from app import state


async def init(bot):
    return  # FIXME переделать stats_for_today

    @bot.on(events.NewMessage(pattern="/stats"))
    async def stats(event: Message) -> None:
        sender: TgUser = await event.get_sender()

        user = await state.get().users_repo.get_by_id(sender.id)
        if user is None:
            await event.respond(
                "Чтобы использовать бота, зарегистрируйтесть с помощью /start"
            )
            return

        await send_stats(bot, user)


async def send_stats(bot: TelegramClient, user: User) -> None:
    tg_user = TgUser(user.id)
    await bot.send_message(tg_user, stats_for_today(user))


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

    if user.days_left <= 1:
        msg += f"""
**Остаток до {datetime.today + timedelta(user.days_left)}**
{user.remaining_budget - user.expense_today + user.income_today}
---------------------

        """

        msg += f"""
**Бюджет на день**
{user.daily_budget}
--------------

        """

    return msg
