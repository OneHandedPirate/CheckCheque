import sqlite3
from pathlib import Path

from src.config import DB_NAME

DB_PATH = Path(__file__).resolve().parent.parent / "db" / f"{DB_NAME}.db"


class DBService:
    ItemType = tuple[str, str, str, float, str]

    def __init__(self) -> None:
        self.connection: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    def __enter__(self) -> "DBService":
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, trace) -> None:
        self.cursor.close()
        self.connection.close()

    def insert_new_items(
        self, items: list[ItemType], initial: bool = False
    ) -> list[ItemType]:
        with self:
            if initial:
                self.cursor.execute(f"""DROP TABLE IF EXISTS {DB_NAME};""")
                self.cursor.execute(
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

            self.connection.commit()

            return items

    @staticmethod
    def _insert_query() -> str:
        return f"""INSERT INTO {DB_NAME} (name, price, amount, total, created_at) VALUES (?, ?, ?, ?, ?)"""

    @staticmethod
    def _statistics_query() -> str:
        return f"""
        SELECT (name, price, amount, total, created_at)
        FROM {DB_NAME} WHERE strftime(?, created_at) = strftime(?, 'now')"""

    def _insert(self, items: list[ItemType] | ItemType, bulk: bool = False) -> None:
        if bulk:
            self.cursor.executemany(self._insert_query(), items)
        else:
            self.cursor.execute(self._insert_query(), items)

    def get_statistics(self, timespan: str):
        pass
