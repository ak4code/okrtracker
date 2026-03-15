from rest_framework import serializers

from core.models import Team, User
from core.selectors import get_team_by_id, get_user_by_id
from okr.constants import MetricType
from okr.models import Quarter
from okr.selectors import get_quarter_by_id


def validate_metric_values(*, metric_type: str, start_value, current_value, target_value) -> None:
    """
    Проверяет значения метрики ключевого результата.

    :param metric_type: Тип метрики.
    :param start_value: Стартовое значение.
    :param current_value: Текущее значение.
    :param target_value: Целевое значение.
    :raises serializers.ValidationError: Если значения не соответствуют типу метрики.
    """
    if metric_type != MetricType.BOOLEAN:
        return

    values = {start_value, current_value, target_value}
    if values - {0, 1}:
        raise serializers.ValidationError(
            {'metric_type': 'Для булевой метрики допускаются только значения 0 и 1.'},
        )


class OkrRelationsValidationMixin:
    """Содержит общую валидацию связей OKR."""

    def validate_owner_id(self, value: int) -> int:
        """
        Проверяет существование владельца цели.

        :param value: Идентификатор пользователя.
        :return: Идентификатор существующего пользователя.
        """
        try:
            get_user_by_id(user_id=value)
        except User.DoesNotExist as error:
            raise serializers.ValidationError('Пользователь не найден.') from error
        return value

    def validate_team_id(self, value: int) -> int:
        """
        Проверяет существование команды.

        :param value: Идентификатор команды.
        :return: Идентификатор существующей команды.
        """
        try:
            get_team_by_id(team_id=value)
        except Team.DoesNotExist as error:
            raise serializers.ValidationError('Команда не найдена.') from error
        return value

    def validate_period_id(self, value: int) -> int:
        """
        Проверяет существование квартала.

        :param value: Идентификатор квартала.
        :return: Идентификатор существующего квартала.
        """
        try:
            get_quarter_by_id(quarter_id=value)
        except Quarter.DoesNotExist as error:
            raise serializers.ValidationError('Квартал не найден.') from error
        return value
