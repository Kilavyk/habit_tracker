from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserAuthenticationTests(APITestCase):
    """Тесты аутентификации и регистрации пользователей"""

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')

        # Создаем тестового пользователя
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Testpass123',
            'password2': 'Testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='Existingpass123'
        )

    def test_user_registration_success(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

        # Проверяем, что пользователь создан в базе
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_registration_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями"""
        data = self.user_data.copy()
        data['password2'] = 'Differentpass123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_login_success(self):
        """Тест успешного входа пользователя"""
        login_data = {
            'username': 'existinguser',
            'password': 'Existingpass123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """Тест входа с неверными учетными данными"""
        login_data = {
            'username': 'existinguser',
            'password': 'Wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile_access_authenticated(self):
        """Тест доступа к профилю аутентифицированного пользователя"""
        self.client.force_authenticate(user=self.existing_user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'existinguser')

    def test_user_profile_access_unauthenticated(self):
        """Тест доступа к профилю неаутентифицированного пользователя"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile_update(self):
        """Тест обновления профиля пользователя"""
        self.client.force_authenticate(user=self.existing_user)
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        response = self.client.patch(self.profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_user.refresh_from_db()
        self.assertEqual(self.existing_user.first_name, 'Updated')
        self.assertEqual(self.existing_user.email, 'updated@example.com')
