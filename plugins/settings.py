import dataclasses

import loguru
from telethon import events
from telethon.tl.custom import Message
from telethon.tl.types import User

import domain
from app import state
from app.state import SettingsConversationState


async def is_message_settings_change(event: Message) -> bool:
    sender: User = await event.get_sender()
    conv_state = state.get().conversation_states.get(sender.id)
    if conv_state is None:
        return False
    elif conv_state == SettingsConversationState.STARTED:
        state.get().conversation_states[
            sender.id
        ] = SettingsConversationState.WAIT_FOR_SUM
        return False
    elif conv_state == SettingsConversationState.ENDED:
        state.get().conversation_states.pop(sender.id)
        return True

    return True


async def init(bot):
    @bot.on(events.NewMessage(pattern="/settings"))
    async def settings(event: Message) -> None:
        sender: User = await event.get_sender()

        state.get().conversation_states[sender.id] = SettingsConversationState.STARTED

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
            try:
                budget = eval(event.text, {}, {})  # TODO проверка на >0
                user: domain.User = await state.get().users_repo.get_by_id(sender.id)
                new_user = dataclasses.replace(
                    user, whole_budget=budget, expense_today=0, income_today=0
                )
                await state.get().users_repo.add_or_update_user(new_user)
                conv_states[sender.id] = SettingsConversationState.WAIT_FOR_DATE
                await event.respond(f"На сколько дней вы планируете бюджет?")
            except Exception as e:
                loguru.logger.exception(f"Error: {e}")
                await event.respond(
                    f"Возможно, вы неправильно указали бюджет. Укажите число, например 1000:"
                )
        elif conv_state == SettingsConversationState.WAIT_FOR_DATE:
            try:
                user: domain.User = await state.get().users_repo.get_by_id(sender.id)
                days = int(event.text)  # TODO добавить проверку на >0
                user = dataclasses.replace(user, days_left=days)
                await state.get().users_repo.add_or_update_user(user)
                state.get().conversation_states[
                    sender.id
                ] = SettingsConversationState.ENDED
                await event.respond(
                    f"Отлично! Задан бюджет **{user.whole_budget}** на **{user.days_left}** дней."  # FIXME не меняется срок для пользователя
                )
            except Exception as e:
                loguru.logger.exception(f"Error: {e}")
                await event.respond(
                    f"Возможно, вы неправильно указали количетство дней. Укажите число, например 7:"
                )
