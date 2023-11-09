import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from src.config import ALLOWED_USERS, BOT_TOKEN, DB_NAME
from src.services.keyboads import (
    menu_back_ikb,
    menu_main_ikb,
    stats_back_ikb,
    stats_keyboard_ikb,
)
from src.services.main import BotService

dp = Dispatcher()
bs = BotService()


class DateState(StatesGroup):
    waiting_for_date_input = State()


@dp.message(Command("start", "menu"))
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with /start or /menu command
    """
    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("You are not welcome here!")
    await message.answer(
        bs.get_menu_text(
            name=message.from_user.full_name,
            start=True if message.text == "/start" else False,
        ),
        reply_markup=menu_main_ikb.as_markup(),
    )


@dp.callback_query(F.data.startswith("menu_"))
async def menu_callback(query: CallbackQuery, state: FSMContext) -> None:
    menu_item = query.data.split("_")[1]
    match menu_item:
        case "process":
            await query.message.edit_text(
                bs.check_new_checks(), reply_markup=menu_back_ikb.as_markup()
            )
        case "stats":
            await query.message.edit_text(
                "Нажмите на кнопку для вывода статистики",
                reply_markup=stats_keyboard_ikb.as_markup(),
            )
            await state.set_state(DateState.waiting_for_date_input)
        case "last":
            await query.message.edit_text(
                bs.get_last_check(), reply_markup=menu_back_ikb.as_markup()
            )
        case "download":
            with open(f"db/{DB_NAME}.db", "rb") as db_from_buffer:
                await query.message.answer_document(
                    BufferedInputFile(db_from_buffer.read(), filename=f"{DB_NAME}.db"),
                    caption="Ваша БД",
                )
        case "main":
            await query.message.edit_text(
                bs.get_menu_text(start=False), reply_markup=menu_main_ikb.as_markup()
            )


@dp.callback_query(F.data.startswith("stata_"))
async def stats_callback(query: CallbackQuery):
    period = query.data.split("_")[1]
    await query.message.edit_text(
        bs.get_statistics(period), reply_markup=stats_back_ikb.as_markup()
    )


@dp.message(DateState.waiting_for_date_input)
async def process_stats_input(message: Message, state: FSMContext):
    date_to_parse = message.text
    await message.answer(
        f"Вы ввели: {date_to_parse}", reply_markup=stats_back_ikb.as_markup()
    )
    await state.clear()


async def main() -> None:
    bs.initial_process()

    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
