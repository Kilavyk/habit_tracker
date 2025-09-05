from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import TelegramUser
from .serializers import TelegramUserSerializer


class TelegramUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления привязкой Telegram аккаунта.

    Endpoints:
        GET /api/telegram/ - получение привязанного Telegram аккаунта
        POST /api/telegram/ - привязка Telegram аккаунта
        PUT /api/telegram/{id}/ - обновление привязки
        DELETE /api/telegram/{id}/ - отвязка Telegram аккаунта

    Permissions:
        - Только аутентифицированные пользователи
        - Доступ только к своим данным
    """

    serializer_class = TelegramUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return TelegramUser.objects.none()

        return TelegramUser.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
