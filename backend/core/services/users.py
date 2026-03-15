from django.utils.crypto import get_random_string

from core.models import Role, Team, User


def create_user(
    *,
    email: str,
    first_name: str,
    last_name: str,
    role: Role | None,
    primary_team: Team | None,
    teams: list[Team],
    is_active: bool,
    is_staff: bool,
    password: str | None,
) -> User:
    """
    Создаёт пользователя продукта.

    :param email: Email пользователя.
    :param first_name: Имя пользователя.
    :param last_name: Фамилия пользователя.
    :param role: Бизнес-роль пользователя.
    :param primary_team: Основная команда пользователя.
    :param teams: Команды пользователя.
    :param is_active: Флаг активности.
    :param is_staff: Флаг доступа в админку.
    :param password: Пароль пользователя.
    :return: Созданный пользователь.
    """
    user = User.objects.create_user(
        email=email,
        password=password or get_random_string(20),
        first_name=first_name,
        last_name=last_name,
        role=role,
        primary_team=primary_team,
        is_active=is_active,
        is_staff=is_staff,
    )
    user.teams.set(teams)
    return user


def update_user(
    *,
    user: User,
    email: str,
    first_name: str,
    last_name: str,
    role: Role | None,
    primary_team: Team | None,
    teams: list[Team],
    is_active: bool,
    is_staff: bool,
    password: str | None,
) -> User:
    """
    Обновляет пользователя продукта.

    :param user: Экземпляр пользователя.
    :param email: Email пользователя.
    :param first_name: Имя пользователя.
    :param last_name: Фамилия пользователя.
    :param role: Бизнес-роль пользователя.
    :param primary_team: Основная команда пользователя.
    :param teams: Команды пользователя.
    :param is_active: Флаг активности.
    :param is_staff: Флаг доступа в админку.
    :param password: Новый пароль пользователя.
    :return: Обновлённый пользователь.
    """
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.role = role
    user.primary_team = primary_team
    user.is_active = is_active
    user.is_staff = is_staff
    if password:
        user.set_password(password)
    user.save(
        update_fields=[
            'email',
            'first_name',
            'last_name',
            'role',
            'primary_team',
            'is_active',
            'is_staff',
            'password',
            'updated_at',
        ],
    )
    user.teams.set(teams)
    return user
