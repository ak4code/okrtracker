from django.db.models import Prefetch, QuerySet

from core.models import Team, User


def get_user_display_name(user: User) -> str:
    """
    Возвращает отображаемое имя пользователя.

    :param user: Экземпляр пользователя.
    :return: Имя и фамилия пользователя или email.
    """
    full_name = f'{user.first_name} {user.last_name}'.strip()
    return full_name or user.email


def get_users() -> QuerySet[User]:
    """
    Возвращает список пользователей с ролями и командами.

    :return: QuerySet пользователей.
    """
    return (
        User.objects.select_related('role', 'primary_team')
        .prefetch_related(
            Prefetch('teams', queryset=Team.objects.only('id')),
        )
        .order_by('email')
    )


def get_user_by_id(*, user_id: int) -> User:
    """
    Возвращает пользователя по идентификатору.

    :param user_id: Идентификатор пользователя.
    :return: Экземпляр пользователя.
    """
    return get_users().get(id=user_id)
