import os
import django
from django.conf import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp
import async_timeout
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


async def send_telegram_message_async(chat_id, text):
    """
    Асинхронная отправка сообщения в Telegram.

    Args:
        chat_id (int): ID чата получателя
        text (str): Текст сообщения

    Returns:
        bool: True если отправка успешна, False в случае ошибки
    """

    try:
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(10):
                async with session.post(
                        f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                        data={'chat_id': chat_id, 'text': text}
                ) as response:
                    return response.status == 200
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")
        return False


async def handle_start_command_async(chat_id, username):
    """
    Асинхронная отправка сообщения в Telegram.

    Args:
        chat_id (int): ID чата получателя
        text (str): Текст сообщения

    Returns:
        bool: True если отправка успешна, False в случае ошибки
    """

    from users.models import User
    from telegram_bot.models import TelegramUser

    try:
        # Убираем @ если есть
        if username.startswith('@'):
            username = username[1:]
        username = username.strip()

        # Асинхронно получаем пользователя
        try:
            user = await sync_to_async(User.objects.get)(username=username)
        except User.DoesNotExist:
            await send_telegram_message_async(chat_id, f"❌ Пользователь '{username}' не найден. Проверьте username.")
            return False

        # Пытаемся создать или обновить запись
        try:
            telegram_user, created = await sync_to_async(
                TelegramUser.objects.update_or_create
            )(
                user=user,
                defaults={'chat_id': chat_id, 'telegram_username': username}
            )

            if created:
                message = f"✅ Аккаунт привязан! Вы будете получавать напоминания о привычках."
            else:
                message = f"✅ Аккаунт перепривязан! Теперь вы будете получать напоминания."

            await send_telegram_message_async(chat_id, message)
            return True

        except Exception as db_error:
            # Общая обработка ошибок базы данных
            print(f"Ошибка в базе данных: {db_error}")

            # Пробуем получить существующую запись и обновить её
            try:
                existing = await sync_to_async(TelegramUser.objects.get)(chat_id=chat_id)
                existing.user = user
                existing.telegram_username = username
                await sync_to_async(existing.save)()

                message = f"✅ Аккаунт перепривязан! Теперь вы будете получать напоминания."
                await send_telegram_message_async(chat_id, message)
                return True
            except Exception as e:
                print(f"Ошибка при обновлении существующей записи: {e}")
                await send_telegram_message_async(chat_id, "❌ Ошибка привязки. Попробуйте позже.")
                return False

    except Exception as e:
        print(f"Ошибка в функции handle_start_command_async: {e}")
        await send_telegram_message_async(chat_id, "❌ Ошибка привязки. Попробуйте позже.")
        return False


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start для Telegram бота.

    Usage:
        /start username - привязка аккаунта

    Args:
        update: Объект обновления Telegram
        context: Контекст выполнения команды
    """

    if context.args:
        username = context.args[0]
        await handle_start_command_async(update.effective_chat.id, username)
    else:
        await update.message.reply_text("❌ Используйте: /start ваш_username")


def run_bot():
    """
    Запуск Telegram бота с обработчиком команды /start.

    Features:
        - Асинхронная обработка сообщений
        - Интеграция с Django ORM
        - Обработка ошибок базы данных
    """
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))

    print("🤖 Запускаем бота с python-telegram-bot...")
    application.run_polling()


if __name__ == '__main__':
    run_bot()
