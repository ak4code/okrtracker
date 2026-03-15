from rest_framework import serializers

from okr.models import Quarter
from okr.services.quarters import create_quarter, update_quarter


class QuarterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    year = serializers.IntegerField()
    quarter = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_active = serializers.BooleanField()


class QuarterCreateSerializer(serializers.Serializer):
    year = serializers.IntegerField(min_value=2000, max_value=3000)
    quarter = serializers.IntegerField(min_value=1, max_value=4)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_active = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs: dict) -> dict:
        """
        Проверяет корректность данных нового квартала.

        :param attrs: Данные сериализатора после преобразования типов.
        :return: Провалидированные данные квартала.
        """
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError({'end_date': 'Дата окончания должна быть не раньше даты начала.'})

        existing_quarter = Quarter.objects.filter(year=attrs['year'], quarter=attrs['quarter'])
        if self.instance is not None:
            existing_quarter = existing_quarter.exclude(id=self.instance.id)

        if existing_quarter.exists():
            raise serializers.ValidationError({'quarter': 'Квартал с таким годом уже существует.'})

        return attrs

    def create(self, validated_data: dict):
        """
        Создаёт новый квартал через service-слой.

        :param validated_data: Провалидированные данные квартала.
        :return: Созданный квартал.
        """
        return create_quarter(
            year=validated_data['year'],
            quarter_number=validated_data['quarter'],
            start_date=validated_data['start_date'],
            end_date=validated_data['end_date'],
            is_active=validated_data['is_active'],
        )

    def update(self, instance: Quarter, validated_data: dict) -> Quarter:
        """
        Обновляет квартал через service-слой.

        :param instance: Существующий квартал.
        :param validated_data: Провалидированные данные квартала.
        :return: Обновлённый квартал.
        """
        return update_quarter(
            quarter=instance,
            year=validated_data['year'],
            quarter_number=validated_data['quarter'],
            start_date=validated_data['start_date'],
            end_date=validated_data['end_date'],
            is_active=validated_data['is_active'],
        )
