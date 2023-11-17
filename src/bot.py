import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from src.config import ALLOWED_USERS, BOT_TOKEN, DB_NAME
from src.services.keyboads import menu_back_ikb, stats_back_ikb, stats_keyboard_ikb
from src.services.main import BotService
from src.services.utils import validate_date_input

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
        **bs.get_menu(
            name=message.from_user.full_name,
            start=True if message.text == "/start" else False,
        )
    )


@dp.callback_query(F.data.startswith("menu_"))
async def menu_callback(query: CallbackQuery, state: FSMContext) -> None:
    menu_item = query.data.split("_")[1]
    match menu_item:
        case "process":
            await query.message.edit_text(
                bs.check_new_checks(), reply_markup=menu_back_ikb.as_markup()
            )
            await state.clear()
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
            await state.clear()
        case "download":
            with open(f"db/{DB_NAME}.db", "rb") as db_from_buffer:
                await query.message.answer_document(
                    BufferedInputFile(db_from_buffer.read(), filename=f"{DB_NAME}.db"),
                    caption="Ваша БД",
                )
            await state.clear()
        case "main":
            await query.message.edit_text(**bs.get_menu(start=False))
            await state.clear()


@dp.callback_query(F.data.startswith("stata_"))
async def stats_callback(query: CallbackQuery):
    period = query.data.split("_")[1]
    await query.message.edit_text(**bs.get_statistics(period, query.from_user.id))


@dp.callback_query(F.data.startswith("page_"))
async def pagination_callback(query: CallbackQuery):
    try:
        page_num = int(query.data.split("_")[1])
        await query.message.edit_text(
            **bs.get_paginated_stats(query.from_user.id, page_num)
        )
    except TelegramBadRequest as e:
        print(e)


@dp.message(DateState.waiting_for_date_input)
async def process_date_input(message: Message, state: FSMContext):
    date_string = message.text
    if validate_date_input(date_string):
        await message.answer(
            **bs.get_custom_statistics(date_string, message.from_user.id),
        )
        await state.clear()
    else:
        await message.answer(
            "❗️Некорректный формат даты❗️\n\n"
            "Попробуйте еще раз или нажмите кнопку Назад для перехода в меню статистики",
            reply_markup=stats_back_ikb.as_markup(),
        )
        await state.set_state(DateState.waiting_for_date_input)


async def main() -> None:
    bs.initial_process()

    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
