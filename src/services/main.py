from src.config import LABEL
from src.services import utils
from src.services.db import DBService
from src.services.mail import MailService
from src.services.render import RenderService


class BotService:
    MONTHS = utils.MONTHS

    def __init__(self):
        self.mail = MailService()
        self.db = DBService()
        self.render = RenderService()

    def initial_process(self):
        items_from_email = self.mail.process_checks("ALL", LABEL)
        return (
            self.db.insert_new_items(items_from_email, initial=True)
            if items_from_email
            else None
        )

    def get_menu_text(self, start: bool, name: str = "default"):
        return self.render.render_menu_text(start, name)

    def check_new_checks(self) -> str:
        new_items = self.mail.process_checks("UNSEEN", "Inbox")

        if new_items:
            self.db.insert_new_items(new_items)
            return (
                f"Обработано новых чеков: {len(set([i[4] for i in new_items]))}\n\n"
                f"{self.render.render_checks(items=new_items)}"
            )
        return "Новых чеков нет!"

    def get_statistics(self, period: str) -> str:
        items = self.db.get_statistics(period)
        return self.render.render_statistics(items, period)

    def get_last_check(self):
        items = self.db.get_last_check()
        return self.render.render_checks(items)
