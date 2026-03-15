from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import AutoTimestampMixin
from okr.constants import (
    ChangeLogAction,
    ChangeLogEntityType,
    MetricType,
    OkrStatus,
)
from okr.services.validators import validate_key_result_value


class Quarter(models.Model):
    """Описывает квартал OKR-планирования."""

    name = models.CharField(max_length=32, unique=True, verbose_name='Название')
    year = models.PositiveSmallIntegerField(verbose_name='Год')
    quarter = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='Квартал',
    )
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    is_active = models.BooleanField(default=False, verbose_name='Активный')

    class Meta:
        verbose_name = 'Квартал'
        verbose_name_plural = 'Кварталы'
        constraints = [
            models.UniqueConstraint(
                fields=['year', 'quarter'],
                name='unique_okr_quarter_per_year',
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        """
        Синхронизирует название квартала перед сохранением.

        :param args: Позиционные аргументы метода сохранения Django.
        :param kwargs: Именованные аргументы метода сохранения Django.
        """
        self.name = f'Q{self.quarter} {self.year}'
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Возвращает отображаемое название квартала.

        :return: Название квартала.
        """
        return self.name


class Okr(AutoTimestampMixin):
    """Описывает цель OKR команды на выбранный период."""

    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    owner = models.ForeignKey(
        'core.User',
        on_delete=models.PROTECT,
        related_name='owned_okrs',
        verbose_name='Ответственный',
    )
    team = models.ForeignKey(
        'core.Team',
        on_delete=models.PROTECT,
        related_name='okrs',
        verbose_name='Команда',
    )
    period = models.ForeignKey(
        'okr.Quarter',
        on_delete=models.PROTECT,
        related_name='okrs',
        verbose_name='Период',
    )
    status = models.CharField(
        max_length=32,
        choices=OkrStatus.choices,
        default=OkrStatus.DRAFT,
        verbose_name='Статус',
    )
    progress = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name='Прогресс',
    )
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.PROTECT,
        related_name='created_okrs',
        verbose_name='Создал',
    )
    archived_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата архивирования')

    class Meta:
        verbose_name = 'OKR'
        verbose_name_plural = 'OKR'

    def __str__(self) -> str:
        """
        Возвращает название цели OKR.

        :return: Название цели.
        """
        return self.title


class KeyResult(AutoTimestampMixin):
    """Описывает ключевой результат внутри цели OKR."""

    okr = models.ForeignKey(
        'okr.Okr',
        on_delete=models.CASCADE,
        related_name='key_results',
        verbose_name='OKR',
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    metric_type = models.CharField(
        max_length=32,
        choices=MetricType.choices,
        default=MetricType.NUMBER,
        verbose_name='Тип метрики',
    )
    start_value = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Стартовое значение')
    current_value = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Текущее значение')
    target_value = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Целевое значение')
    value = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=Decimal('0.3'),
        validators=[validate_key_result_value],
        verbose_name='Значение KR',
    )
    status = models.CharField(
        max_length=32,
        choices=OkrStatus.choices,
        default=OkrStatus.DRAFT,
        verbose_name='Статус',
    )

    class Meta:
        verbose_name = 'Ключевой результат'
        verbose_name_plural = 'Ключевые результаты'

    def __str__(self) -> str:
        """
        Возвращает название ключевого результата.

        :return: Название ключевого результата.
        """
        return self.title


class CheckIn(AutoTimestampMixin):
    """Фиксирует обновление прогресса ключевого результата."""

    key_result = models.ForeignKey(
        'okr.KeyResult',
        on_delete=models.CASCADE,
        related_name='check_ins',
        verbose_name='Ключевой результат',
    )
    author = models.ForeignKey(
        'core.User',
        on_delete=models.PROTECT,
        related_name='key_result_check_ins',
        verbose_name='Автор',
    )
    previous_value = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Предыдущее значение')
    new_value = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Новое значение')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Check-in'
        verbose_name_plural = 'Check-in'

    def save(self, *args, **kwargs) -> None:
        """
        Подставляет предыдущее значение ключевого результата перед сохранением check-in.

        :param args: Позиционные аргументы метода сохранения Django.
        :param kwargs: Именованные аргументы метода сохранения Django.
        """
        if self._state.adding:
            self.previous_value = self.key_result.current_value

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Возвращает краткое представление check-in.

        :return: Название check-in.
        """
        return f'{self.key_result} -> {self.new_value}'


class Comment(AutoTimestampMixin):
    """Хранит комментарии к цели OKR."""

    okr = models.ForeignKey(
        'okr.Okr',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='OKR',
    )
    author = models.ForeignKey(
        'core.User',
        on_delete=models.PROTECT,
        related_name='okr_comments',
        verbose_name='Автор',
    )
    text = models.TextField(verbose_name='Текст')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        """
        Возвращает краткое представление комментария.

        :return: Текст комментария.
        """
        return self.text[:50]


class ChangeLog(AutoTimestampMixin):
    """Хранит аудит ключевых действий над OKR-сущностями."""

    entity_type = models.CharField(max_length=32, choices=ChangeLogEntityType.choices, verbose_name='Тип сущности')
    entity_id = models.PositiveBigIntegerField(verbose_name='Идентификатор сущности')
    action = models.CharField(max_length=32, choices=ChangeLogAction.choices, verbose_name='Действие')
    author = models.ForeignKey(
        'core.User',
        on_delete=models.PROTECT,
        related_name='change_logs',
        verbose_name='Автор',
    )
    payload = models.JSONField(default=dict, verbose_name='Данные')

    class Meta:
        verbose_name = 'История изменений'
        verbose_name_plural = 'История изменений'

    def __str__(self) -> str:
        """
        Возвращает краткое описание записи аудита.

        :return: Описание записи аудита.
        """
        return f'{self.get_entity_type_display()}: {self.get_action_display()}'
