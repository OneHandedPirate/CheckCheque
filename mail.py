import email
import imaplib
from datetime import datetime
from email.header import decode_header
from email.message import Message

from bs4 import BeautifulSoup

from config import DATE_FORMAT, EMAIL, IMAP_URL, LOOKUP_STRING, PASSWORD


class MailConnection:
    def __init__(self):
        self.email: str = EMAIL
        self.password: str = PASSWORD
        self.connection: imaplib.IMAP4_SSL | None = None

    def __enter__(self):
        self._login()
        return self

    def __exit__(self, exc_type, exc_value, trace):
        self._logout()

    def _login(self):
        self.connection = imaplib.IMAP4_SSL(IMAP_URL)
        self.connection.login(self.email, self.password)

    def _logout(self):
        self.connection.logout()

    def _select_mailbox(self, mailbox: str):
        self.connection.select(mailbox)

    def _search(self, criteria: str, mailbox="Inbox"):
        """Returns concatenated string of email uids ready to be put into fetch"""
        self._select_mailbox(mailbox)

        status, data = self.connection.uid("search", criteria)
        if status == "OK":
            return ",".join(data[0].decode().split()) if data[0] else None
        return

    def _fetch(self, uids: str, message_parts: str):
        status, data = self.connection.uid("fetch", uids, message_parts)
        if status == "OK":
            return data
        return

    def _change_seen_status(self, uids: str, status: bool):
        typ, response = self.connection.uid(
            "store", uids, f"{'+' if status else '-'}X-GM-LABELS", "SamberiChecks"
        )
        return typ

    def process_new_checks(self) -> list[tuple] | None:
        """
        search for new checks in Inbox
        returns list of new db-insert-ready items
        """
        res = []
        with self as conn:
            email_uids = conn._search("UNSEEN")
            if email_uids:
                data = conn._fetch(email_uids, "(BODY.PEEK[])")
                for letter in data:
                    if isinstance(letter, tuple):
                        raw_email: bytes = letter[1]
                        email_message = email.message_from_bytes(raw_email)
                        decoded_subject = decode_header(email_message["Subject"])[0][0]
                        if (
                            isinstance(decoded_subject, bytes)
                            and LOOKUP_STRING in decoded_subject.decode().lower()
                        ):
                            res += self._process_check(email_message)

        return res if res else None

    @staticmethod
    def _process_check(email_message: Message) -> list[tuple]:
        """
        Process individual email with check
        return list of tuples with items
        """
        res = []

        for part in email_message.get_payload():
            if part.get_content_type() == "text/html":
                html_content: str = (
                    part.get_payload(decode=True).decode().replace("\r\n", "")
                )
                bs = BeautifulSoup(html_content, "lxml")
                table = bs.find("table", attrs={"cellpadding": "3"})
                date = table.find("td", attrs={"colspan": "2"})
                date_string = " ".join(date.text.split()[-2:])
                dt = datetime.strptime(date_string, DATE_FORMAT)
                formatted_date = dt.strftime("%Y-%m-%d")

                items = table.find_all("tr")
                filtered_items = [item for item in items if len(item.contents) == 7]
                for item in filtered_items:
                    tds = item.find_all("td")
                    name = tds[1].text.strip()
                    price = tds[2].text.strip().replace(",", ".")
                    amount = tds[3].text.strip().replace(",", ".")
                    res.append((name, price, amount, formatted_date))
        return res
