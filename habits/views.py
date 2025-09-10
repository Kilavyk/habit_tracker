from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Habit
from .paginators import HabitPaginator
from .serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления привычками пользователя.

    Endpoints:
        GET /api/habits/ - список привычек текущего пользователя
        POST /api/habits/ - создание новой привычки
        GET /api/habits/{id}/ - получение конкретной привычки
        PUT /api/habits/{id}/ - полное обновление привычки
        PATCH /api/habits/{id}/ - частичное обновление привычки
        DELETE /api/habits/{id}/ - удаление привычки
        GET /api/habits/public/ - список публичных привычек

    Permissions:
        - Только аутентифицированные пользователи
        - Доступ только к своим привычкам

    Pagination:
        - Размер страницы: 5 элементов
        - Максимальный размер страницы: 50 элементов
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPaginator

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()

        if self.action == "list_public":
            return Habit.objects.filter(is_public=True).order_by("-created_at")
        return Habit.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def public(self, request):

        if getattr(self, "swagger_fake_view", False):
            return Response([])

        public_habits = Habit.objects.filter(is_public=True).order_by("-created_at")
        page = self.paginate_queryset(public_habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(public_habits, many=True)
        return Response(serializer.data)
