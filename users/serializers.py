from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserLoginSerializer(serializers.Serializer):
    """
    Сериализатор для модели TelegramUser.

    Provides:
        - Сериализация данных Telegram пользователя
        - Автоматическое связывание с текущим пользователем
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        ref_name = "UserLogin"


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Fields:
        username (str): Имя пользователя
        email (str): Email адрес
        password (str): Пароль
        password2 (str): Подтверждение пароля
        first_name (str): Имя
        last_name (str): Фамилия

    Validation:
        - Проверка совпадения паролей
        - Валидация сложности пароля
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения данных пользователя.

    Fields:
        id (int): ID пользователя (read-only)
        username (str): Имя пользователя
        email (str): Email адрес
        first_name (str): Имя
        last_name (str): Фамилия
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class TelegramConnectSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = []
