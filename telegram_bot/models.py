from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class TelegramUser(models.Model):
    """
    Модель для связи пользователя с Telegram аккаунтом.

    Attributes:
        user (OneToOneField): Связанный пользователь системы
        chat_id (BigIntegerField): ID чата в Telegram
        telegram_username (CharField): Имя пользователя в Telegram
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telegram_user',
        verbose_name=_('пользователь')
    )
    chat_id = models.BigIntegerField(
        _('Telegram Chat ID'),
        null=True,
        blank=True,
        unique=True
    )
    telegram_username = models.CharField(
        _('Telegram username'),
        max_length=255,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Telegram пользователь')
        verbose_name_plural = _('Telegram пользователи')

    def __str__(self):
        return f"{self.user} - {self.telegram_username}"
