import datetime
import sqlite3
from pathlib import Path

from src.config import DATE_FORMAT, DB_NAME, LABEL
from src.services.db import DBService
from src.services.mail import MailService

DB_PATH = Path(__file__).resolve().parent.parent / "db" / f"{DB_NAME}.db"


db = DBService()

months = {
    "01": "❄️ Январь",
    "02": "🌨 Февраль",
    "03": "🌷 Март",
    "04": "🌺 Апрель",
    "05": "🌻 Май",
    "06": "🍹 Июнь",
    "07": "👙 Июль",
    "08": "🏖 Август",
    "09": "🍁 Сентябрь",
    "10": "🎃 Октябрь",
    "11": "☕ Ноябрь",
    "12": "🎄 Декабрь",
}


def get_last_check():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT name, price, amount, total, created_at
        FROM pokupochki
        WHERE created_at = (SELECT MAX(created_at) FROM pokupochki)"""
        )
        _all = cursor.fetchall()

        res = ""
        for item in _all:
            res += f"<b>{item[0]}</b>\nЦена за ед.: {item[1]}\nКоличество: {item[2]}\nСумма: {item[3]}\n\n"
        return (
            datetime.datetime.strptime(_all[0][4], "%Y-%m-%d %H:%M").strftime(
                DATE_FORMAT
            ),
            res,
        )


def initial_process(mail: MailService):
    items_from_email = mail.process_checks("ALL", LABEL)
    return (
        db.insert_new_items(items_from_email, initial=True)
        if items_from_email
        else None
    )


def check_new_checks(mail: MailService):
    new_checks = mail.process_checks("UNSEEN", "Inbox")
    if new_checks:
        db.insert_new_items(new_checks)
        return f"Обработано новых чеков: {len(set([i[4] for i in new_checks]))}"
    else:
        return "Новых чеков нет!"


def year_stats():
    res = ""
    year = db.get_year_statistics()
    for month in year:
        res += f"<b>{months[month[2]]}</b>\nПоходов в магаз: {month[1]}\nПотрачено: {month[0]}\n\n"
    return res


def month_stats():
    month = db.get_month_statistics()
    res = f'{months[str(datetime.datetime.now().month).rjust(2, "0")]}\n\n'
    summ = 0
    for indx, item in enumerate(month, 1):
        summ += item[2]
        res += f"<b>{item[0]}</b>\nКоличество: {item[1]}\nСумма: {item[2]}\n\n"
    res += f"-----------------------------\n<b>Общая сумма</b>: {summ:.2f}"
    return res


def week_stats():
    res = ""
    week = db.get_week_statistics()
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
