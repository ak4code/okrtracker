from decimal import Decimal

from django.core.exceptions import ValidationError

from okr.constants import KR_VALUE_CONFIDENT, KR_VALUE_LOW, PROGRESS_DONE, PROGRESS_LOW


def validate_key_result_progress(value: Decimal) -> None:
    """
    Проверяет, что прогресс ключевого результата находится в диапазоне от 0 до 1.

    :param value: Проверяемое значение прогресса.
    :raises ValidationError: Если значение выходит за допустимый диапазон.
    """
    progress = Decimal(value)
    if progress < PROGRESS_LOW or progress > PROGRESS_DONE:
        raise ValidationError('Допустимые значения прогресса: от 0.0 до 1.0.')


def validate_key_result_value(value: Decimal) -> None:
    """
    Проверяет, что значение KR входит в допустимую шкалу 0.3, 0.7, 1.0.

    :param value: Проверяемое значение KR.
    :raises ValidationError: Если значение не входит в допустимую шкалу.
    """
    normalized_value = Decimal(value)
    if normalized_value not in (KR_VALUE_LOW, KR_VALUE_CONFIDENT, PROGRESS_DONE):
        raise ValidationError('Допустимые значения KR: 0.3, 0.7, 1.0.')
