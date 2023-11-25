import asyncio

import loguru
from telethon import events, TelegramClient
from telethon.tl.custom import Message
from telethon.tl.types import User as TgUser
from domain import User

from pkg import state
from plugins import stats


async def init(bot: TelegramClient):
    @bot.on(events.NewMessage(pattern="/nextday"))
    async def next_day(event: Message) -> None:
        sender: TgUser = await event.get_sender()

        user = (await state.get().users_repo.get_by_id(sender.id)).ok().value
        if user is None:
            await event.respond(
                "Сначала введите укажите срок и бюджет с помощью /start"
            )
            return

        await next_day_for(bot, user)

    asyncio.create_task(update_users_periodically(bot, 24 * 60 * 60))


async def update_users_periodically(bot: TelegramClient, duration_secs: float) -> None:
    await asyncio.sleep(duration_secs)
    tasks = []

    users_result = await state.get().users_repo.get_all()

    if users_result.is_err:
        return

    for user in users_result.ok().value:
        tasks.append(next_day_for(bot, user))

    await asyncio.gather(*tasks)

    loguru.logger.info(f"Updated all users, next update in {duration_secs} seconds.")


async def next_day_for(bot: TelegramClient, user: User) -> None:
    tg_user = TgUser(user.id)

    await stats.send_stats(bot, user)

    user = user.apply_today()
    await state.get().users_repo.update_user(user)

    # FIXME: не отправлять это сообщение если срок кончился
    await bot.send_message(
        tg_user, f"Начался новый день. Бюджет на сегодня: **{user.budget_today}**"
    )
