from rest_framework import serializers

from core.models import Role, Team, User
from core.services.roles import create_role, update_role
from core.services.teams import create_team, update_team
from core.services.users import create_user, update_user


class JWTLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)


class JWTRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=False)


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()


class RoleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    description = serializers.CharField()


class RoleUpsertSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=64, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs: dict) -> dict:
        """
        Проверяет уникальность роли.

        :param attrs: Данные роли.
        :return: Провалидированные данные.
        """
        name_queryset = Role.objects.filter(name=attrs['name'])
        code_queryset = Role.objects.filter(code=attrs.get('code') or attrs['name'])
        if self.instance is not None:
            name_queryset = name_queryset.exclude(id=self.instance.id)
            code_queryset = code_queryset.exclude(id=self.instance.id)
        if name_queryset.exists():
            raise serializers.ValidationError({'name': 'Роль с таким названием уже существует.'})
        if attrs.get('code') and code_queryset.exists():
            raise serializers.ValidationError({'code': 'Роль с таким кодом уже существует.'})
        return attrs

    def create(self, validated_data: dict) -> Role:
        """
        Создаёт роль через service-слой.

        :param validated_data: Провалидированные данные роли.
        :return: Созданная роль.
        """
        return create_role(**validated_data)

    def update(self, instance: Role, validated_data: dict) -> Role:
        """
        Обновляет роль через service-слой.

        :param instance: Существующая роль.
        :param validated_data: Провалидированные данные роли.
        :return: Обновлённая роль.
        """
        return update_role(role=instance, **validated_data)


class TeamSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField()
    description = serializers.CharField()
    members_count = serializers.IntegerField()


class TeamUpsertSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=64, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs: dict) -> dict:
        """
        Проверяет уникальность команды.

        :param attrs: Данные команды.
        :return: Провалидированные данные.
        """
        name_queryset = Team.objects.filter(name=attrs['name'])
        code_queryset = Team.objects.filter(code=attrs.get('code') or attrs['name'])
        if self.instance is not None:
            name_queryset = name_queryset.exclude(id=self.instance.id)
            code_queryset = code_queryset.exclude(id=self.instance.id)
        if name_queryset.exists():
            raise serializers.ValidationError({'name': 'Команда с таким названием уже существует.'})
        if attrs.get('code') and code_queryset.exists():
            raise serializers.ValidationError({'code': 'Команда с таким кодом уже существует.'})
        return attrs

    def create(self, validated_data: dict) -> Team:
        """
        Создаёт команду через service-слой.

        :param validated_data: Провалидированные данные команды.
        :return: Созданная команда.
        """
        return create_team(**validated_data)

    def update(self, instance: Team, validated_data: dict) -> Team:
        """
        Обновляет команду через service-слой.

        :param instance: Существующая команда.
        :param validated_data: Провалидированные данные команды.
        :return: Обновлённая команда.
        """
        return update_team(team=instance, **validated_data)


class UserListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.SerializerMethodField()
    primary_team = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()

    def get_role(self, obj: User) -> str:
        """
        Возвращает название роли пользователя.

        :param obj: Экземпляр пользователя.
        :return: Название роли или пустая строка.
        """
        return obj.role.name if obj.role else ''

    def get_primary_team(self, obj: User) -> str:
        """
        Возвращает основную команду пользователя.

        :param obj: Экземпляр пользователя.
        :return: Название команды или пустая строка.
        """
        return obj.primary_team.name if obj.primary_team else ''

    def get_teams(self, obj: User) -> list[int]:
        """
        Возвращает идентификаторы команд пользователя.

        :param obj: Экземпляр пользователя.
        :return: Список идентификаторов команд.
        """
        return list(obj.teams.values_list('id', flat=True))


class UserUpsertSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    role_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    primary_team_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    team_ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)
    is_active = serializers.BooleanField(required=False, default=True)
    is_staff = serializers.BooleanField(required=False, default=False)
    password = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs: dict) -> dict:
        """
        Проверяет пользователя и связанные сущности.

        :param attrs: Данные пользователя.
        :return: Провалидированные данные.
        """
        email_queryset = User.objects.filter(email=attrs['email'])
        if self.instance is not None:
            email_queryset = email_queryset.exclude(id=self.instance.id)
        if email_queryset.exists():
            raise serializers.ValidationError({'email': 'Пользователь с таким email уже существует.'})

        role = Role.objects.filter(id=attrs['role_id']).first() if attrs.get('role_id') else None
        if attrs.get('role_id') and role is None:
            raise serializers.ValidationError({'role_id': 'Роль не найдена.'})

        primary_team = (
            Team.objects.filter(id=attrs['primary_team_id']).first() if attrs.get('primary_team_id') else None
        )
        if attrs.get('primary_team_id') and primary_team is None:
            raise serializers.ValidationError({'primary_team_id': 'Команда не найдена.'})

        teams = list(Team.objects.filter(id__in=attrs['team_ids']))
        if len(teams) != len(set(attrs['team_ids'])):
            raise serializers.ValidationError({'team_ids': 'Одна или несколько команд не найдены.'})

        attrs['role'] = role
        attrs['primary_team'] = primary_team
        attrs['teams'] = teams
        return attrs

    def create(self, validated_data: dict) -> User:
        """
        Создаёт пользователя через service-слой.

        :param validated_data: Провалидированные данные пользователя.
        :return: Созданный пользователь.
        """
        return create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            primary_team=validated_data['primary_team'],
            teams=validated_data['teams'],
            is_active=validated_data['is_active'],
            is_staff=validated_data['is_staff'],
            password=validated_data['password'] or None,
        )

    def update(self, instance: User, validated_data: dict) -> User:
        """
        Обновляет пользователя через service-слой.

        :param instance: Существующий пользователь.
        :param validated_data: Провалидированные данные пользователя.
        :return: Обновлённый пользователь.
        """
        return update_user(
            user=instance,
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            primary_team=validated_data['primary_team'],
            teams=validated_data['teams'],
            is_active=validated_data['is_active'],
            is_staff=validated_data['is_staff'],
            password=validated_data['password'] or None,
        )
