import dataclasses
import datetime

import loguru
from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User

from domain.models import user
from pkg import state
from pkg.state import SettingsConversationState


async def is_message_settings_change(event: Message) -> bool:
    sender: User = await event.get_sender()

    return sender.id in state.get().conversation_states


async def init(bot):
    return

    @bot.on(events.NewMessage(pattern="/settings"))
    async def settings(event: Message) -> None:
        sender: User = await event.get_sender()

        state.get().conversation_states[
            sender.id
        ] = SettingsConversationState.WAIT_FOR_SUM

        await event.respond(f"Отлично! Введите сумму, которую хотите потратить:")

    @bot.on(events.NewMessage(func=is_message_settings_change))
    async def set_settings(event: Message) -> None:
        sender: User = await event.get_sender()

        conv_states = state.get().conversation_states
        conv_state = conv_states.get(sender.id)

        if conv_state is None:
            raise ValueError(
                "This code should be unreachable. Check file settings.py, either set_settings or "
                "is_message_settings_change works improperly."
            )

        # FIXME кривой костыль, не знаю как пофиксить
        if conv_state == SettingsConversationState.WAIT_FOR_SUM:
            budget = eval(event.text, {}, {})
            new_user = user.User(
                sender.id, period=datetime.date.today(), whole_budget=budget
            )
            conv_state = SettingsConversationState.WAIT_FOR_DATE
            conv_states[sender.id] = conv_state

            # conv_state.new_user = new_user FIXME
            await event.respond(f"Теперь введите дату, до которой планируете траты:")
        elif conv_state == SettingsConversationState.WAIT_FOR_DATE:
            try:
                date = datetime.datetime.strptime(event.text, "%d.%m.%y").date()
                new_user = dataclasses.replace(conv_state.new_user, period=date)
                await state.get().users_repo.insert_user(new_user)
            except Exception as e:
                loguru.logger.error(f"Error: {e}")
                await event.respond(
                    f"Возможно, вы неправильно указали дату. Попробуйте ещё раз:"
                )
