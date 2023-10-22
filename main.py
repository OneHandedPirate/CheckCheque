import time
import os
import imaplib
import email
import sqlite3
from datetime import datetime
from email.header import decode_header
from sqlite3 import Connection, Cursor

from dotenv import load_dotenv
from bs4 import BeautifulSoup


load_dotenv()

db_connection: Connection = sqlite3.connect('pokupochki.db')

cursor: Cursor = db_connection.cursor()


DATE_FORMAT: str = '%d.%m.%Y %H:%M'
IMAP_URL: str = 'imap.gmail.com'
EMAIL: str = os.getenv('EMAIL')
PASSWORD: str = os.getenv('PASSWORD')

gmail_connection: imaplib.IMAP4_SSL = imaplib.IMAP4_SSL(IMAP_URL)

gmail_connection.login(EMAIL, PASSWORD)


# Search for new checks (Unseen) in Inbox
gmail_connection.select('Inbox')
typ, data = gmail_connection.search(None, 'UNSEEN')
if data[0]:
    email_ids = data[0].split()
    for email_id in email_ids:
        typ, msg_data = gmail_connection.fetch(email_id, '(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg_header = response_part[1].decode('utf-8')
                decoded_subject = decode_header(msg_header)[1][0]
                if isinstance(decoded_subject, bytes):
                    decoded_subject = decoded_subject.decode('utf-8')
                if 'невада' in decoded_subject.lower():
                    print(f'Письмо найдено! Его заголовок: {decoded_subject}')
                    typ, response = gmail_connection.store(email_id, '+X-GM-LABELS', 'SamberiChecks')

time.sleep(5)


# Search for unprocessed checks in SamberiChecks folder

gmail_connection.select('SamberiChecks')


typ, data = gmail_connection.search(None, 'UNSEEN')

mail_id_list = data[0].decode().split()


for num in mail_id_list:
    typ, data = gmail_connection.fetch(num, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)

    if email_message.is_multipart():
        for part in email_message.get_payload():
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True).decode().replace('\r\n', '')
    else:
        if email_message.get_content_type() == "text/html":
            html_content = email_message.get_payload(decode=True).decode().replace('\r\n', '')

    bs = BeautifulSoup(html_content, 'lxml')
    table = bs.find('table', attrs={'cellpadding': "3"})

    date = table.find('td', attrs={'colspan': '2'})
    date_string = ' '.join(date.text.split()[-2:])
    dt = datetime.strptime(date_string, DATE_FORMAT)
    formatted_date = dt.strftime("%Y-%m-%d")

    items = table.find_all('tr')
    filtered_items = [item for item in items if len(item.contents) == 7]
    for item in filtered_items:
        tds = item.find_all('td')
        name = tds[1].text.strip()
        price = tds[2].text.strip().replace(',', '.')
        amount = tds[3].text.strip().replace(',', '.')
        print(name, price, amount)
        cursor.execute("""INSERT INTO pokupochki (name, price, amount, created_at) VALUES (?, ?, ?, ?)""", (name, price, amount, formatted_date))
    gmail_connection.store(num, '+FLAGS', '\\Seen')

db_connection.commit()
db_connection.close()
gmail_connection.logout()
