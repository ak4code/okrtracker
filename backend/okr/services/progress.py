from decimal import ROUND_HALF_UP, Decimal

from okr.constants import PROGRESS_DONE, PROGRESS_LOW, MetricType
from okr.models import CheckIn, KeyResult, Okr


def calculate_progress(start_value: Decimal, current_value: Decimal, target_value: Decimal) -> Decimal:
    """
    Вычисляет прогресс ключевого результата по значениям метрики.

    :param start_value: Стартовое значение метрики.
    :param current_value: Текущее значение метрики.
    :param target_value: Целевое значение метрики.
    :return: Нормализованный прогресс в диапазоне от 0.0 до 1.0.
    """
    if target_value == start_value:
        progress = PROGRESS_DONE if current_value == target_value else PROGRESS_LOW
        return Decimal(progress).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    ratio = (current_value - start_value) / (target_value - start_value)
    clamped_ratio = min(max(ratio, Decimal('0')), Decimal('1'))
    return Decimal(clamped_ratio).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)


def apply_check_in_value(*, key_result: KeyResult, current_value: Decimal) -> Decimal:
    """
    Применяет check-in к текущему значению KR.

    :param key_result: Ключевой результат, к которому применяется check-in.
    :param current_value: Новое текущее значение KR.
    :return: Новое текущее значение KR.
    """
    if key_result.metric_type == MetricType.BOOLEAN:
        return current_value

    return current_value


def update_key_result_progress_from_check_in(check_in: CheckIn) -> KeyResult:
    """
    Обновляет значения и прогресс ключевого результата по check-in.

    :param check_in: Сохранённый check-in ключевого результата.
    :return: Обновлённый ключевой результат.
    """
    key_result = check_in.key_result
    key_result.current_value = apply_check_in_value(
        key_result=key_result,
        current_value=check_in.new_value,
    )
    key_result.save(update_fields=['current_value', 'updated_at'])
    return key_result


def update_okr_progress(okr: Okr) -> Okr:
    """
    Пересчитывает агрегированный прогресс OKR по максимальному значению достигнутого KR.

    :param okr: Цель OKR для пересчёта.
    :return: Обновлённая цель OKR.
    """
    key_results = list(okr.key_results.only('id', 'start_value', 'current_value', 'target_value', 'value'))
    if not key_results:
        okr.progress = Decimal('0.0')
        okr.save(update_fields=['progress', 'updated_at'])
        return okr

    completed_values = [
        Decimal(key_result.value)
        for key_result in key_results
        if calculate_progress(
            start_value=key_result.start_value,
            current_value=key_result.current_value,
            target_value=key_result.target_value,
        )
        >= PROGRESS_DONE
    ]
    okr.progress = max(completed_values, default=Decimal('0.0')).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    okr.save(update_fields=['progress', 'updated_at'])
    return okr


def apply_check_in_updates(check_in: CheckIn) -> None:
    """
    Применяет check-in к ключевому результату и обновляет агрегаты OKR.

    :param check_in: Сохранённый check-in ключевого результата.
    """
    key_result = update_key_result_progress_from_check_in(check_in=check_in)
    update_okr_progress(okr=key_result.okr)


def replay_check_ins_for_key_result(*, key_result: KeyResult, base_value: Decimal | None = None) -> KeyResult:
    """
    Полностью пересчитывает previous/current значения KR по всей истории check-in.

    :param key_result: Ключевой результат для пересчёта.
    :param base_value:
        Базовое значение до первого check-in. Если не передано, берётся из первого check-in
        или start_value.
    :return: Обновлённый ключевой результат.
    """
    check_ins = list(key_result.check_ins.order_by('created_at', 'id'))

    if not check_ins:
        key_result.current_value = key_result.start_value if base_value is None else base_value
        key_result.save(update_fields=['current_value', 'updated_at'])
        return key_result

    running_value = check_ins[0].previous_value if base_value is None else base_value
    for check_in in check_ins:
        check_in.previous_value = running_value
        running_value = apply_check_in_value(
            key_result=key_result,
            current_value=check_in.new_value,
        )
        check_in.save(update_fields=['previous_value'])

    key_result.current_value = running_value
    key_result.save(update_fields=['current_value', 'updated_at'])
    return key_result
