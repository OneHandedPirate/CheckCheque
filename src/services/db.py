import sqlite3
from pathlib import Path

from src.config import DB_NAME

DB_PATH = Path(__file__).resolve().parent.parent / "db" / f"{DB_NAME}.db"


class DBService:
    ItemType = tuple[str, float, float, float, str]

    def __init__(self) -> None:
        self._connection: sqlite3.Connection | None = None
        self._cursor: sqlite3.Cursor | None = None

    def __enter__(self) -> "DBService":
        try:
            self._connection = sqlite3.connect(DB_PATH)
            self._cursor = self._connection.cursor()
        except Exception as e:
            print(f"Error occurred while connecting to the database: {e}")
        return self

    def __exit__(self, exc_type, exc_value, trace) -> None:
        self._cursor.close()
        self._connection.close()

    def insert_new_items(
        self, items: list[ItemType], initial: bool = False
    ) -> list[ItemType]:
        with self:
            try:
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
            except Exception as e:
                print(f"Error occurred while inserting new items: {e}")
                return []

    @staticmethod
    def _insert_query() -> str:
        return f"""INSERT INTO {DB_NAME} (name, price, amount, total, created_at) VALUES (?, ?, ?, ?, ?)"""

    @staticmethod
    def _day_statistics_query() -> str:
        return f"""
        SELECT name, price, amount, total, created_at
        FROM {DB_NAME} WHERE strftime('%Y-%m-%d', created_at) = strftime('%Y-%m-%d', ?)"""

    @staticmethod
    def _week_statistics_query() -> str:
        return f"""
        SELECT name, price, amount, total, created_at
        FROM {DB_NAME} WHERE strftime('%Y-%W', created_at) = strftime('%Y-%W', ?)"""

    @staticmethod
    def _month_statistics_query() -> str:
        return f"""
            SELECT name, SUM(amount), Round(SUM(total), 2), strftime('%m.%Y', created_at)
            FROM {DB_NAME}
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', ?)
            GROUP BY name
            ORDER BY 3 DESC;"""

    @staticmethod
    def _year_statistics_query() -> str:
        return f"""SELECT
                    ROUND(SUM(total), 2),
                    COUNT(DISTINCT created_at),
                    strftime('%m', created_at),
                    strftime('%Y', created_at)
                    FROM {DB_NAME}
                    WHERE strftime('%Y', created_at) = strftime('%Y', ?)
                    GROUP BY strftime('%m', created_at);"""

    @staticmethod
    def _last_check_query() -> str:
        return f"""
        SELECT name, price, amount, total, created_at
        FROM {DB_NAME}
        WHERE created_at = (SELECT MAX(created_at) FROM {DB_NAME});"""

    def _insert(self, items: list[ItemType] | ItemType, bulk: bool = False) -> None:
        if bulk:
            self._cursor.executemany(self._insert_query(), items)
        else:
            self._cursor.execute(self._insert_query(), items)

    def get_statistics(self, period: str, date: str = "now") -> list[tuple] | None:
        with self:
            query = None
            match period:
                case "week":
                    query = self._week_statistics_query()
                case "month":
                    query = self._month_statistics_query()
                case "year":
                    query = self._year_statistics_query()
                case "day":
                    query = self._day_statistics_query()
            try:
                if query:
                    self._cursor.execute(query, (date,))
                res = self._cursor.fetchall()
                if query and res:
                    return res
            except Exception as e:
                print(f"Error occurred while retrieving statistics: {e}")
        return None

    def get_last_check(self) -> list[tuple] | None:
        with self:
            try:
                self._cursor.execute(self._last_check_query())
                res = self._cursor.fetchall()
                if res:
                    return res
            except Exception as e:
                print(f"Error occurred while retrieving statistics: {e}")
        return None
