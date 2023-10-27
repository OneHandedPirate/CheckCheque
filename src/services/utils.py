import datetime
import sqlite3
from pathlib import Path

from src.config import DATE_FORMAT, DB_NAME, LABEL
from src.services.db import DBService
from src.services.mail import MailService

DB_PATH = Path(__file__).resolve().parent.parent / "db" / f"{DB_NAME}.db"


db = DBService()


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


def statistics(timespan: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = """
        SELECT SUM(total)
        FROM pokupochki
        WHERE strftime(?, created_at) = strftime(?, 'now')
        """

        cursor.execute(query, (timespan, timespan))

        total = cursor.fetchone()[0]

    return f"{total:.2f}"
