from django.db.models import QuerySet

from core.models import Role


def get_roles() -> QuerySet[Role]:
    """
    Возвращает список ролей продукта.

    :return: QuerySet ролей.
    """
    return Role.objects.all().order_by('name')


def get_role_by_id(*, role_id: int) -> Role:
    """
    Возвращает роль по идентификатору.

    :param role_id: Идентификатор роли.
    :return: Экземпляр роли.
    """
    return get_roles().get(id=role_id)
