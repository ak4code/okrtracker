from django.utils.text import slugify

from core.models import Role


def create_role(*, name: str, code: str, description: str) -> Role:
    """
    Создаёт бизнес-роль.

    :param name: Название роли.
    :param code: Код роли.
    :param description: Описание роли.
    :return: Созданная роль.
    """
    normalized_code = slugify(code or name)
    return Role.objects.create(name=name, code=normalized_code, description=description)


def update_role(*, role: Role, name: str, code: str, description: str) -> Role:
    """
    Обновляет бизнес-роль.

    :param role: Экземпляр роли.
    :param name: Название роли.
    :param code: Код роли.
    :param description: Описание роли.
    :return: Обновлённая роль.
    """
    role.name = name
    role.code = slugify(code or name)
    role.description = description
    role.save(update_fields=['name', 'code', 'description', 'updated_at'])
    return role
