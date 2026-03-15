from decimal import Decimal

from django.db import transaction

from core.models import User
from core.selectors import get_team_by_id, get_user_by_id, get_user_display_name
from okr.constants import (
    KR_VALUE_CONFIDENT,
    KR_VALUE_LOW,
    PROGRESS_DONE,
    ChangeLogAction,
    ChangeLogEntityType,
    OkrStatus,
)
from okr.models import ChangeLog, KeyResult, Okr
from okr.selectors import get_quarter_by_id
from okr.services.audit import build_change
from okr.services.progress import calculate_progress, update_okr_progress


def get_key_result_value_by_position(position: int) -> Decimal:
    """
    Возвращает фиксированное значение KR по его позиции внутри OKR.

    :param position: Позиция ключевого результата, начиная с 1.
    :return: Значение KR на шкале 0.3 / 0.7 / 1.0.
    """
    if position == 1:
        return KR_VALUE_LOW
    if position == 2:
        return KR_VALUE_CONFIDENT
    return PROGRESS_DONE


@transaction.atomic
def create_okr(
    *,
    title: str,
    description: str,
    owner_id: int,
    team_id: int,
    period_id: int,
    status: str,
    created_by: User,
    key_results_data: list[dict],
) -> Okr:
    """
    Создаёт OKR с ключевыми результатами и записью аудита.

    :param title: Название цели OKR.
    :param description: Описание цели OKR.
    :param owner_id: Идентификатор владельца цели.
    :param team_id: Идентификатор команды.
    :param period_id: Идентификатор квартала.
    :param status: Статус цели OKR.
    :param created_by: Пользователь, создающий цель.
    :param key_results_data: Данные ключевых результатов.
    :return: Созданная цель OKR.
    """
    owner = get_user_by_id(user_id=owner_id)
    team = get_team_by_id(team_id=team_id)
    period = get_quarter_by_id(quarter_id=period_id)

    okr = Okr.objects.create(
        title=title,
        description=description,
        owner=owner,
        team=team,
        period=period,
        status=status,
        created_by=created_by,
        archived_at=None,
    )

    for index, key_result_data in enumerate(key_results_data, start=1):
        start_value = key_result_data['start_value']
        current_value = key_result_data['current_value']
        target_value = key_result_data['target_value']
        KeyResult.objects.create(
            okr=okr,
            title=key_result_data['title'],
            description=key_result_data['description'],
            metric_type=key_result_data['metric_type'],
            start_value=start_value,
            current_value=current_value,
            target_value=target_value,
            value=get_key_result_value_by_position(index),
            status=key_result_data['status'],
        )

    update_okr_progress(okr=okr)
    ChangeLog.objects.create(
        entity_type=ChangeLogEntityType.OKR,
        entity_id=okr.id,
        action=ChangeLogAction.CREATED,
        author=created_by,
        payload={
            'title': okr.title,
            'owner_id': owner.id,
            'team_id': team.id,
            'period_id': period.id,
            'status': okr.status,
            'key_results_count': len(key_results_data),
        },
    )
    return okr


@transaction.atomic
def update_okr(
    *,
    okr: Okr,
    title: str,
    description: str,
    owner_id: int,
    team_id: int,
    period_id: int,
    status: str,
    updated_by: User,
) -> Okr:
    """
    Обновляет OKR и пишет запись в аудит.

    :param okr: Экземпляр цели OKR.
    :param title: Новое название цели.
    :param description: Новое описание цели.
    :param owner_id: Идентификатор владельца цели.
    :param team_id: Идентификатор команды.
    :param period_id: Идентификатор квартала.
    :param status: Новый статус цели.
    :param updated_by: Пользователь, обновляющий цель.
    :return: Обновлённая цель OKR.
    """
    owner = get_user_by_id(user_id=owner_id)
    team = get_team_by_id(team_id=team_id)
    period = get_quarter_by_id(quarter_id=period_id)
    previous_owner = get_user_display_name(okr.owner)
    current_owner = get_user_display_name(owner)
    changes = [
        build_change(field='title', label='Название', previous=okr.title, current=title),
        build_change(field='description', label='Описание', previous=okr.description, current=description),
        build_change(field='owner', label='Владелец', previous=previous_owner, current=current_owner),
        build_change(field='team', label='Команда', previous=okr.team.name, current=team.name),
        build_change(field='period', label='Квартал', previous=okr.period.name, current=period.name),
        build_change(
            field='status',
            label='Статус',
            previous=OkrStatus(okr.status).label,
            current=OkrStatus(status).label,
        ),
    ]

    okr.title = title
    okr.description = description
    okr.owner = owner
    okr.team = team
    okr.period = period
    okr.status = status
    okr.archived_at = None
    okr.save(
        update_fields=[
            'title',
            'description',
            'owner',
            'team',
            'period',
            'status',
            'archived_at',
            'updated_at',
        ],
    )

    ChangeLog.objects.create(
        entity_type=ChangeLogEntityType.OKR,
        entity_id=okr.id,
        action=ChangeLogAction.UPDATED,
        author=updated_by,
        payload={
            'title': okr.title,
            'changes': [change for change in changes if change is not None],
        },
    )
    return okr


