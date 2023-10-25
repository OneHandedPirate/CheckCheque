import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from utils import check_new_checks, get_last_check, initial_process

from config import ALLOWED_USERS, BOT_TOKEN
from mail import Mail

dp = Dispatcher()

gmail = Mail()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    if message.chat.id not in ALLOWED_USERS:
        await message.answer("You are not welcome here!")
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        if message.chat.id not in ALLOWED_USERS:
            await message.answer(f"Hello, {message.chat.id}! Access denied")
        else:
            res = get_last_check()
            await message.answer(f"{res[0]}\n\n<code>{res[1]}</code>")
            await message.answer(check_new_checks(gmail))

    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    initial_process(gmail)

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
