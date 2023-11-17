from pprint import pprint

from src.config import LABEL
from src.services import utils
from src.services.db import DBService
from src.services.keyboads import get_stats_page_buttons, menu_main_ikb, stats_back_ikb
from src.services.mail import MailService
from src.services.render import RenderService


class BotService:
    MONTHS = utils.MONTHS

    def __init__(self):
        self.mail = MailService()
        self.db = DBService()
        self.render = RenderService()
        self.pages: dict = {}

    def initial_process(self):
        items_from_email = self.mail.process_checks("ALL", LABEL)
        return (
            self.db.insert_new_items(items_from_email, initial=True)
            if items_from_email
            else None
        )

    def get_menu(self, start: bool, name: str = "default") -> dict:
        return {
            "text": self.render.render_menu_text(start, name),
            "reply_markup": menu_main_ikb.as_markup(),
        }

    def check_new_checks(self) -> str:
        new_items = self.mail.process_checks("UNSEEN", "Inbox")

        if new_items:
            self.db.insert_new_items(new_items)
            return self.render.render_checks(
                items=new_items,
                first_string=f"Обработано новых чеков: {len(set([i[4] for i in new_items]))}\n\n",
            )
        return "Новых чеков нет!"

    def get_statistics(self, period: str, user_id: int) -> str | dict:
        items = self.db.get_statistics(period)
        res = self.render.render_statistics(items, period)
        if isinstance(res, list):
            self.pages[user_id] = res
            return self.get_paginated_stats(user_id)
        return {"text": res, "reply_markup": stats_back_ikb.as_markup()}

    def get_custom_statistics(self, date_string: str, user_id: int) -> str | dict:
        period = date = None
        date_lst = [i.rjust(2, "0") for i in date_string.split(".")]
        match len(date_lst):
            case 3:
                period = "day"
                date = "-".join(date_lst[::-1])
            case 2:
                period = "month"
                date = "-".join(date_lst[::-1] + ["01"])
            case 1:
                period = "year"
                date = "-".join(date_lst[::-1] + (["01"] * 2))
        date += " 00:00"
        items = self.db.get_statistics(period, date)
        res = self.render.render_statistics(items, period)
        if isinstance(res, list):
            self.pages[user_id] = res
            pprint(self.pages)
            return self.get_paginated_stats(user_id)
        return {"text": res, "reply_markup": stats_back_ikb.as_markup()}

    def get_last_check(self):
        items = self.db.get_last_check()
        return self.render.render_checks(items, first_string="🛒 Ваш последний чек:\n\n")

    def get_paginated_stats(self, user_id: int, page: int = 1):
        if not self.pages.get(user_id):
            return {"text": "Страниц нет", "reply_markup": stats_back_ikb.as_markup()}
        return {
            "text": self.pages[user_id][page - 1],
            "reply_markup": get_stats_page_buttons(
                len(self.pages[user_id])
            ).as_markup(),
        }
