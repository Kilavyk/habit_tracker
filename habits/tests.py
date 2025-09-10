from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Habit

User = get_user_model()


class HabitCRUDTests(APITestCase):
    """Тесты CRUD операций для привычек"""

    def setUp(self):
        self.habits_list_url = reverse("habits-list")
        self.public_habits_url = reverse("public-habits")

        # Создаем пользователей
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )

        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

        # Создаем тестовые привычки
        self.habit1 = Habit.objects.create(
            user=self.user1,
            place="Дом",
            time="08:00:00",
            action="Утренняя зарядка",
            duration=60,  # 1 минута
            frequency=1,
            is_public=True,
        )

        self.habit2 = Habit.objects.create(
            user=self.user1,
            place="Парк",
            time="18:00:00",
            action="Вечерняя пробежка",
            duration=120,  # 2 минуты
            frequency=2,
            is_public=False,
        )

        self.habit3 = Habit.objects.create(
            user=self.user2,
            place="Спортзал",
            time="19:00:00",
            action="Тренировка",
            duration=90,  # 1.5 минуты
            frequency=3,
            is_public=True,
        )

        # Данные для создания новой привычки
        self.valid_habit_data = {
            "place": "Офис",
            "time": "12:00:00",
            "action": "Обеденная прогулка",
            "duration": 60,  # 1 минута
            "frequency": 1,
            "is_public": True,
        }

        self.invalid_habit_data = {
            "place": "Офис",
            "time": "12:00:00",
            "action": "Обеденная прогулка",
            "duration": 300,  # > 120 секунд - должно вызвать ошибку
            "frequency": 8,  # > 7 дней - должно вызвать ошибку
            "is_public": True,
        }

    def test_get_habits_authenticated(self):
        """Тест получения списка привычек аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.habits_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # Только привычки user1

    def test_get_habits_unauthenticated(self):
        """Тест получения списка привычек неаутентифицированным пользователем"""
        response = self.client.get(self.habits_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_public_habits(self):
        """Тест получения списка публичных привычек"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.public_habits_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        public_habits = [
            habit for habit in response.data["results"] if habit["is_public"]
        ]
        self.assertEqual(len(public_habits), len(response.data["results"]))

    def test_create_habit_valid_data(self):
        """Тест создания привычки с валидными данными"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.habits_list_url, self.valid_habit_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 4)
        self.assertEqual(response.data["user"], self.user1.id)

    def test_create_habit_invalid_data(self):
        """Тест создания привычки с невалидными данными"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.habits_list_url, self.invalid_habit_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Проверяем, что есть ошибки валидации
        self.assertIn("non_field_errors", response.data)
        self.assertTrue(len(response.data["non_field_errors"]) > 0)

    def test_create_habit_with_reward_and_linked_habit(self):
        """Тест создания привычки с одновременным указанием вознаграждения и связанной привычки"""
        self.client.force_authenticate(user=self.user1)
        data = self.valid_habit_data.copy()
        data.update(
            {
                "reward": "Кофе",
                "linked_habit": self.habit1.id,
            }
        )
        response = self.client.post(self.habits_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_specific_habit_owner(self):
        """Тест получения конкретной привычки владельцем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("habits-detail", kwargs={"pk": self.habit1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.habit1.id)

    def test_get_specific_habit_other_user(self):
        """Тест получения чужой привычки"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("habits-detail", kwargs={"pk": self.habit1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_habit_owner(self):
        """Тест обновления привычки владельцем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("habits-detail", kwargs={"pk": self.habit1.id})
        update_data = {"action": "Обновленная зарядка"}
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit1.refresh_from_db()
        self.assertEqual(self.habit1.action, "Обновленная зарядка")

    def test_update_habit_other_user(self):
        """Тест обновления чужой привычки"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("habits-detail", kwargs={"pk": self.habit1.id})
        update_data = {"action": "Чужая попытка изменить"}
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_habit_owner(self):
        """Тест удаления привычки владельцем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("habits-detail", kwargs={"pk": self.habit1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 2)

    def test_delete_habit_other_user(self):
        """Тест удаления чужой привычки"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("habits-detail", kwargs={"pk": self.habit1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Habit.objects.count(), 3)  # Ничего не удалено

    def test_habit_list_pagination(self):
        """Тест пагинации списка привычек"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.habits_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_habit_ordering(self):
        """Тест ordering привычек"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.habits_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habits = response.data["results"]
        if len(habits) > 1:
            self.assertTrue(habits[0]["id"] >= habits[1]["id"])


class HabitValidationTests(APITestCase):
    """Тесты валидации бизнес-правил привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.habits_list_url = reverse("habits-list")

        # Создаем приятную привычку для тестов связывания с корректной длительностью
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time="20:00:00",
            action="Чтение книги",
            duration=120,  # 2 минуты
            frequency=1,
            is_pleasant=True,
        )

        self.not_pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Улица",
            time="07:00:00",
            action="Бег",
            duration=60,  # 1 минута
            frequency=1,
            is_pleasant=False,
        )

    def test_create_pleasant_habit_with_reward(self):
        """Тест: приятная привычка не может иметь вознаграждение"""
        data = {
            "place": "Дом",
            "time": "21:00:00",
            "action": "Просмотр фильма",
            "duration": 120,  # 2 минуты
            "frequency": 1,
            "is_pleasant": True,
            "reward": "Попкорн",
        }
        response = self.client.post(self.habits_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_create_pleasant_habit_with_linked_habit(self):
        """Тест: приятная привычка не может иметь связанную привычку"""
        data = {
            "place": "Дом",
            "time": "21:00:00",
            "action": "Просмотр фильма",
            "duration": 120,  # 2 минуты
            "frequency": 1,
            "is_pleasant": True,
            "linked_habit": self.pleasant_habit.id,
        }
        response = self.client.post(self.habits_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_create_habit_with_not_pleasant_linked_habit(self):
        """Тест: связанная привычка должна быть приятной"""
        data = {
            "place": "Офис",
            "time": "15:00:00",
            "action": "Перерыв",
            "duration": 60,  # 1 минута
            "frequency": 1,
            "is_pleasant": False,
            "linked_habit": self.not_pleasant_habit.id,
        }
        response = self.client.post(self.habits_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_with_pleasant_linked_habit(self):
        """Тест: успешное создание привычки с приятной связанной привычкой"""
        data = {
            "place": "Офис",
            "time": "15:00:00",
            "action": "Перерыв",
            "duration": 60,  # 1 минута
            "frequency": 1,
            "is_pleasant": False,
            "linked_habit": self.pleasant_habit.id,
        }
        response = self.client.post(self.habits_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_habit_with_reward_only(self):
        """Тест: успешное создание привычки только с вознаграждением"""
        data = {
            "place": "Офис",
            "time": "15:00:00",
            "action": "Работа",
            "duration": 90,  # 1.5 минуты
            "frequency": 1,
            "is_pleasant": False,
            "reward": "Кофе-брейк",
        }
        response = self.client.post(self.habits_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class HabitModelTests(TestCase):
    """Тесты модели Habit"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_habit_creation(self):
        """Тест создания привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time="08:00:00",
            action="Тестовая привычка",
            duration=60,
            frequency=1,
        )
        self.assertEqual(habit.action, "Тестовая привычка")
        self.assertEqual(habit.user, self.user)

    def test_habit_str_representation(self):
        """Тест строкового представления привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place="Дом",
            time="08:00:00",
            action="Тестовая привычка",
            duration=60,
            frequency=1,
        )
        self.assertIn(self.user.username, str(habit))
        self.assertIn("Тестовая привычка", str(habit))

    def test_habit_clean_validation(self):
        """Тест валидации clean метода"""
        habit = Habit(
            user=self.user,
            place="Дом",
            time="08:00:00",
            action="Тестовая привычка",
            duration=300,  # > 120 секунд
            frequency=1,
        )

        with self.assertRaises(Exception) as context:
            habit.clean()

        self.assertIn("120 секунд", str(context.exception))
