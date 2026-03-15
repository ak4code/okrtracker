import json
import ssl
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import AuthenticationFailed

from core.models import User

KEYCLOAK_HTTP_TIMEOUT_SECONDS = 10


def is_keycloak_enabled() -> bool:
    """
    Возвращает флаг включения интеграции с Keycloak.

    :return: ``True``, если Keycloak включён.
    """
    return bool(settings.KEYCLOAK_ENABLED)


def create_keycloak_token_pair(*, email: str, password: str) -> dict[str, str]:
    """
    Создаёт пару токенов через Keycloak.

    :param email: Логин пользователя в Keycloak.
    :param password: Пароль пользователя в Keycloak.
    :return: Словарь с access и refresh токенами.
    """
    payload = _request_keycloak_token(
        {
            'grant_type': 'password',
            'client_id': _get_required_keycloak_setting('KEYCLOAK_CLIENT_ID'),
            'username': email,
            'password': password,
            'scope': 'openid profile email',
        }
    )
    return _build_token_pair(payload)


def refresh_keycloak_access_token(*, refresh_token: str) -> dict[str, str]:
    """
    Обновляет access-токен через Keycloak.

    :param refresh_token: Refresh-токен пользователя.
    :return: Словарь с новым access токеном.
    """
    payload = _request_keycloak_token(
        {
            'grant_type': 'refresh_token',
            'client_id': _get_required_keycloak_setting('KEYCLOAK_CLIENT_ID'),
            'refresh_token': refresh_token,
        }
    )
    return {
        'access': _extract_token_value(payload=payload, key='access_token'),
    }


def get_keycloak_user_by_access_token(*, access_token: str) -> User | None:
    """
    Возвращает локального пользователя по Keycloak access token.

    Если токен не относится к Keycloak, возвращает ``None``.

    :param access_token: Bearer access token.
    :return: Пользователь приложения или ``None``.
    """
    claims = _decode_keycloak_access_token(access_token=access_token)
    if claims is None:
        return None

    return _sync_keycloak_user(claims=claims)


def _build_token_pair(*, payload: dict) -> dict[str, str]:
    """
    Приводит ответ Keycloak к формату API приложения.

    :param payload: Ответ token endpoint.
    :return: Словарь с access и refresh токенами.
    """
    return {
        'access': _extract_token_value(payload=payload, key='access_token'),
        'refresh': _extract_token_value(payload=payload, key='refresh_token'),
    }


def _extract_token_value(*, payload: dict, key: str) -> str:
    """
    Извлекает обязательное значение токена из ответа Keycloak.

    :param payload: Ответ token endpoint.
    :param key: Ключ токена.
    :return: Значение токена.
    :raises AuthenticationFailed: Если ключ отсутствует.
    """
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise AuthenticationFailed('Keycloak вернул некорректный набор токенов.')
    return value


def _request_keycloak_token(data: dict[str, str]) -> dict:
    """
    Выполняет запрос к token endpoint Keycloak.

    :param data: Данные формы для token endpoint.
    :return: JSON-ответ Keycloak.
    """
    if not is_keycloak_enabled():
        raise AuthenticationFailed('Интеграция с Keycloak отключена.')

    request_data = {
        **data,
    }
    client_secret = settings.KEYCLOAK_CLIENT_SECRET
    if client_secret:
        request_data['client_secret'] = client_secret

    return _perform_json_request(
        url=get_keycloak_openid_configuration()['token_endpoint'],
        data=request_data,
        default_error_message='Не удалось выполнить аутентификацию через Keycloak.',
    )


def _decode_keycloak_access_token(*, access_token: str) -> dict | None:
    """
    Декодирует и проверяет Keycloak access token.

    :param access_token: Bearer access token.
    :return: Claims токена или ``None``, если токен не от Keycloak.
    """
    unverified_claims = _decode_unverified_claims(access_token=access_token)
    if unverified_claims is None:
        return None

    if unverified_claims.get('iss') != get_keycloak_issuer():
        return None

    signing_key = _get_signing_key(access_token=access_token)
    algorithm = _get_token_algorithm(access_token=access_token)

    try:
        claims = jwt.decode(
            access_token,
            key=signing_key,
            algorithms=[algorithm],
            issuer=get_keycloak_issuer(),
            options={'verify_aud': False},
        )
    except jwt.PyJWTError as error:
        raise AuthenticationFailed('Недействительный Keycloak access token.') from error

    _validate_client_claims(claims=claims)
    return claims


def _decode_unverified_claims(*, access_token: str) -> dict | None:
    """
    Возвращает claims токена без проверки подписи.

    :param access_token: Bearer access token.
    :return: Claims токена или ``None``.
    """
    try:
        claims = jwt.decode(
            access_token,
            options={
                'verify_signature': False,
                'verify_exp': False,
                'verify_aud': False,
            },
        )
    except jwt.PyJWTError:
        return None

    return claims if isinstance(claims, dict) else None


def _get_signing_key(*, access_token: str):
    """
    Возвращает публичный ключ для проверки подписи токена.

    :param access_token: Bearer access token.
    :return: Объект ключа для ``jwt.decode``.
    """
    header = jwt.get_unverified_header(access_token)
    key_id = header.get('kid')
    if not isinstance(key_id, str) or not key_id:
        raise AuthenticationFailed('Не удалось определить signing key Keycloak.')

    for jwk in get_keycloak_jwks().get('keys', []):
        if jwk.get('kid') == key_id:
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    raise AuthenticationFailed('Signing key Keycloak не найден.')


