import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, Message
from aiogram.utils.markdown import hbold

from src.config import ALLOWED_USERS, BOT_TOKEN
from src.services.main import BotService

dp = Dispatcher()

bs = BotService()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("You are not welcome here!")
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message(Command("last"))
async def last_check_handler(message: types.Message) -> None:
    try:
        if message.from_user.id not in ALLOWED_USERS:
            await message.answer(f"Hello, {message.from_user.id}! Access denied")
        else:
            await message.reply(bs.get_last_check())

    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


@dp.message(Command("process"))
async def process_new_checks(message: types.Message) -> None:
    try:
        if message.from_user.id not in ALLOWED_USERS:
            await message.answer(f"Hello, {message.from_user.id}! Access denied")
        else:
            await message.reply(bs.check_new_checks())

    except TypeError:
        await message.answer("Nice try!")


@dp.message(Command("down"))
async def download_db(message: types.Message) -> None:
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer(f"Hello, {message.from_user.id}! Access denied")
    else:
        with open("db/pokupochki.db", "rb") as db_from_buffer:
            await message.answer_document(
                BufferedInputFile(db_from_buffer.read(), filename="pokupochki.db"),
                caption="БД из буфера",
            )


@dp.message(Command("year"))
async def year(message: types.Message) -> None:
    try:
        if message.from_user.id not in ALLOWED_USERS:
            await message.answer(f"Hello, {message.from_user.id}! Access denied")
        else:

            await message.reply(bs.get_year_stats())

    except TypeError:
        await message.answer("Nice try!")


@dp.message(Command("week"))
async def week(message: types.Message) -> None:
    try:
        if message.from_user.id not in ALLOWED_USERS:
            await message.answer(f"Hello, {message.from_user.id}! Access denied")
        else:
            await message.reply(bs.get_week_stats())

    except TypeError:
        await message.answer("Nice try!")


@dp.message(Command("month"))
async def month(message: types.Message) -> None:
    try:
        if message.from_user.id not in ALLOWED_USERS:
            await message.answer(f"Hello, {message.from_user.id}! Access denied")
        else:
            await message.reply(bs.get_month_stats())

    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    bs.initial_process()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
