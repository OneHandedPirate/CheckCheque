import os

from dotenv import load_dotenv

load_dotenv()

DATE_FORMAT: str = os.getenv("DATE_FORMAT", "%d.%m.%Y %H:%M")
IMAP_URL: str = os.getenv("IMAP_URL", "imap.gmail.com")
EMAIL: str = os.getenv("EMAIL")
PASSWORD: str = os.getenv("PASSWORD")
LOOKUP_STRING: str = os.getenv("LOOKUP_STRING", "невада")
LABEL: str = os.getenv("LABEL")
BOT_TOKEN: str = os.getenv("BOT_TOKEN")
ALLOWED_USERS: list[int] = list(map(int, os.getenv("ALLOWED_USERS").split(",")))
DB_NAME: str = os.getenv("DB_NAME")
