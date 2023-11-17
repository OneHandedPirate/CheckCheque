from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

menu_back_ikb = InlineKeyboardBuilder()
menu_back_ikb.add(InlineKeyboardButton(text="Назад", callback_data="menu_main"))

stats_back_ikb = InlineKeyboardBuilder()
stats_back_ikb.add(InlineKeyboardButton(text="Назад", callback_data="menu_stats"))

stats_keyboard_ikb = InlineKeyboardBuilder()
stats_keyboard_ikb.add(
    InlineKeyboardButton(text="Неделя", callback_data="stata_week"),
    InlineKeyboardButton(text="Месяц", callback_data="stata_month"),
    InlineKeyboardButton(text="Год", callback_data="stata_year"),
    InlineKeyboardButton(text="Назад", callback_data="menu_main"),
)

stats_keyboard_ikb.adjust(3, 1)

menu_main_ikb = InlineKeyboardBuilder()
menu_main_ikb.add(
    InlineKeyboardButton(text="Последний чек", callback_data="menu_last"),
    InlineKeyboardButton(text="Статистика", callback_data="menu_stats"),
    InlineKeyboardButton(text="Обработка новых чеков", callback_data="menu_process"),
    InlineKeyboardButton(text="Выгрузка БД", callback_data="menu_download"),
)
menu_main_ikb.adjust(2, 1, 1)


def get_stats_page_buttons(pages: int, current_page: int) -> InlineKeyboardBuilder:
    page_buttons = InlineKeyboardBuilder()
    page_buttons.add(
        *[
            InlineKeyboardButton(text=f"{page}", callback_data=f"page_{page}")
            for page in range(1, pages + 1)
            if page != current_page
        ],
        InlineKeyboardButton(text="Назад", callback_data="menu_stats"),
    )
    page_buttons.adjust(pages - 1, 1)
    return page_buttons
