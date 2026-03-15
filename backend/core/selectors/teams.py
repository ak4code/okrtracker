from django.db.models import Count, QuerySet

from core.models import Team


def get_teams() -> QuerySet[Team]:
    """
    Возвращает список команд с участниками.

    :return: QuerySet команд.
    """
    return Team.objects.annotate(members_count=Count('members', distinct=True)).order_by('name')


def get_team_by_id(*, team_id: int) -> Team:
    """
    Возвращает команду по идентификатору.

    :param team_id: Идентификатор команды.
    :return: Экземпляр команды.
    """
    return Team.objects.annotate(members_count=Count('members', distinct=True)).get(id=team_id)
