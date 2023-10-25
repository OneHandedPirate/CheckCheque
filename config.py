import os

from dotenv import load_dotenv

load_dotenv()

DATE_FORMAT: str = "%d.%m.%Y %H:%M"
IMAP_URL: str = "imap.gmail.com"
EMAIL: str = os.getenv("EMAIL")
PASSWORD: str = os.getenv("PASSWORD")
LOOKUP_STRING: str = "невада"
LABEL: str = "SamberiChecks"
BOT_TOKEN: str = os.getenv("BOT_TOKEN")
ALLOWED_USERS: list[int] = list(map(int, os.getenv("ALLOWED_USERS").split(",")))
