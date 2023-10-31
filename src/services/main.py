from datetime import datetime

from src.config import DATE_FORMAT, LABEL
from src.services import utils
from src.services.db import DBService
from src.services.mail import MailService


class BotService:
    MONTHS = utils.MONTHS

    def __init__(self):
        self.mail = MailService()
        self.db = DBService()

    def initial_process(self):
        items_from_email = self.mail.process_checks("ALL", LABEL)
        return (
            self.db.insert_new_items(items_from_email, initial=True)
            if items_from_email
            else None
        )

    def check_new_checks(self):
        new_checks = self.mail.process_checks("UNSEEN", "Inbox")
        if new_checks:
            self.db.insert_new_items(new_checks)
            return f"Обработано новых чеков: {len(set([i[4] for i in new_checks]))}"
        else:
            return "Новых чеков нет!"

    def get_year_stats(self):
        res = ""
        year = self.db.get_statistics("year")
        if not year:
            return "В этом году покупок нет"
        for month in year:
            res += f"<b>{self.MONTHS[month[2]]}</b>\nПоходов в магаз: {month[1]}\nПотрачено: {month[0]}\n\n"
        return res

    def get_month_stats(self):
        month = self.db.get_statistics("month")
        if not month:
            return "В этом месяце покупок нет"
        res = f'{self.MONTHS[str(datetime.now().month).rjust(2, "0")]}\n\n'
        summ = 0
        for indx, item in enumerate(month, 1):
            summ += item[2]
            res += f"<b>{item[0]}</b>\nКоличество: {item[1]}\nСумма: {item[2]}\n\n"
        res += f"----------------------------------\n<b>Общая сумма</b>: {summ:.2f}"
        return res

    def get_week_stats(self):
        res = ""
        week = self.db.get_statistics("week")
        if not week:
            return "На этой неделе покупок не было"
        n, summ = 0, 0
        for indx, item in enumerate(week):
            if indx == 0 or indx > 0 and week[indx - 1][4] != item[4]:
                if indx != 0:
                    res += f"------------------\n<b>Сумма: </b> {summ:.2f}\n------------------\n\n"
                    summ = 0
                date, time = item[4].split()
                date = ".".join(date.split("-")[::-1])
                res += f"🗓️ {date}\n🕓 {time}\n\n"
                n = 0

            n += 1
            if item[2] != 1:
                res += f"<b>{n}) {item[0]}</b>\nЦена за ед.: {item[1]}\nКоличество: {item[2]}\nСумма: {item[3]}\n\n"

            else:
                res += f"<b>{n}) {item[0]}</b>\nЦена: {item[3]}\n\n"
            summ += float(item[3])
        res += f"------------------\n<b>Сумма: </b> {summ:.2f}\n------------------\n\n"
        return res

    def get_last_check(self):
        _all = self.db.get_statistics("last")
        if not _all:
            return "Покупок в базе нет :("
        date, time = (
            datetime.strptime(_all[0][4], "%Y-%m-%d %H:%M")
            .strftime(DATE_FORMAT)
            .split()
        )
        res = f"🗓️{date}\n🕓{time}\n\n"
        for item in _all:
            res += f"<b>{item[0]}</b>\nЦена за ед.: {item[1]}\nКоличество: {item[2]}\nСумма: {item[3]}\n\n"
        return res
