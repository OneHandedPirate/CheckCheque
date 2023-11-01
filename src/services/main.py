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

    def get_menu(self, start: bool, name: str = "default"):
        return self.render.render_menu(start, name)

    def check_new_checks(self):
        new_checks = self.mail.process_checks("UNSEEN", "Inbox")

        if new_checks:
            self.db.insert_new_items(new_checks)
            return f"Обработано новых чеков: {len(set([i[4] for i in new_checks]))}"
        return "Новых чеков нет!"

    def get_statistics(self, period: str) -> str:
        items = self.db.get_statistics(period)
        return self.render.render_statistics(items, period)
