from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Модель для связи пользователя с Telegram аккаунтом.

    Attributes:
        user (OneToOneField): Связанный пользователь системы
        chat_id (BigIntegerField): ID чата в Telegram
        telegram_username (CharField): Имя пользователя в Telegram
    """

    email = models.EmailField(_("email address"), unique=True, blank=False, null=False)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username
