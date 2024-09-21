import base64
import binascii
import email
import email.message
import imaplib
import os
from contextlib import suppress
from datetime import datetime
from email.header import decode_header
from typing import Optional, TypedDict

from bs4 import BeautifulSoup
from pandas import to_datetime
from users.models import ConfigUser

from email_client.settings import BASE_DIR


class MessageDict(TypedDict):
    title_msg: Optional[str]
    send_time: datetime
    recieve_time: datetime
    body: str
    files: list[str]


class ImapClient:
    def __init__(self,
                 username: str,
                 password: str,
                 name_server: str,
                 config_user: ConfigUser,
                 last_uid: Optional[int] = None) -> None:
        self.username = username
        self.password = password
        self.name_server = name_server
        self.config_user = config_user
        self.last_uid = last_uid
        self.list_uids: Optional[list[int]] = None
        self.connect: Optional[imaplib.IMAP4_SSL] = None

    def auth_mail(self) -> bool:
        self.connect = imaplib.IMAP4_SSL(self.name_server)
        self.connect.login(self.username, self.password)
        return True

    def get_message(self, uid: str | bytes) -> MessageDict:
        _, msg = self.connect.uid('fetch', uid, '(RFC822)')
        msg = email.message_from_bytes(msg[0][1])
        if msg["Subject"] is None:
            title_msg = None
        else:
            header = decode_header(msg["Subject"])[0][0]
            title_msg = self._get_decode_str(header)
        send_time = to_datetime(msg['Date'])
        recieve_time = to_datetime(msg['Received'].split('; ')[1])

        files = []
        body_msg = None
        if msg.is_multipart():
            path = f'{BASE_DIR}/media/{self.config_user.id}/'
            with suppress(FileExistsError):
                os.makedirs(path)
            for part in msg.walk():
                if part.get_content_disposition() != 'attachment':
                    continue
                file_name = decode_header(part.get_filename())[0][0]
                file_name = self._get_decode_str(file_name)
                if file_name:
                    with open(path + file_name, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    files.append(file_name)
        else:
            body_msg = msg.get_payload(decode=True)
            with suppress(UnicodeDecodeError, binascii.Error):
                body_msg = base64.b64decode(body_msg).decode()
            body_msg = self._get_decode_str(body_msg)

            if msg.get_content_subtype() == 'html':
                soup = BeautifulSoup(body_msg, 'lxml')

                body_msg = soup.get_text()
                body_msg = ' '.join(body_msg.split())

        return MessageDict({
                    'title_msg': title_msg,
                    'body': body_msg,
                    'send_time': send_time,
                    'recieve_time': recieve_time,
                    'files': files
        })

    def _get_decode_str(self, string: bytes | str) -> str:
        if type(string) is str:
            return string
        else:
            return string.decode()

    def search_last_msg(self) -> Optional[int]:
        if not self.last_uid or not self.list_uids:
            return None
        start_elem = 0
        end_elem = len(self.list_uids) - 1
        while start_elem <= end_elem:
            elem_mid = start_elem + (end_elem - start_elem) // 2
            if self.list_uids[elem_mid] > self.last_uid:
                end_elem = elem_mid - 1
            elif self.list_uids[elem_mid] < self.last_uid:
                start_elem = elem_mid + 1
            else:
                return elem_mid
        return None

    def get_list_uid_message(self) -> list[int]:
        self.connect.select('INBOX')
        resp = self.connect.uid('search', "ALL")[1][0].split()
        self.list_uids = [int(i.decode()) for i in resp]
        return self.list_uids
