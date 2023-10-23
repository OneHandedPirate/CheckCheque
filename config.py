import os

from dotenv import load_dotenv

load_dotenv()

DATE_FORMAT: str = "%d.%m.%Y %H:%M"
IMAP_URL: str = "imap.gmail.com"
EMAIL: str = os.getenv("EMAIL")
PASSWORD: str = os.getenv("PASSWORD")
LOOKUP_STRING: str = "невада"
