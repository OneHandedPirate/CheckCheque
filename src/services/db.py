import sqlite3
from datetime import datetime
from pathlib import Path

from src.config import DB_NAME

DB_PATH = Path(__file__).resolve().parent.parent / "db" / f"{DB_NAME}.db"


class DBService:
    ItemType = tuple[str, str, str, float, str]

    def __init__(self) -> None:
        self._connection: sqlite3.Connection | None = None
        self._cursor: sqlite3.Cursor | None = None

    def __enter__(self) -> "DBService":
        self._connection = sqlite3.connect(DB_PATH)
        self._cursor = self._connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, trace) -> None:
        self._cursor.close()
        self._connection.close()

    def insert_new_items(
        self, items: list[ItemType], initial: bool = False
    ) -> list[ItemType]:
        with self:
            if initial:
                self._cursor.execute(f"""DROP TABLE IF EXISTS {DB_NAME};""")
                self._cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {DB_NAME} (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    price DECIMAL(10,2),
                    amount DECIMAL(10,3),
                    total DECIMAL(10,2),
                    created_at TEXT
                );"""
                )

            self._insert(items, bulk=True)

            self._connection.commit()

            return items

    @staticmethod
    def _insert_query() -> str:
        return f"""INSERT INTO {DB_NAME} (name, price, amount, total, created_at) VALUES (?, ?, ?, ?, ?)"""

    @staticmethod
    def _week_statistics_query() -> str:
        return f"""
        SELECT name, price, amount, total, created_at
        FROM {DB_NAME} WHERE strftime('%Y-%W', created_at) = strftime('%Y-%W', 'now')"""

    @staticmethod
    def _month_statistics_query() -> str:
        pass

    @staticmethod
    def _year_statistics_query() -> str:
        return f"""SELECT
                    ROUND(SUM(price), 2),
                    COUNT(DISTINCT created_at),
                    strftime('%m', created_at)
                    FROM {DB_NAME}
                    WHERE strftime('%Y', created_at) = ?
                    GROUP BY strftime('%m', created_at);"""

    def _insert(self, items: list[ItemType] | ItemType, bulk: bool = False) -> None:
        if bulk:
            self._cursor.executemany(self._insert_query(), items)
        else:
            self._cursor.execute(self._insert_query(), items)

    def get_week_statistics(self):
        with self:
            self._cursor.execute(self._week_statistics_query())
            return self._cursor.fetchall()

    def get_year_statistics(self):
        with self:
            query = self._year_statistics_query()
            period = (str(datetime.now().year),)
            self._cursor.execute(query, period)
            return self._cursor.fetchall()

    def get_month_statistics(self):
        with self:
            query = """
            SELECT name, SUM(amount), Round(SUM(total), 2)
            FROM pokupochki
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
            GROUP BY name
            ORDER BY 3 DESC;"""
            self._cursor.execute(query)
            return self._cursor.fetchall()
