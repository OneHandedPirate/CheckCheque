import datetime
import sqlite3
from pathlib import Path

from config import LABEL
from mail import Mail

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "pokupochki.db"


def get_last_check():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT name, amount, total, created_at
        FROM pokupochki
        WHERE created_at = (SELECT created_at FROM pokupochki ORDER BY 1 DESC LIMIT 1)"""
        )
        _all = cursor.fetchall()

        res = ""
        for item in _all:
            res += f"{item[0][:30]} {item[1]} {item[2]}\n\n"
        return (
            datetime.datetime.strptime(_all[0][3], "%Y-%m-%d %H:%M").strftime(
                "%d.%m.%Y %H:%M"
            ),
            res,
        )


def initial_process(mail: Mail):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS pokupochki (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price DECIMAL(10,2),
            amount DECIMAL(10,3),
            total DECIMAL(10,2),
            created_at TEXT
        );"""
        )

        cursor.executemany(
            """INSERT INTO pokupochki (name, price, amount, total, created_at) VALUES (?, ?, ?, ?, ?)""",
            mail.process_checks("ALL", LABEL),
        )

        conn.commit()


def check_new_checks(mail: Mail):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        new_checks = mail.process_checks("UNSEEN", "Inbox")

        if new_checks:
            cursor.executemany(
                """INSERT INTO pokupochki (name, price, amount, total, created_at) VALUES (?, ?, ?, ?, ?)""",
                new_checks,
            )

            conn.commit()
            return f"{new_checks}"
        else:
            return "Новых чеков нет!"
