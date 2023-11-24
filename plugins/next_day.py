from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User as TgUser

from pkg import state
from plugins import stats


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

        await stats.stats(event)

        user = old_user.apply_today()
        await state.get().users_repo.update_user(user)

        # FIXME: не отправлять это сообщение если срок кончился
        await event.respond(
            f"Начался новый день. Бюджет на сегодня: **{user.budget_today}**"
        )
