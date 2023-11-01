from aiogram import Router
from aiogram.types import Message
from aiogram.utils.formatting import Text, Code
from aiogram.filters import Command
from pkg import state

router = Router()


@router.message(Command(commands=["env"]))
async def env(message: Message) -> None:
    if message.from_user is not None and message.from_user.username in state.get().admin_usernames:
        content: Code
        with open('.env', 'r') as f:
            content = Code(f.read())

        await message.answer(**content.as_kwargs())
    else:
        await message.answer(f"Sorry, you are not allowed to use this.")


@router.message(Command(commands=["repo"]))
async def repo(message: Message) -> None:
    await message.answer("github.com/kozlov-ma/monexo")
