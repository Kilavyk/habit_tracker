from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, UserLoginSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint для регистрации нового пользователя.

    Method: POST
    URL: /api/register/

    Request Body:
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "password2": "string",
            "first_name": "string",
            "last_name": "string"
        }

    Response:
        - 201 Created: Успешная регистрация с JWT токенами
        - 400 Bad Request: Ошибки валидации
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    API endpoint для аутентификации пользователя.

    Method: POST
    URL: /api/login/

    Request Body:
        {
            "username": "string",
            "password": "string"
        }

    Response:
        - 200 OK: Успешная аутентификация с JWT токенами
        - 401 Unauthorized: Неверные учетные данные
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint для просмотра и редактирования профиля пользователя.

    Methods:
        GET /api/profile/ - получение данных профиля
        PUT /api/profile/ - полное обновление профиля
        PATCH /api/profile/ - частичное обновление профиля

    Permissions:
        - Только аутентифицированные пользователи
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
