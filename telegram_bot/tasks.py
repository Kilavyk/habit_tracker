import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from habits.models import Habit
from telegram_bot.models import TelegramUser


@shared_task
def send_telegram_reminder():
    """
    Фоновая задача для отправки напоминаний о привычках через Telegram.

    Logic:
        - Проверяет привычки каждую минуту
        - Отправляет напоминание, если время привычки совпадает с текущим (±1 минута)
        - Учитывает периодичность привычки
        - Обновляет время последнего напоминания

    Conditions:
        - Привычка должна быть активна
        - Пользователь должен иметь привязанный Telegram аккаунт
        - Не отправляет повторные напоминания в тот же день
    """

    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)
    current_date = now.date()

    habits = Habit.objects.all()

    for habit in habits:
        try:
            # Проверяем, совпадает ли время (с допуском ±1 минута)
            habit_time = habit.time.replace(second=0, microsecond=0)
            time_diff = abs(
                (current_time.hour * 60 + current_time.minute)
                - (habit_time.hour * 60 + habit_time.minute)
            )

            if time_diff > 1:
                continue

            # Проверяем, нужно ли отправлять напоминание сегодня
            if habit.last_reminder_sent:
                last_sent_date = timezone.localtime(habit.last_reminder_sent).date()
                if last_sent_date == current_date:
                    continue

                # Проверяем периодичность
                days_since_last = (current_date - last_sent_date).days
                if days_since_last < habit.frequency:
                    continue

            # Проверяем наличие Telegram пользователя
            try:
                telegram_user = TelegramUser.objects.get(user=habit.user)
                if not telegram_user.chat_id:
                    continue

                # Формируем сообщение для Telegram
                message = (
                    f"🔔 Напоминание о привычке!\n\n"
                    f"Действие: {habit.action}\n"
                    f"Место: {habit.place}\n"
                    f"Время: {habit.time.strftime('%H:%M')}\n"
                    f"Длительность: {habit.duration} секунд"
                )

                # Отправляем сообщение
                response = requests.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    data={"chat_id": telegram_user.chat_id, "text": message},
                    timeout=10,
                )

                if response.status_code == 200:
                    habit.last_reminder_sent = now
                    habit.save()
                else:
                    print(f"Ошибка отправки: {response.status_code} - {response.text}")

            except TelegramUser.DoesNotExist:
                print(f"Telegram пользователь не найден для: {habit.user}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения для {habit.user}: {e}")

        except Exception as e:
            print(f"Ошибка обработки привычки {habit.id}: {e}")

    print("Следующая проверка через минуту.")
