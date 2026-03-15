from django.db import transaction

from core.models import User
from okr.constants import ChangeLogAction, ChangeLogEntityType
from okr.models import ChangeLog, CheckIn, KeyResult
from okr.services.audit import build_change
from okr.services.progress import replay_check_ins_for_key_result, update_okr_progress


@transaction.atomic
def create_check_in(
    *,
    key_result: KeyResult,
    author: User,
    new_value,
    comment: str,
) -> CheckIn:
    """
    Создаёт check-in для ключевого результата.

    Дальнейший пересчёт прогресса и запись в аудит выполняются сигналами.

    :param key_result: Ключевой результат, к которому относится check-in.
    :param author: Пользователь, создавший check-in.
    :param new_value: Новое значение метрики.
    :param comment: Комментарий к обновлению.
    :return: Созданный check-in.
    """
    return CheckIn.objects.create(
        key_result=key_result,
        author=author,
        new_value=new_value,
        comment=comment,
    )


@transaction.atomic
def update_check_in(
    *,
    check_in: CheckIn,
    new_value,
    comment: str,
    updated_by: User,
) -> CheckIn:
    """
    Обновляет существующий check-in и пересчитывает цепочку значений KR.

    :param check_in: Экземпляр check-in.
    :param new_value: Новое значение check-in.
    :param comment: Новый комментарий.
    :param updated_by: Пользователь, обновляющий check-in.
    :return: Обновлённый check-in.
    """
    changes = [
        build_change(field='new_value', previous=check_in.new_value, current=new_value),
        build_change(field='comment', previous=check_in.comment, current=comment),
    ]
    check_in.new_value = new_value
    check_in.comment = comment
    check_in.save(update_fields=['new_value', 'comment', 'updated_at'])

    replay_check_ins_for_key_result(key_result=check_in.key_result)
    update_okr_progress(okr=check_in.key_result.okr)
    ChangeLog.objects.create(
        entity_type=ChangeLogEntityType.CHECK_IN,
        entity_id=check_in.id,
        action=ChangeLogAction.UPDATED,
        author=updated_by,
        payload={
            'key_result_id': check_in.key_result_id,
            'key_result_title': check_in.key_result.title,
            'previous_value': str(check_in.previous_value),
            'new_value': str(check_in.new_value),
            'comment': check_in.comment,
            'changes': [change for change in changes if change is not None],
        },
    )
    return check_in


@transaction.atomic
def delete_check_in(
    *,
    check_in: CheckIn,
    deleted_by: User,
) -> int:
    """
    Удаляет check-in и пересчитывает цепочку значений KR.

    :param check_in: Экземпляр check-in.
    :param deleted_by: Пользователь, удаляющий check-in.
    :return: Идентификатор связанного OKR.
    """
    key_result = check_in.key_result
    okr_id = key_result.okr_id
    has_earlier_check_ins = (
        key_result.check_ins.filter(created_at__lt=check_in.created_at).exists()
        or key_result.check_ins.filter(
            created_at=check_in.created_at,
            id__lt=check_in.id,
        ).exists()
    )
    base_value = check_in.previous_value if not has_earlier_check_ins else None

    ChangeLog.objects.create(
        entity_type=ChangeLogEntityType.CHECK_IN,
        entity_id=check_in.id,
        action=ChangeLogAction.DELETED,
        author=deleted_by,
        payload={
            'key_result_id': key_result.id,
            'key_result_title': key_result.title,
            'previous_value': str(check_in.previous_value),
            'new_value': str(check_in.new_value),
            'comment': check_in.comment,
        },
    )
    check_in.delete()

    replay_check_ins_for_key_result(key_result=key_result, base_value=base_value)
    update_okr_progress(okr=key_result.okr)
    return okr_id
