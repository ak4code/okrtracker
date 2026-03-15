from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common_utils.api import IsStaffForUnsafeMethods
from core.api.serializers import (
    CurrentUserSerializer,
    JWTLoginSerializer,
    JWTRefreshSerializer,
    RoleSerializer,
    RoleUpsertSerializer,
    TeamSerializer,
    TeamUpsertSerializer,
    UserListSerializer,
    UserUpsertSerializer,
)
from core.selectors import get_roles, get_team_by_id, get_teams, get_users
from core.services.auth import create_jwt_token_pair, refresh_jwt_access_token


class JWTLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Выполняет вход пользователя и возвращает JWT-токены.

        :param request: HTTP-запрос с email и password.
        :return: HTTP-ответ с парой JWT-токенов.
        """
        serializer = JWTLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = create_jwt_token_pair(**serializer.validated_data)
        return Response(tokens, status=status.HTTP_200_OK)


class JWTRefreshAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Обновляет access-токен по refresh-токену.

        :param request: HTTP-запрос с refresh-токеном.
        :return: HTTP-ответ с новым access-токеном.
        """
        serializer = JWTRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = refresh_jwt_access_token(refresh_token=serializer.validated_data['refresh'])
        return Response(payload, status=status.HTTP_200_OK)


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Возвращает данные текущего пользователя по JWT-токену.

        :param request: HTTP-запрос с аутентифицированным пользователем.
        :return: HTTP-ответ с данными текущего пользователя.
        """
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoleListAPIView(APIView):
    permission_classes = [IsStaffForUnsafeMethods]

    def get(self, request):
        """
        Возвращает список ролей продукта.

        :param request: HTTP-запрос аутентифицированного пользователя.
        :return: HTTP-ответ со списком ролей.
        """
        serializer = RoleSerializer(get_roles(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Создаёт роль продукта.

        :param request: HTTP-запрос с данными роли.
        :return: HTTP-ответ с созданной ролью.
        """
        serializer = RoleUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)


class RoleDetailAPIView(APIView):
    permission_classes = [IsStaffForUnsafeMethods]

    def patch(self, request, role_id: int):
        """
        Обновляет роль продукта.

        :param request: HTTP-запрос с данными роли.
        :param role_id: Идентификатор роли.
        :return: HTTP-ответ с обновлённой ролью.
        :raises Http404: Если роль не найдена.
        """
        role = get_object_or_404(get_roles(), id=role_id)
        serializer = RoleUpsertSerializer(instance=role, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_role = serializer.save()
        return Response(RoleSerializer(updated_role).data, status=status.HTTP_200_OK)


class TeamListAPIView(APIView):
    permission_classes = [IsStaffForUnsafeMethods]

    def get(self, request):
        """
        Возвращает список команд.

        :param request: HTTP-запрос аутентифицированного пользователя.
        :return: HTTP-ответ со списком команд.
        """
        serializer = TeamSerializer(get_teams(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Создаёт команду.

        :param request: HTTP-запрос с данными команды.
        :return: HTTP-ответ с созданной командой.
        """
        serializer = TeamUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        return Response(TeamSerializer(get_team_by_id(team_id=team.id)).data, status=status.HTTP_201_CREATED)


class TeamDetailAPIView(APIView):
    permission_classes = [IsStaffForUnsafeMethods]

    def patch(self, request, team_id: int):
        """
        Обновляет команду.

        :param request: HTTP-запрос с данными команды.
        :param team_id: Идентификатор команды.
        :return: HTTP-ответ с обновлённой командой.
        :raises Http404: Если команда не найдена.
        """
        team = get_object_or_404(get_teams(), id=team_id)
        serializer = TeamUpsertSerializer(instance=team, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_team = serializer.save()
        return Response(TeamSerializer(get_team_by_id(team_id=updated_team.id)).data, status=status.HTTP_200_OK)


class UserListAPIView(APIView):
    permission_classes = [IsStaffForUnsafeMethods]

    def get(self, request):
        """
        Возвращает список пользователей.

        :param request: HTTP-запрос аутентифицированного пользователя.
        :return: HTTP-ответ со списком пользователей.
        """
        serializer = UserListSerializer(get_users(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Создаёт пользователя.

        :param request: HTTP-запрос с данными пользователя.
        :return: HTTP-ответ с созданным пользователем.
        """
        serializer = UserUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserListSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailAPIView(APIView):
    permission_classes = [IsStaffForUnsafeMethods]

    def patch(self, request, user_id: int):
        """
        Обновляет пользователя.

        :param request: HTTP-запрос с данными пользователя.
        :param user_id: Идентификатор пользователя.
        :return: HTTP-ответ с обновлённым пользователем.
        :raises Http404: Если пользователь не найден.
        """
        user = get_object_or_404(get_users(), id=user_id)
        serializer = UserUpsertSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()
        return Response(UserListSerializer(updated_user).data, status=status.HTTP_200_OK)
