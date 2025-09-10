from rest_framework import serializers

from .models import TelegramUser


class TelegramUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели TelegramUser.

    Provides:
        - Сериализация данных Telegram пользователя
        - Автоматическое связывание с текущим пользователем
    """

    class Meta:
        model = TelegramUser
        fields = ["chat_id", "telegram_username"]
        read_only_fields = ["user"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
