from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User

from pkg import state


async def init(bot):
    @bot.on(events.NewMessage(pattern="/env"))
    async def env(event: Message) -> None:
        sender: User = await event.get_sender()
        if sender is not None and sender.username in state.get().admin_usernames:
            content: str
            with open(".env", "r") as f:
                nl = "\n"
                content = f"```{nl}{f.read()}{nl}```"

            await event.respond(content)
        else:
            await event.respond(f"Sorry, you are not allowed to use this.")

    @bot.on(events.NewMessage(pattern="/repo"))
    async def repo(event: Message) -> None:
        await event.respond("github.com/kozlov-ma/monexo")
