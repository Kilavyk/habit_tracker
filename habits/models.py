from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Habit(models.Model):
    """
    Модель привычки пользователя.

    Attributes:
        user (ForeignKey): Пользователь, создавший привычку
        place (CharField): Место выполнения привычки
        time (TimeField): Время выполнения привычки
        action (CharField): Действие привычки
        is_pleasant (BooleanField): Признак приятной привычки
        linked_habit (ForeignKey): Связанная приятная привычка
        frequency (PositiveIntegerField): Периодичность выполнения (в днях)
        reward (CharField): Вознаграждение за выполнение
        duration (PositiveIntegerField): Время на выполнение (в секундах)
        is_public (BooleanField): Признак публичности привычки
        created_at (DateTimeField): Дата создания привычки
        last_reminder_sent (DateTimeField): Время последнего отправленного напоминания

    Methods:
        clean(): Валидация данных модели
        save(): Сохранение с предварительной валидацией
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name=_("пользователь"),
    )
    place = models.CharField(max_length=255, verbose_name=_("место"))
    time = models.TimeField(verbose_name=_("время"))
    action = models.CharField(max_length=255, verbose_name=_("действие"))
    is_pleasant = models.BooleanField(
        default=False, verbose_name=_("признак приятной привычки")
    )
    linked_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("связанная привычка"),
        limit_choices_to={"is_pleasant": True},
    )
    frequency = models.PositiveIntegerField(
        default=1, verbose_name=_("периодичность (в днях)")
    )
    reward = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("вознаграждение")
    )
    duration = models.PositiveIntegerField(
        verbose_name=_("время на выполнение (в секундах)")
    )
    is_public = models.BooleanField(
        default=False, verbose_name=_("признак публичности")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("дата создания")
    )
    last_reminder_sent = models.DateTimeField(
        verbose_name=_("последнее напоминание отправлено"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("привычка")
        verbose_name_plural = _("привычки")
        ordering = ["-created_at"]

    def clean(self):
        if self.duration > 120:
            raise ValidationError(_("Время выполнения не может превышать 120 секунд."))

        if self.frequency > 7:
            raise ValidationError(_("Периодичность не может быть реже раза в неделю."))

        if self.frequency < 1:
            raise ValidationError(_("Периодичность не может быть меньше 1 дня."))

        if self.is_pleasant and (self.reward or self.linked_habit):
            raise ValidationError(
                _(
                    "У приятной привычки не может быть вознаграждения или связанной привычки."
                )
            )

        if self.reward and self.linked_habit:
            raise ValidationError(
                _("Нельзя одновременно указывать вознаграждение и связанную привычку.")
            )

        if self.linked_habit and not self.linked_habit.is_pleasant:
            raise ValidationError(
                _("В связанные привычки можно добавлять только приятные привычки.")
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}: {self.action} at {self.time}"
