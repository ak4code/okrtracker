from django.db.models import QuerySet

from okr.models import Quarter


def get_quarters() -> QuerySet[Quarter]:
    """
    Возвращает список кварталов для выбора периода.

    :return: QuerySet кварталов, отсортированный по году и кварталу.
    """
    return Quarter.objects.order_by('year', 'quarter')


def get_quarter_by_id(*, quarter_id: int) -> Quarter:
    """
    Возвращает квартал по идентификатору.

    :param quarter_id: Идентификатор квартала.
    :return: Экземпляр квартала.
    """
    return get_quarters().get(id=quarter_id)
