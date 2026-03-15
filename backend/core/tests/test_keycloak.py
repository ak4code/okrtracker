import pytest
from django.contrib.auth.hashers import is_password_usable
from rest_framework.test import APIRequestFactory

from core.authentication import KeycloakJWTAuthentication
from core.models import User
from core.services import auth as auth_service
from core.services import keycloak as keycloak_service

pytestmark = [pytest.mark.django_db]


def test_login_uses_keycloak_when_enabled(settings, monkeypatch):
    """
    Arrange: включаем Keycloak и подменяем token exchange.
    Act: вызываем create_jwt_token_pair.
    Assert: ответ приходит из Keycloak service.
    """
    settings.KEYCLOAK_ENABLED = True
    monkeypatch.setattr(
        auth_service,
        'create_keycloak_token_pair',
        lambda *, email, password: {
            'access': f'access-for-{email}',
            'refresh': f'refresh-for-{password}',
        },
    )

    tokens = auth_service.create_jwt_token_pair(email='user@example.com', password='secret123')

    assert tokens == {
        'access': 'access-for-user@example.com',
        'refresh': 'refresh-for-secret123',
    }


def test_refresh_uses_keycloak_when_enabled(settings, monkeypatch):
    """
    Arrange: включаем Keycloak и подменяем refresh exchange.
    Act: вызываем refresh_jwt_access_token.
    Assert: access токен приходит из Keycloak service.
    """
    settings.KEYCLOAK_ENABLED = True
    monkeypatch.setattr(
        auth_service,
        'refresh_keycloak_access_token',
        lambda *, refresh_token: {
            'access': f'access-from-{refresh_token}',
        },
    )

    tokens = auth_service.refresh_jwt_access_token(refresh_token='refresh-token')

    assert tokens == {
        'access': 'access-from-refresh-token',
    }


def test_keycloak_authentication_returns_user(settings, monkeypatch):
    """
    Arrange: включаем Keycloak и подменяем разбор access token.
    Act: вызываем authentication class с Bearer токеном Keycloak.
    Assert: authentication class возвращает локального пользователя.
    """
    settings.KEYCLOAK_ENABLED = True

    user = User.objects.create_user(
        email='keycloak@example.com',
        password='secret123',
        first_name='Key',
        last_name='Cloak',
    )

    monkeypatch.setattr(
        'core.authentication.get_keycloak_user_by_access_token',
        lambda *, access_token: user if access_token == 'kc-token' else None,
    )
    request = APIRequestFactory().get(
        '/api/core/auth/me/',
        HTTP_AUTHORIZATION='Bearer kc-token',
    )

    authenticated = KeycloakJWTAuthentication().authenticate(request)

    assert authenticated == (user, 'kc-token')


def test_get_keycloak_user_by_access_token_creates_local_user(settings, monkeypatch):
    """
    Arrange: подменяем успешную валидацию claims от Keycloak.
    Act: синхронизируем локального пользователя по токену.
    Assert: создаётся активный пользователь с неиспользуемым паролем.
    """
    settings.KEYCLOAK_ENABLED = True
    monkeypatch.setattr(
        keycloak_service,
        '_decode_keycloak_access_token',
        lambda *, access_token: {
            'email': 'sync@example.com',
            'given_name': 'Sync',
            'family_name': 'User',
        },
    )

    user = keycloak_service.get_keycloak_user_by_access_token(access_token='kc-token')

    assert user is not None
    assert user.email == 'sync@example.com'
    assert user.first_name == 'Sync'
    assert user.last_name == 'User'
    assert user.is_active is True
    assert is_password_usable(user.password) is False
