import pytest
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.urls import resolve
from rest_framework.test import APIRequestFactory

from core.api.views import JWTLoginAPIView
from core.models import User

pytestmark = [pytest.mark.django_db]


def test_django_settings_loaded():
    """
    Arrange: Django settings уже загружены тестовым раннером.
    Act: читаем значение ROOT_URLCONF из settings.
    Assert: используется корневой URL-конфиг проекта.
    """
    assert settings.ROOT_URLCONF == 'config.urls'


def test_admin_url_is_registered():
    """
    Arrange: URL-конфиг проекта зарегистрирован в Django.
    Act: резолвим путь /admin/.
    Assert: маршрут указывает на стандартный admin index view.
    """
    match = resolve('/admin/')
    assert match.func.__name__ == 'index'


def test_drf_api_request_factory_works(login_payload, login_user):
    """
    Arrange: создаём пользователя и POST-запрос через APIRequestFactory для реального login view.
    Act: вызываем JWTLoginAPIView через as_view().
    Assert: получаем успешный ответ с access и refresh токенами.
    """
    request = APIRequestFactory().post(
        '/api/core/auth/jwt/login/',
        login_payload,
        format='json',
    )
    response = JWTLoginAPIView.as_view()(request)

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_user_includes_permissions_mixin():
    """
    Arrange: импортирована пользовательская модель User.
    Act: проверяем наследование от PermissionsMixin.
    Assert: модель пользователя поддерживает permissions API Django.
    """
    assert issubclass(User, PermissionsMixin)


@pytest.mark.parametrize(
    ('email', 'is_superuser'),
    [
        ('user@example.com', False),
        ('admin@example.com', True),
    ],
)
def test_user_manager_uses_email_as_login(email, is_superuser):
    """
    Arrange: используем кастомный manager пользователя.
    Act: создаём пользователя через manager по email и паролю.
    Assert: email используется как USERNAME_FIELD, а username отсутствует.
    """
    if is_superuser:
        user = User.objects.create_superuser(email=email, password='secret123')
    else:
        user = User.objects.create_user(email=email, password='secret123')

    assert user.email == email
    assert user.USERNAME_FIELD == 'email'
    assert user.username is None
    assert user.check_password('secret123')
    assert user.is_superuser is is_superuser


def test_user_manager_creates_superuser():
    """
    Arrange: используем кастомный manager пользователя.
    Act: создаём суперпользователя по email и паролю.
    Assert: обязательные флаги суперпользователя выставлены корректно.
    """
    user = User.objects.create_superuser(email='admin@example.com', password='secret123')

    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.is_active is True


@pytest.mark.parametrize(
    'endpoint',
    [
        '/api/core/auth/jwt/login/',
    ],
)
def test_jwt_login_returns_token_pair(api_client, endpoint, login_payload, login_user):
    """
    Arrange: создаём пользователя и готовим API-клиент с корректными учетными данными.
    Act: отправляем POST-запрос на JWT login endpoint.
    Assert: получаем access и refresh токены со статусом 200.
    """
    response = api_client.post(endpoint, login_payload, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_jwt_refresh_returns_new_access_token(api_client, login_payload, login_user):
    """
    Arrange: создаём пользователя и получаем refresh токен через login endpoint.
    Act: отправляем POST-запрос на endpoint обновления токена.
    Assert: получаем новый access токен со статусом 200.
    """
    login_response = api_client.post('/api/core/auth/jwt/login/', login_payload, format='json')

    response = api_client.post(
        '/api/core/auth/jwt/refresh/',
        {
            'refresh': login_response.data['refresh'],
        },
        format='json',
    )

    assert response.status_code == 200
    assert 'access' in response.data


def test_current_user_endpoint_returns_authenticated_user(api_client, make_user):
    """
    Arrange: создаём пользователя, получаем access токен и добавляем его в заголовок Authorization.
    Act: отправляем GET-запрос на endpoint текущего пользователя.
    Assert: получаем данные аутентифицированного пользователя со статусом 200.
    """
    make_user(
        first_name='Иван',
        last_name='Иванов',
        email='me@example.com',
    )
    login_response = api_client.post(
        '/api/core/auth/jwt/login/',
        {
            'email': 'me@example.com',
            'password': 'secret123',
        },
        format='json',
    )
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')

    response = api_client.get('/api/core/auth/me/')

    assert response.status_code == 200
    assert response.data['email'] == 'me@example.com'
    assert response.data['first_name'] == 'Иван'
    assert response.data['last_name'] == 'Иванов'
