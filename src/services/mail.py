import email
import imaplib
from datetime import datetime
from email.header import decode_header
from email.message import Message

from bs4 import BeautifulSoup

from src.config import DATE_FORMAT, EMAIL, IMAP_URL, LABEL, LOOKUP_STRINGS, PASSWORD


class MailService:
    def __init__(self) -> None:
        self._email: str = EMAIL
        self._password: str = PASSWORD
        self._connection: imaplib.IMAP4_SSL | None = None

    def __enter__(self) -> "MailService":
        try:
            self._connection = imaplib.IMAP4_SSL(IMAP_URL)
            self._connection.login(self._email, self._password)
        except Exception as e:
            print(f"Error occured while connecting to {self._email}:{e}")
        return self

    def __exit__(self, exc_type, exc_value, trace) -> None:
        self._connection.logout()

    def _select_mailbox(self, mailbox: str) -> None:
        self._connection.select(mailbox)

    def _search(self, criteria: str, folder: str) -> str | bool:
        """
        search for messages matching the given criteria in the given folder
        returns uid-ready concatenated string of email uids or False
        """
        self._select_mailbox(folder)

        status, data = self._connection.uid("search", criteria)
        if status == "OK":
            return ",".join(data[0].decode().split()) if data[0] else False
        return False

    def _fetch(self, uids: str, message_parts: str) -> list | bool:
        status, data = self._connection.uid("fetch", uids, message_parts)
        if status == "OK":
            return data
        return False

    def _add_label(self, uids: str) -> bool:
        typ, response = self._connection.uid("store", uids, "+X-GM-LABELS", LABEL)
        return typ == "OK"

    def _make_seen(self, uids: str) -> bool:
        typ, response = self._connection.uid("STORE", uids, "+FLAGS", "\\Seen")
        return typ == "OK"

    def process_checks(
        self, criteria: str, folder: str = "Inbox"
    ) -> list[tuple] | None | bool:
        """
        search for new checks in Inbox
        returns list of new db-insert-ready items
        """
        res = []
        with self as conn:
            try:
                email_uids = conn._search(criteria, folder)
                if not email_uids:
                    return None

                data = conn._fetch(email_uids, "(BODY.PEEK[])")
                processed_indx = []
                for indx, letter in enumerate(data):
                    if not isinstance(letter, tuple):
                        continue
                    raw_email: bytes = letter[1]
                    email_message = email.message_from_bytes(raw_email)
                    subject = decode_header(email_message["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        decoded_subject = subject.decode().lower()
                        if any(sub in decoded_subject for sub in LOOKUP_STRINGS):
                            processed_indx.append(indx // 2)
                            res += self._parse_email(email_message)
            except Exception as e:
                print(f"Error occurred: {e}")
                return False
            else:
                if processed_indx:
                    processed_uids = ",".join(
                        [email_uids.split(",")[indx] for indx in processed_indx]
                    )
                    if folder == "Inbox":
                        self._add_label(processed_uids)
                    if criteria == "UNSEEN":
                        self._make_seen(processed_uids)
                return res or None

    @staticmethod
    def _parse_email(email_message: Message) -> list[tuple]:
        """
        parse individual email with check
        return list of item tuples or empty list
        """
        res = []
        for part in email_message.get_payload():
            if not part.get_content_type() == "text/html":
                continue
            try:
                html_content = (
                    part.get_payload(decode=True).decode().replace("\r\n", "")
                )
                bs = BeautifulSoup(html_content, "lxml")
                table = bs.find("table", attrs={"cellpadding": "3"})
                date = table.find("td", attrs={"colspan": "2"})
                date_string = " ".join(date.text.split()[-2:])
                dt = datetime.strptime(date_string, DATE_FORMAT)
                formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                all_tr = table.find_all("tr")
                items = [item for item in all_tr if len(item.contents) == 7]
                for item in items:
                    tds = item.find_all("td")
                    name = tds[1].text.strip()
                    price = tds[2].text.strip().replace(",", ".").replace(" ", "")
                    amount = tds[3].text.strip().replace(",", ".")
                    res.append(
                        (
                            name,
                            price,
                            amount,
                            round(float(price) * float(amount), 2),
                            formatted_date,
                        )
                    )
            except Exception as e:
                print(f"Error occurred while parsing email: {e}")
        return res
