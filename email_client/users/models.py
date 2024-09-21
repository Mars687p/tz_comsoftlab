from django.contrib.auth.models import User
from django.db import models


class ConfigUser(models.Model):
    """
    Чтобы можно было для одного пользователя создавать несколько
    почтовых ящиков
    """
    name_mail = models.CharField(max_length=64,
                                 null=True,
                                 blank=True)
    name_server = models.CharField(max_length=256)
    username_mail = models.CharField(max_length=256)
    pass_mail = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Почтовый ящик'
        verbose_name_plural = 'Почтовые ящики'

    def __str__(self) -> str:
        return f"{self.name_mail} - {self.user.username}"
