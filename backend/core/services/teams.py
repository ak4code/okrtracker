from django.utils.text import slugify

from core.models import Team


def create_team(*, name: str, code: str, description: str) -> Team:
    """
    Создаёт команду.

    :param name: Название команды.
    :param code: Код команды.
    :param description: Описание команды.
    :return: Созданная команда.
    """
    normalized_code = slugify(code or name)
    return Team.objects.create(name=name, code=normalized_code, description=description)


def update_team(*, team: Team, name: str, code: str, description: str) -> Team:
    """
    Обновляет команду.

    :param team: Экземпляр команды.
    :param name: Название команды.
    :param code: Код команды.
    :param description: Описание команды.
    :return: Обновлённая команда.
    """
    team.name = name
    team.code = slugify(code or name)
    team.description = description
    team.save(update_fields=['name', 'code', 'description', 'updated_at'])
    return team
