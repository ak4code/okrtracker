from decimal import Decimal

from django.db import models


class OkrStatus(models.TextChoices):
    """Определяет допустимые статусы OKR и ключевых результатов."""

    DRAFT = 'draft', 'Черновик'
    ON_TRACK = 'on_track', 'В графике'
    AT_RISK = 'at_risk', 'Есть риск'
    COMPLETED = 'completed', 'Завершён'


class MetricType(models.TextChoices):
    """Определяет тип метрики ключевого результата."""

    NUMBER = 'number', 'Число'
    PERCENT = 'percent', 'Процент'
    CURRENCY = 'currency', 'Деньги'
    BOOLEAN = 'boolean', 'Да/Нет'


class ChangeLogEntityType(models.TextChoices):
    """Определяет тип сущности в журнале изменений."""

    OKR = 'okr', 'OKR'
    KEY_RESULT = 'key_result', 'Ключевой результат'
    CHECK_IN = 'check_in', 'Check-in'
    COMMENT = 'comment', 'Комментарий'


class ChangeLogAction(models.TextChoices):
    """Определяет тип действия в журнале изменений."""

    CREATED = 'created', 'Создание'
    UPDATED = 'updated', 'Изменение'
    DELETED = 'deleted', 'Удаление'


PROGRESS_LOW = Decimal('0.0')
KR_VALUE_LOW = Decimal('0.3')
KR_VALUE_CONFIDENT = Decimal('0.7')
PROGRESS_DONE = Decimal('1.0')
