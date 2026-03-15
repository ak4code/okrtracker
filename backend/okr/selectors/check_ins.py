from django.db.models import QuerySet

from okr.models import CheckIn


def get_check_ins() -> QuerySet[CheckIn]:
    """
    Возвращает queryset check-in с базовыми связями.

    :return: QuerySet check-in.
    """
    return CheckIn.objects.select_related('author', 'key_result', 'key_result__okr')


def get_check_in_by_id(*, check_in_id: int) -> CheckIn:
    """
    Возвращает check-in по идентификатору.

    :param check_in_id: Идентификатор check-in.
    :return: Экземпляр check-in.
    """
    return get_check_ins().get(id=check_in_id)
