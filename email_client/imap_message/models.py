from django.db import models
from django.db.models.query import QuerySet
from users.models import ConfigUser


class MessageModel(models.Model):
    title = models.CharField('Тема письма',
                             max_length=256,
                             null=True,
                             blank=True)
    send_time = models.DateTimeField('Дата отправки')
    recieve_time = models.DateTimeField('Дата получения')
    body = models.TextField('Текст сообщения',
                            null=True,
                            blank=True)
    uid = models.IntegerField('uid')
    config_user = models.ForeignKey(ConfigUser,
                                    verbose_name='Почтовый клиент',
                                    on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Письмо'
        verbose_name_plural = 'Письма'
        ordering = ['-uid']

    def __str__(self) -> str:
        return f'Письмо: {self.title if self.title is not None else "Без темы"}'

    @staticmethod
    def get_queryset(user_id: int,
                     client_id: int | None = None) -> QuerySet:
        if client_id is None:
            message_quereyset = MessageModel.objects.filter(
                            config_user__user__id=user_id
                ).prefetch_related('filesmodel_set').select_related('config_user')
        else:
            message_quereyset = MessageModel.objects.filter(
                config_user__id=client_id
                ).prefetch_related('filesmodel_set').select_related('config_user')
        return message_quereyset

    def get_short_body(self) -> str:
        if self.body:
            return ' '.join(self.body.split(' ')[:10]) + ' ...'
        else:
            return ''


class FilesModel(models.Model):
    name = models.CharField(max_length=256)
    message = models.ForeignKey(
                            MessageModel,
                            null=True,
                            blank=True,
                            on_delete=models.CASCADE)