@transaction.atomic
def create_key_result(
    *,
    okr: Okr,
    title: str,
    description: str,
    metric_type: str,
    start_value,
    current_value,
    target_value,
    status: str,
    created_by: User,
) -> KeyResult:
    """
    Создаёт новый ключевой результат для существующего OKR.

    :param okr: Экземпляр цели OKR.
    :param title: Название ключевого результата.
    :param description: Описание ключевого результата.
    :param metric_type: Тип метрики.
    :param start_value: Стартовое значение метрики.
    :param current_value: Текущее значение метрики.
    :param target_value: Целевое значение метрики.
    :param status: Статус ключевого результата.
    :param created_by: Пользователь, создающий ключевой результат.
    :return: Созданный ключевой результат.
    """
    next_position = okr.key_results.count() + 1
    key_result = KeyResult.objects.create(
        okr=okr,
        title=title,
        description=description,
        metric_type=metric_type,
        start_value=start_value,
        current_value=current_value,
        target_value=target_value,
        value=get_key_result_value_by_position(next_position),
        status=status,
    )

    progress = calculate_progress(
        start_value=start_value,
        current_value=current_value,
        target_value=target_value,
    )
    update_okr_progress(okr=okr)
    ChangeLog.objects.create(
        entity_type=ChangeLogEntityType.KEY_RESULT,
        entity_id=key_result.id,
        action=ChangeLogAction.CREATED,
        author=created_by,
        payload={
            'okr_id': okr.id,
            'title': key_result.title,
            'metric_type': key_result.metric_type,
            'status': key_result.status,
            'value': str(key_result.value),
            'progress': str(progress),
        },
    )
    return key_result


@transaction.atomic
def update_key_result(
    *,
    key_result: KeyResult,
    title: str,
    description: str,
    value,
    metric_type: str,
    start_value,
    current_value,
    target_value,
    status: str,
    updated_by: User,
) -> KeyResult:
    """
    Обновляет ключевой результат и связанные агрегаты OKR.

    :param key_result: Экземпляр ключевого результата.
    :param title: Новое название ключевого результата.
    :param description: Новое описание ключевого результата.
    :param value: Новое значение KR на шкале.
    :param metric_type: Тип метрики.
    :param start_value: Стартовое значение метрики.
    :param current_value: Текущее значение метрики.
    :param target_value: Целевое значение метрики.
    :param status: Новый статус ключевого результата.
    :param updated_by: Пользователь, обновляющий ключевой результат.
    :return: Обновлённый ключевой результат.
    """
    changes = [
        build_change(field='title', label='Название', previous=key_result.title, current=title),
        build_change(
            field='description',
            label='Описание',
            previous=key_result.description,
            current=description,
        ),
        build_change(
            field='value',
            label='Значение KR',
            previous=key_result.value,
            current=value,
        ),
        build_change(
            field='metric_type',
            label='Тип метрики',
            previous=key_result.get_metric_type_display(),
            current=dict(KeyResult._meta.get_field('metric_type').choices)[metric_type],
        ),
        build_change(
            field='start_value',
            label='Старт',
            previous=key_result.start_value,
            current=start_value,
        ),
        build_change(
            field='current_value',
            label='Текущее значение',
            previous=key_result.current_value,
            current=current_value,
        ),
        build_change(
            field='target_value',
            label='Цель',
            previous=key_result.target_value,
            current=target_value,
        ),
        build_change(
            field='status',
            label='Статус',
            previous=key_result.get_status_display(),
            current=OkrStatus(status).label,
        ),
    ]
    key_result.title = title
    key_result.description = description
    key_result.value = value
    key_result.metric_type = metric_type
    key_result.start_value = start_value
    key_result.current_value = current_value
    key_result.target_value = target_value
    key_result.status = status
    progress = calculate_progress(
        start_value=start_value,
        current_value=current_value,
        target_value=target_value,
    )
    key_result.save(
        update_fields=[
            'title',
            'description',
            'value',
            'metric_type',
            'start_value',
            'current_value',
            'target_value',
            'status',
            'updated_at',
        ],
    )

    update_okr_progress(okr=key_result.okr)
    ChangeLog.objects.create(
        entity_type=ChangeLogEntityType.KEY_RESULT,
        entity_id=key_result.id,
        action=ChangeLogAction.UPDATED,
        author=updated_by,
        payload={
            'okr_id': key_result.okr_id,
            'title': key_result.title,
            'changes': [change for change in changes if change is not None],
            'progress': str(progress),
        },
    )
    return key_result
