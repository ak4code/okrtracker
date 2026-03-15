def build_change(*, field: str, previous, current, label: str | None = None) -> dict | None:
    """
    Собирает описание изменения поля для payload аудита.

    :param field: Системное имя поля.
    :param previous: Предыдущее значение поля.
    :param current: Новое значение поля.
    :param label: Человекочитаемая подпись поля.
    :return: Словарь изменения или None, если значения не изменились.
    """
    previous_value = '' if previous is None else str(previous)
    current_value = '' if current is None else str(current)
    if previous_value == current_value:
        return None

    payload = {
        'field': field,
        'from': previous_value,
        'to': current_value,
    }
    if label:
        payload['label'] = label
    return payload