def _get_token_algorithm(*, access_token: str) -> str:
    """
    Возвращает алгоритм подписи токена.

    :param access_token: Bearer access token.
    :return: Алгоритм подписи.
    """
    header = jwt.get_unverified_header(access_token)
    algorithm = header.get('alg')
    if not isinstance(algorithm, str) or not algorithm:
        raise AuthenticationFailed('Не удалось определить алгоритм подписи Keycloak.')
    return algorithm


def _validate_client_claims(*, claims: dict) -> None:
    """
    Проверяет принадлежность токена настроенному клиенту Keycloak.

    :param claims: Claims access token.
    :raises AuthenticationFailed: Если токен выпущен не для нужного клиента.
    """
    client_id = _get_required_keycloak_setting('KEYCLOAK_CLIENT_ID')
    authorized_party = claims.get('azp')
    audience = claims.get('aud')

    if authorized_party == client_id:
        return

    if isinstance(audience, str) and audience == client_id:
        return

    if isinstance(audience, list) and client_id in audience:
        return

    raise AuthenticationFailed('Токен Keycloak выпущен для другого клиента.')


def _sync_keycloak_user(*, claims: dict) -> User:
    """
    Создаёт или обновляет локального пользователя по claims токена.

    :param claims: Claims access token.
    :return: Локальный пользователь.
    """
    email = claims.get('email')
    if not isinstance(email, str) or not email:
        raise AuthenticationFailed('В Keycloak access token отсутствует email.')

    first_name = claims.get('given_name') if isinstance(claims.get('given_name'), str) else ''
    last_name = claims.get('family_name') if isinstance(claims.get('family_name'), str) else ''

    user = User.objects.filter(email=email).first()
    if user is None:
        return User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            password=make_password(None),
        )

    update_fields: list[str] = []
    if user.first_name != first_name:
        user.first_name = first_name
        update_fields.append('first_name')
    if user.last_name != last_name:
        user.last_name = last_name
        update_fields.append('last_name')
    if not user.is_active:
        user.is_active = True
        update_fields.append('is_active')

    if update_fields:
        update_fields.append('updated_at')
        user.save(update_fields=update_fields)

    return user


@lru_cache(maxsize=1)
def get_keycloak_openid_configuration() -> dict:
    """
    Возвращает OpenID configuration Keycloak.

    :return: OpenID configuration.
    """
    return _perform_json_request(
        url=f'{get_keycloak_issuer()}/.well-known/openid-configuration',
        data=None,
        default_error_message='Не удалось получить конфигурацию Keycloak.',
    )


@lru_cache(maxsize=1)
def get_keycloak_jwks() -> dict:
    """
    Возвращает JSON Web Key Set Keycloak.

    :return: Набор публичных ключей.
    """
    return _perform_json_request(
        url=get_keycloak_openid_configuration()['jwks_uri'],
        data=None,
        default_error_message='Не удалось получить публичные ключи Keycloak.',
    )


def get_keycloak_issuer() -> str:
    """
    Возвращает issuer Keycloak.

    :return: URL issuer.
    """
    server_url = _get_required_keycloak_setting('KEYCLOAK_SERVER_URL')
    realm = _get_required_keycloak_setting('KEYCLOAK_REALM')
    return f'{server_url}/realms/{realm}'


def _perform_json_request(*, url: str, data: dict[str, str] | None, default_error_message: str) -> dict:
    """
    Выполняет JSON-запрос к Keycloak.

    :param url: URL endpoint.
    :param data: Данные формы или ``None``.
    :param default_error_message: Сообщение об ошибке по умолчанию.
    :return: JSON-ответ.
    """
    request_data = None
    headers = {'Accept': 'application/json'}
    if data is not None:
        request_data = urlencode(data).encode('utf-8')
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

    request = Request(url, data=request_data, headers=headers)

    try:
        with urlopen(
            request,
            timeout=KEYCLOAK_HTTP_TIMEOUT_SECONDS,
            context=_build_ssl_context(),
        ) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        payload = _decode_error_payload(error=error)
        error_message = payload.get('error_description') or payload.get('error') or default_error_message
        raise AuthenticationFailed(error_message) from error
    except (URLError, TimeoutError, ValueError) as error:
        raise AuthenticationFailed(default_error_message) from error

    if not isinstance(payload, dict):
        raise AuthenticationFailed(default_error_message)

    return payload


def _decode_error_payload(*, error: HTTPError) -> dict:
    """
    Пытается декодировать JSON-ошибку Keycloak.

    :param error: HTTP-ошибка.
    :return: Декодированный payload или пустой словарь.
    """
    try:
        payload = json.loads(error.read().decode('utf-8'))
    except ValueError:
        return {}

    return payload if isinstance(payload, dict) else {}


def _build_ssl_context() -> ssl.SSLContext | None:
    """
    Возвращает SSL-контекст для запросов в Keycloak.

    :return: SSL-контекст или ``None``.
    """
    if settings.KEYCLOAK_VERIFY_SSL:
        return None
    return ssl._create_unverified_context()


def _get_required_keycloak_setting(setting_name: str) -> str:
    """
    Возвращает обязательную настройку Keycloak.

    :param setting_name: Имя настройки.
    :return: Значение настройки.
    :raises AuthenticationFailed: Если настройка не заполнена.
    """
    value = getattr(settings, setting_name, '')
    if isinstance(value, str) and value:
        return value
    raise AuthenticationFailed('Keycloak настроен не полностью.')
