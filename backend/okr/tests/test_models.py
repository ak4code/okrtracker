from decimal import Decimal

import pytest
from model_bakery import baker

from okr.models import ChangeLog, ChangeLogAction, ChangeLogEntityType, CheckIn, Comment, KeyResult
from okr.services.progress import calculate_progress

pytestmark = [pytest.mark.django_db]


def test_check_in_updates_key_result_and_okr_progress(owner, model_okr, model_key_result):
    """
    Arrange: создаём OKR с двумя ключевыми результатами и исходным прогрессом.
    Act: сохраняем check-in для первого ключевого результата.
    Assert: обновляются current_value, progress ключевого результата и агрегированный progress у OKR.
    """
    baker.make(
        KeyResult,
        okr=model_okr,
        start_value=Decimal('0.00'),
        current_value=Decimal('80.00'),
        target_value=Decimal('100.00'),
        value=Decimal('0.7'),
    )

    check_in = baker.make(
        CheckIn,
        key_result=model_key_result,
        author=owner,
        previous_value=Decimal('0.00'),
        new_value=Decimal('60.00'),
        comment='Обновили результат.',
    )

    model_key_result.refresh_from_db()
    model_okr.refresh_from_db()

    assert check_in.previous_value == Decimal('0.00')
    assert model_key_result.current_value == Decimal('60.00')
    assert calculate_progress(
        start_value=model_key_result.start_value,
        current_value=model_key_result.current_value,
        target_value=model_key_result.target_value,
    ) == Decimal('0.6')
    assert model_okr.progress == Decimal('0.0')


def test_okr_progress_uses_max_completed_key_result_value(owner, model_okr):
    """
    Arrange: создаём два KR со значениями 0.3 и 0.7, из которых завершён только второй.
    Act: сохраняем check-in для завершённого KR.
    Assert: progress OKR становится равным максимальному значению завершённого KR.
    """
    lower_key_result = baker.make(
        KeyResult,
        okr=model_okr,
        start_value=Decimal('0.00'),
        current_value=Decimal('0.00'),
        target_value=Decimal('100.00'),
        value=Decimal('0.3'),
    )
    higher_key_result = baker.make(
        KeyResult,
        okr=model_okr,
        start_value=Decimal('0.00'),
        current_value=Decimal('100.00'),
        target_value=Decimal('100.00'),
        value=Decimal('0.7'),
    )

    baker.make(
        CheckIn,
        key_result=higher_key_result,
        author=owner,
        previous_value=Decimal('0.00'),
        new_value=Decimal('100.00'),
        comment='KR 0.7 закрыт.',
    )

    lower_key_result.refresh_from_db()
    higher_key_result.refresh_from_db()
    model_okr.refresh_from_db()

    assert calculate_progress(
        start_value=lower_key_result.start_value,
        current_value=lower_key_result.current_value,
        target_value=lower_key_result.target_value,
    ) == Decimal('0.0')
    assert calculate_progress(
        start_value=higher_key_result.start_value,
        current_value=higher_key_result.current_value,
        target_value=higher_key_result.target_value,
    ) == Decimal('1.0')
    assert model_okr.progress == Decimal('0.7')


def test_check_in_creates_change_log(owner, model_key_result):
    """
    Arrange: создаём ключевой результат и автора обновления.
    Act: сохраняем check-in.
    Assert: в журнале изменений появляется запись с данными обновления.
    """
    check_in = baker.make(
        CheckIn,
        key_result=model_key_result,
        author=owner,
        previous_value=Decimal('0.00'),
        new_value=Decimal('25.00'),
        comment='Первый check-in.',
    )

    change_log = ChangeLog.objects.get(
        entity_type=ChangeLogEntityType.CHECK_IN,
        entity_id=check_in.id,
    )

    assert change_log.action == ChangeLogAction.CREATED
    assert change_log.author == owner
    assert change_log.payload['new_value'] == '25.00'


@pytest.mark.parametrize(
    ('text', 'action'),
    [
        ('Первый комментарий.', ChangeLogAction.CREATED),
        ('Обновлённый комментарий.', ChangeLogAction.UPDATED),
    ],
)
def test_comment_creates_change_log(owner, model_okr, text, action):
    """
    Arrange: создаём комментарий к OKR и при необходимости обновляем его текст.
    Act: сохраняем комментарий в базе.
    Assert: в журнале изменений создаётся запись с корректным действием и текстом.
    """
    comment = baker.make(Comment, okr=model_okr, author=owner, text='Черновик комментария.')

    if action == ChangeLogAction.UPDATED:
        comment.text = text
        comment.save(update_fields=['text', 'updated_at'])

    change_log = ChangeLog.objects.filter(
        entity_type=ChangeLogEntityType.COMMENT,
        entity_id=comment.id,
    ).latest('created_at')

    expected_text = text if action == ChangeLogAction.UPDATED else 'Черновик комментария.'

    assert change_log.action == action
    assert change_log.author == owner
    assert change_log.payload['text'] == expected_text
