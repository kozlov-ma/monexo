from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User


async def init(bot):
    @bot.on(events.NewMessage(pattern="/help"))
    async def hello(event: Message) -> None:
        sender: User = await event.get_sender()
        help_msg = """
**Введение**
- Зарегистрируйтесь и начните работу с ботом с помощью /start
- Чтобы указать изначальные параметры срока и бюджета, используйте /settings

**Доходы и расходы**
- Чтобы записать трату, просто отправьте боту число, например 1000
- Можно также использовать арифметические выражения, например 1000 + 500 или 10 * 2
- Чтобы записать доход, используйте число со знаком '+', например +1000

**Что дальше?**
- Посмотреть статистику на сегодня можно с помощью /stats
- Каждые 24 часа бот будет сообщать вам о текущем состоянии бюджета и давать статистику за прошедший день
- Это сообщение можно показать ещё раз с помощью /help
"""
        await event.respond(help_msg)
