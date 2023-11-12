import datetime
import uuid

from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User

import domain
from pkg import state


async def init(bot):
    @bot.on(events.NewMessage(pattern="/start"))
    async def start(event: Message) -> None:
        sender: User = await event.get_sender()
        user = domain.User(
            sender.id,
            datetime.date.today(),
        )

        await state.get().users_repo.add_user(user)

        await event.respond(f"Вы успешно зарегистрированы. Данные: {user}")
