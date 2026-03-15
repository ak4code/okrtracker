from django.db.models import Count, Max, Prefetch, Q, QuerySet

from okr.constants import ChangeLogEntityType
from okr.models import ChangeLog, CheckIn, Comment, KeyResult, Okr
from okr.services.progress import calculate_progress


def get_okrs(
    *,
    quarter_name: str | None = None,
    status: str | None = None,
    team_id: int | None = None,
) -> QuerySet[Okr]:
    """
    Возвращает список OKR с основными связанными данными.

    :param quarter_name: Название квартала для фильтрации.
    :param status: Статус OKR для фильтрации.
    :param team_id: Идентификатор команды для фильтрации.
    :return: QuerySet OKR с select_related и prefetch_related.
    """
    queryset = Okr.objects.select_related('owner', 'team', 'period', 'created_by').annotate(
        key_results_count=Count('key_results', distinct=True),
        completed_key_results_count=Count(
            'key_results',
            filter=Q(key_results__status='completed'),
            distinct=True,
        ),
        comments_count=Count('comments', distinct=True),
    )

    if quarter_name:
        queryset = queryset.filter(period__name=quarter_name)

    if status:
        queryset = queryset.filter(status=status)

    if team_id:
        queryset = queryset.filter(team_id=team_id)

    return queryset.order_by('period__year', 'period__quarter', 'id')


def get_okr_detail_queryset() -> QuerySet[Okr]:
    """
    Возвращает queryset OKR со всеми данными для детальной карточки.

    :return: QuerySet OKR с предзагруженными связанными объектами.
    """
    return Okr.objects.select_related('owner', 'team', 'period', 'created_by').prefetch_related(
        Prefetch(
            'key_results',
            queryset=KeyResult.objects.annotate(
                last_check_in=Max('check_ins__created_at'),
            )
            .prefetch_related(
                Prefetch(
                    'check_ins',
                    queryset=CheckIn.objects.select_related('author').order_by('-created_at'),
                ),
            )
            .order_by('value', 'id'),
        ),
        Prefetch(
            'comments',
            queryset=Comment.objects.select_related('author').order_by('-created_at'),
        ),
    )


def hydrate_okr_detail(okr: Okr) -> Okr:
    """
    Донасыщает OKR вычисляемыми полями для детальной карточки.

    :param okr: Экземпляр цели OKR.
    :return: Обновлённый экземпляр OKR.
    """
    for key_result in okr.key_results.all():
        key_result.progress = calculate_progress(
            start_value=key_result.start_value,
            current_value=key_result.current_value,
            target_value=key_result.target_value,
        )

    okr.change_logs_for_okr = list(get_change_logs_for_okr(okr.id))
    return okr


def get_okr_by_id(okr_id: int) -> Okr:
    """
    Возвращает один OKR со всеми данными для детальной карточки.

    :param okr_id: Идентификатор цели OKR.
    :return: Экземпляр OKR с предзагруженными связанными объектами.
    """
    okr = get_okr_detail_queryset().get(id=okr_id)
    return hydrate_okr_detail(okr)


def get_change_logs_for_okr(okr_id: int) -> QuerySet[ChangeLog]:
    """
    Возвращает журнал изменений, связанный с целью OKR.

    :param okr_id: Идентификатор цели OKR.
    :return: QuerySet записей журнала изменений.
    """
    key_result_ids = list(KeyResult.objects.filter(okr_id=okr_id).values_list('id', flat=True))
    check_in_ids = list(CheckIn.objects.filter(key_result__okr_id=okr_id).values_list('id', flat=True))
    comment_ids = list(Comment.objects.filter(okr_id=okr_id).values_list('id', flat=True))

    return (
        ChangeLog.objects.select_related('author')
        .filter(
            Q(entity_type=ChangeLogEntityType.OKR, entity_id=okr_id)
            | Q(entity_type=ChangeLogEntityType.KEY_RESULT, entity_id__in=key_result_ids)
            | Q(entity_type=ChangeLogEntityType.CHECK_IN, entity_id__in=check_in_ids)
            | Q(entity_type=ChangeLogEntityType.COMMENT, entity_id__in=comment_ids),
        )
        .order_by('-created_at', '-id')
    )
