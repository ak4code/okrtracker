from django.db.models import QuerySet

from okr.models import KeyResult


def get_key_results() -> QuerySet[KeyResult]:
    """
    Возвращает queryset ключевых результатов с базовыми связями.

    :return: QuerySet ключевых результатов.
    """
    return KeyResult.objects.select_related('okr', 'okr__owner', 'okr__team', 'okr__period')


def get_key_result_by_id(*, key_result_id: int) -> KeyResult:
    """
    Возвращает ключевой результат по идентификатору.

    :param key_result_id: Идентификатор ключевого результата.
    :return: Экземпляр ключевого результата.
    """
    return get_key_results().get(id=key_result_id)
