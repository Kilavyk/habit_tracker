import os
from celery import Celery
from django.conf import settings

# Установка переменной окружения для настроек проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создание экземпляра объекта Celery
app = Celery('config')

# Загрузка настроек из файла Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение и регистрация задач из файлов tasks.py в приложениях Django
app.autodiscover_tasks()

app.conf.timezone = settings.TIME_ZONE

app.conf.beat_schedule = {
    'send-telegram-reminders': {
        'task': 'telegram_bot.tasks.send_telegram_reminder',
        'schedule': 60.0,  # Каждые 1 минут
    },
}