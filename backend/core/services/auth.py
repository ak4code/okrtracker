from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from core.services.keycloak import (
    create_keycloak_token_pair,
    refresh_keycloak_access_token,
)


def create_jwt_token_pair(*, email: str, password: str) -> dict[str, str]:
    """
    Создаёт пару JWT-токенов для пользователя.

    :param email: Email пользователя для входа.
    :param password: Пароль пользователя для входа.
    :return: Словарь с access и refresh токенами.
    :raises AuthenticationFailed: Если переданы неверные учетные данные.
    """
    if settings.KEYCLOAK_ENABLED:
        return create_keycloak_token_pair(email=email, password=password)

    user = authenticate(email=email, password=password)

    if user is None:
        raise AuthenticationFailed('Неверный email или пароль.')

    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def refresh_jwt_access_token(*, refresh_token: str) -> dict[str, str]:
    """
    Обновляет access-токен по refresh-токену.

    :param refresh_token: Refresh-токен пользователя.
    :return: Словарь с новым access токеном.
    :raises AuthenticationFailed: Если refresh-токен недействителен.
    """
    if settings.KEYCLOAK_ENABLED:
        return refresh_keycloak_access_token(refresh_token=refresh_token)

    try:
        refresh = RefreshToken(refresh_token)
    except Exception as exc:  # noqa: BLE001
        raise AuthenticationFailed('Недействительный refresh-токен.') from exc

    return {
        'access': str(refresh.access_token),
    }
