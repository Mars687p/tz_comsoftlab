import json
import time

from channels.generic.websocket import WebsocketConsumer
from users.models import ConfigUser

from .models import FilesModel, MessageModel
from .services import ImapClient, MessageDict


class ProgressBarConsumer(WebsocketConsumer):
    def connect(self) -> None:
        self.user = self.scope["user"]
        self.accept()
        self.send_run_progress()

    def send_progress_msg(self, msg,
                          progress, content: dict | None = None) -> None:
        self.send(text_data=json.dumps(
                    {
                        "type": "progress",
                        "message": msg,
                        "progress": progress,
                        "content": content,
                    }
                ))

    def send_run_progress(self) -> None:
        object_list = MessageModel.get_queryset(self.user.id)
        mail_boxes = ConfigUser.objects.filter(user__id=self.user.id)
        for mail in mail_boxes:
            imap_client = ImapClient(mail.username_mail,
                                     mail.pass_mail,
                                     mail.name_server,
                                     mail,
                                     )
            first_obj = object_list.first()
            if first_obj:
                imap_client.last_uid = first_obj.uid
            imap_client.auth_mail()
            imap_client.get_list_uid_message()
            self.add_new_messages(imap_client)

    def add_new_messages(self, imap_client: ImapClient) -> None:
        last_index_msg = imap_client.search_last_msg()
        messages_uids = set()
        len_mails = len(imap_client.list_uids)
        if not last_index_msg:
            last_index_msg = -1
            messages_uids = set(i['uid'] for i in MessageModel.objects.values('uid'))
            self.send_progress_msg(f'Проверено 1/{len_mails}', 0)
        else:
            self.send_progress_msg('Письмо найдено', 0)

        time.sleep(1)
        for index, uid in enumerate(
                            imap_client.list_uids[last_index_msg+1:],
                            len_mails - len(imap_client.list_uids[last_index_msg+1:])+1):
            if uid in messages_uids:
                self.send_progress_msg(
                        f'Проверено {index}/{len_mails}', 0)
                continue

            data: MessageDict = imap_client.get_message(str(uid))
            msg = MessageModel.objects.create(
                            title=data['title_msg'],
                            send_time=data['send_time'],
                            recieve_time=data['recieve_time'],
                            body=data['body'],
                            uid=uid,
                            config_user=imap_client.config_user
                            )
            for file in data['files']:
                FilesModel.objects.create(name=file, message=msg)

            self.send_progress_msg(
                        f'Добавлено {index}/{len_mails}',
                        int(index/len_mails * 100),
                        dict(
                            title=msg.title or 'Без темы',
                            body=msg.get_short_body(),
                            send_time=msg.send_time.strftime('%Y-%b-%d  %H:%M:%S %z'),
                            recieve_time=msg.recieve_time.strftime('%Y-%b-%d  %H:%M:%S %z'),
                            files=data['files'],
                            config_user=msg.config_user.__str__(),
                            )
                        )
            time.sleep(.5)

        self.send_progress_msg('Все письма добавлены', 100)
