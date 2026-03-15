from rest_framework import serializers

from core.selectors import get_user_display_name
from okr.constants import MetricType
from okr.models import CheckIn, KeyResult
from okr.services.checkins import create_check_in, update_check_in


class CheckInSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='created_at')
    value = serializers.DecimalField(source='new_value', max_digits=14, decimal_places=2)
    note = serializers.CharField(source='comment')

    def get_author(self, obj: CheckIn) -> str:
        """
        Возвращает автора check-in.

        :param obj: Экземпляр check-in.
        :return: Имя и фамилия автора или email.
        """
        return get_user_display_name(obj.author)


class CheckInCreateSerializer(serializers.Serializer):
    new_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    comment = serializers.CharField(allow_blank=True, default='')

    def validate(self, attrs: dict) -> dict:
        """
        Проверяет корректность данных check-in для выбранной метрики.

        :param attrs: Данные сериализатора после преобразования типов.
        :return: Провалидированные данные check-in.
        """
        key_result: KeyResult = self.context['key_result']

        if key_result.metric_type == MetricType.BOOLEAN:
            if attrs['new_value'] not in {0, 1}:
                raise serializers.ValidationError(
                    {'new_value': 'Для булевой метрики допускаются только значения 0 и 1.'},
                )

            if key_result.check_ins.exists():
                raise serializers.ValidationError(
                    {'new_value': 'Для булевого KR можно создать только один check-in.'},
                )

        return attrs

    def create(self, validated_data: dict) -> CheckIn:
        """
        Создаёт новый check-in через service-слой.

        :param validated_data: Провалидированные данные check-in.
        :return: Созданный check-in.
        """
        return create_check_in(
            key_result=self.context['key_result'],
            author=self.context['request'].user,
            new_value=validated_data['new_value'],
            comment=validated_data['comment'],
        )


class CheckInUpdateSerializer(serializers.Serializer):
    new_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    comment = serializers.CharField(allow_blank=True, default='')

    def validate(self, attrs: dict) -> dict:
        """
        Проверяет корректность данных обновления check-in.

        :param attrs: Данные сериализатора после преобразования типов.
        :return: Провалидированные данные check-in.
        """
        check_in: CheckIn = self.instance
        key_result = check_in.key_result

        if key_result.metric_type == MetricType.BOOLEAN and attrs['new_value'] not in {0, 1}:
            raise serializers.ValidationError(
                {'new_value': 'Для булевой метрики допускаются только значения 0 и 1.'},
            )

        return attrs

    def update(self, instance: CheckIn, validated_data: dict) -> CheckIn:
        """
        Обновляет check-in через service-слой.

        :param instance: Существующий check-in.
        :param validated_data: Провалидированные данные check-in.
        :return: Обновлённый check-in.
        """
        return update_check_in(
            check_in=instance,
            new_value=validated_data['new_value'],
            comment=validated_data['comment'],
            updated_by=self.context['request'].user,
        )
