from rest_framework.pagination import PageNumberPagination


class HabitPaginator(PageNumberPagination):
    """
    Запуск Telegram бота с обработчиком команды /start.

    Features:
        - Асинхронная обработка сообщений
        - Интеграция с Django ORM
        - Обработка ошибок базы данных
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50
