from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import TelegramUser

User = get_user_model()


class TelegramUserTests(APITestCase):
    """Тесты для привязки Telegram аккаунта"""

    def setUp(self):
        self.telegram_list_url = reverse("telegram-list")

        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )

        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

        # Создаем привязанный Telegram аккаунт для user1
        self.telegram_user = TelegramUser.objects.create(
            user=self.user1, chat_id=123456789, telegram_username="user1_telegram"
        )

    def test_get_telegram_user_authenticated(self):
        """Тест получения привязанного Telegram аккаунта"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.telegram_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["chat_id"], 123456789)

    def test_get_telegram_user_no_data(self):
        """Тест получения Telegram аккаунта когда нет привязки"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.telegram_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_telegram_user(self):
        """Тест создания привязки Telegram аккаунта"""
        self.client.force_authenticate(user=self.user2)
        data = {"chat_id": 987654321, "telegram_username": "user2_telegram"}
        response = self.client.post(self.telegram_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TelegramUser.objects.filter(user=self.user2).exists())

    def test_update_telegram_user(self):
        """Тест обновления привязки Telegram аккаунта"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("telegram-detail", kwargs={"pk": self.telegram_user.pk})
        update_data = {"chat_id": 999999999, "telegram_username": "updated_username"}
        response = self.client.put(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.telegram_user.refresh_from_db()
        self.assertEqual(self.telegram_user.chat_id, 999999999)

    def test_delete_telegram_user(self):
        """Тест удаления привязки Telegram аккаунта"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("telegram-detail", kwargs={"pk": self.telegram_user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TelegramUser.objects.filter(user=self.user1).exists())
