import dataclasses
import datetime

import loguru
from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User

from domain.models import user
from pkg import state
from pkg.state import SettingsConversationState
import domain

async def is_message_settings_change(event: Message) -> bool:
    sender: User = await event.get_sender()

    return sender.id in state.get().conversation_states


async def init(bot):
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

        if conv_state == SettingsConversationState.WAIT_FOR_SUM:
            budget = eval(event.text, {}, {})
            user: domain.User = await state.get().users_repo.get_by_id(sender.id)
            new_user = dataclasses.replace(user, whole_budget=budget,
                                           expense_today=0, income_today=0)
            await state.get().users_repo.update_user(new_user)
            conv_states[sender.id] = SettingsConversationState.WAIT_FOR_DATE
            await event.respond(f"Теперь введите дату, до которой планируете траты:")
        elif conv_state == SettingsConversationState.WAIT_FOR_DATE:
            try:
                user: domain.User = await state.get().users_repo.get_by_id(sender.id)
                date = datetime.datetime.strptime(event.text, "%d.%m.%y").date()
                new_user = dataclasses.replace(user, period=date)
                await state.get().users_repo.insert_user(new_user)
                state.get().conversation_states.pop(sender.id)
            except Exception as e:
                loguru.logger.error(f"Error: {e}")
                await event.respond(
                    f"Возможно, вы неправильно указали дату. Попробуйте ещё раз:"
                )
