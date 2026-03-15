from rest_framework.authentication import BaseAuthentication, get_authorization_header

from core.services.keycloak import get_keycloak_user_by_access_token


class KeycloakJWTAuthentication(BaseAuthentication):
    """Аутентифицирует пользователя по Keycloak access token."""

    keyword = 'Bearer'

    def authenticate(self, request):
        """
        Выполняет аутентификацию по Bearer access token.

        :param request: HTTP-запрос.
        :return: Кортеж из пользователя и токена или ``None``.
        """
        authorization = get_authorization_header(request).split()
        if not authorization or authorization[0].lower() != self.keyword.lower().encode():
            return None

        if len(authorization) != 2:
            return None

        try:
            access_token = authorization[1].decode('utf-8')
        except UnicodeDecodeError:
            return None

        user = get_keycloak_user_by_access_token(access_token=access_token)
        if user is None:
            return None

        return user, access_token
