from rest_framework import serializers

from core.selectors import get_user_display_name
from okr.api.serializers.check_ins import CheckInSerializer
from okr.api.serializers.common import validate_metric_values
from okr.constants import MetricType, OkrStatus
from okr.models import KeyResult
from okr.services.okrs import create_key_result, update_key_result
from okr.services.validators import validate_key_result_value


class KeyResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    value = serializers.DecimalField(max_digits=2, decimal_places=1)
    owner = serializers.SerializerMethodField()
    metric_type = serializers.CharField()
    start = serializers.DecimalField(source='start_value', max_digits=14, decimal_places=2)
    current = serializers.DecimalField(source='current_value', max_digits=14, decimal_places=2)
    target = serializers.DecimalField(source='target_value', max_digits=14, decimal_places=2)
    unit = serializers.SerializerMethodField()
    status = serializers.CharField()
    progress = serializers.DecimalField(max_digits=2, decimal_places=1)
    last_check_in = serializers.DateTimeField(format='%Y-%m-%d', allow_null=True)
    history = CheckInSerializer(source='check_ins', many=True)

    def get_owner(self, obj: KeyResult) -> str:
        """
        Возвращает владельца ключевого результата.

        :param obj: Экземпляр ключевого результата.
        :return: Имя владельца OKR.
        """
        return get_user_display_name(obj.okr.owner)

    def get_unit(self, obj: KeyResult) -> str:
        """
        Возвращает отображаемую единицу измерения.

        :param obj: Экземпляр ключевого результата.
        :return: Единица измерения.
        """
        mapping = {
            'number': 'ед.',
            'percent': '%',
            'currency': '₽',
            'boolean': 'bool',
        }
        return mapping.get(obj.metric_type, 'ед.')


class KeyResultCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, default='')
    metric_type = serializers.ChoiceField(choices=MetricType.choices, default=MetricType.NUMBER)
    start_value = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, default='0.00')
    current_value = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    target_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    status = serializers.ChoiceField(choices=OkrStatus.choices, default=OkrStatus.DRAFT)

    def validate(self, attrs: dict) -> dict:
        """
        Проверяет корректность данных ключевого результата.

        :param attrs: Данные сериализатора после преобразования типов.
        :return: Провалидированные данные ключевого результата.
        """
        current_value = attrs.get('current_value', attrs['start_value'])
        attrs['current_value'] = current_value
        validate_metric_values(
            metric_type=attrs['metric_type'],
            start_value=attrs['start_value'],
            current_value=current_value,
            target_value=attrs['target_value'],
        )
        return attrs

    def create(self, validated_data: dict) -> KeyResult:
        """
        Создаёт новый ключевой результат через service-слой.

        :param validated_data: Провалидированные данные ключевого результата.
        :return: Созданный ключевой результат.
        """
        request = self.context['request']
        okr = self.context['okr']
        return create_key_result(
            okr=okr,
            title=validated_data['title'],
            description=validated_data['description'],
            metric_type=validated_data['metric_type'],
            start_value=validated_data['start_value'],
            current_value=validated_data['current_value'],
            target_value=validated_data['target_value'],
            status=validated_data['status'],
            created_by=request.user,
        )


class KeyResultUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, default='')
    value = serializers.DecimalField(max_digits=2, decimal_places=1)
    metric_type = serializers.ChoiceField(choices=MetricType.choices, default=MetricType.NUMBER)
    start_value = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, default='0.00')
    current_value = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    target_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    status = serializers.ChoiceField(choices=OkrStatus.choices, default=OkrStatus.DRAFT)

    def validate_value(self, value):
        """
        Проверяет допустимость значения KR.

        :param value: Значение KR на шкале 0.3 / 0.7 / 1.0.
        :return: Провалидированное значение KR.
        """
        validate_key_result_value(value)
        return value

    def validate(self, attrs: dict) -> dict:
        """
        Проверяет корректность данных ключевого результата.

        :param attrs: Данные сериализатора после преобразования типов.
        :return: Провалидированные данные ключевого результата.
        """
        current_value = attrs.get('current_value', attrs['start_value'])
        attrs['current_value'] = current_value
        validate_metric_values(
            metric_type=attrs['metric_type'],
            start_value=attrs['start_value'],
            current_value=current_value,
            target_value=attrs['target_value'],
        )
        return attrs

    def update(self, instance: KeyResult, validated_data: dict) -> KeyResult:
        """
        Обновляет ключевой результат через service-слой.

        :param instance: Существующий ключевой результат.
        :param validated_data: Провалидированные данные ключевого результата.
        :return: Обновлённый ключевой результат.
        """
        return update_key_result(
            key_result=instance,
            title=validated_data['title'],
            description=validated_data['description'],
            value=validated_data['value'],
            metric_type=validated_data['metric_type'],
            start_value=validated_data['start_value'],
            current_value=validated_data['current_value'],
            target_value=validated_data['target_value'],
            status=validated_data['status'],
            updated_by=self.context['request'].user,
        )
