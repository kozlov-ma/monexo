from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User


async def init(bot):
    @bot.on(events.NewMessage(pattern="/hello"))
    async def hello(event: Message) -> None:
        sender: User = await event.get_sender()
        await event.respond(f"Hello, {sender.username}!")
