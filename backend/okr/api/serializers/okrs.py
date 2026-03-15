from rest_framework import serializers

from core.selectors import get_user_display_name
from okr.api.serializers.change_logs import ChangeLogSerializer
from okr.api.serializers.comments import CommentSerializer
from okr.api.serializers.common import OkrRelationsValidationMixin
from okr.api.serializers.key_results import KeyResultCreateSerializer, KeyResultSerializer
from okr.constants import OkrStatus
from okr.models import Okr
from okr.services.okrs import create_okr, update_okr


class OkrListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    owner = serializers.SerializerMethodField()
    team = serializers.CharField(source='team.name')
    quarter = serializers.CharField(source='period.name')
    status = serializers.CharField()
    progress = serializers.DecimalField(max_digits=2, decimal_places=1)
    updated_at = serializers.DateTimeField()
    key_results_count = serializers.IntegerField()
    completed_key_results_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()

    def get_owner(self, obj: Okr) -> str:
        """
        Возвращает имя владельца OKR.

        :param obj: Экземпляр цели OKR.
        :return: Имя и фамилия владельца или email.
        """
        return get_user_display_name(obj.owner)


class OkrDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    owner_id = serializers.IntegerField(source='owner.id')
    owner = serializers.SerializerMethodField()
    team_id = serializers.IntegerField(source='team.id')
    team = serializers.CharField(source='team.name')
    period_id = serializers.IntegerField(source='period.id')
    quarter = serializers.CharField(source='period.name')
    status = serializers.CharField()
    progress = serializers.DecimalField(max_digits=2, decimal_places=1)
    updated_at = serializers.DateTimeField()
    key_results = KeyResultSerializer(many=True)
    comments = CommentSerializer(many=True)
    change_logs = ChangeLogSerializer(source='change_logs_for_okr', many=True)

    def get_owner(self, obj: Okr) -> str:
        """
        Возвращает владельца OKR.

        :param obj: Экземпляр цели OKR.
        :return: Имя и фамилия владельца или email.
        """
        return get_user_display_name(obj.owner)


class OkrCreateSerializer(OkrRelationsValidationMixin, serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, default='')
    owner_id = serializers.IntegerField(min_value=1)
    team_id = serializers.IntegerField(min_value=1)
    period_id = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(choices=OkrStatus.choices, default=OkrStatus.DRAFT)
    key_results = KeyResultCreateSerializer(many=True)

    def validate_key_results(self, value: list[dict]) -> list[dict]:
        """
        Проверяет наличие хотя бы одного ключевого результата.

        :param value: Список ключевых результатов.
        :return: Провалидированный список ключевых результатов.
        """
        if not value:
            raise serializers.ValidationError('Добавьте хотя бы один ключевой результат.')
        return value

    def create(self, validated_data: dict) -> Okr:
        """
        Создаёт новый OKR через service-слой.

        :param validated_data: Провалидированные данные OKR.
        :return: Созданная цель OKR.
        """
        request = self.context['request']
        return create_okr(
            title=validated_data['title'],
            description=validated_data['description'],
            owner_id=validated_data['owner_id'],
            team_id=validated_data['team_id'],
            period_id=validated_data['period_id'],
            status=validated_data['status'],
            created_by=request.user,
            key_results_data=validated_data['key_results'],
        )


class OkrUpdateSerializer(OkrRelationsValidationMixin, serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, default='')
    owner_id = serializers.IntegerField(min_value=1)
    team_id = serializers.IntegerField(min_value=1)
    period_id = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(choices=OkrStatus.choices, default=OkrStatus.DRAFT)

    def update(self, instance: Okr, validated_data: dict) -> Okr:
        """
        Обновляет цель OKR через service-слой.

        :param instance: Существующая цель OKR.
        :param validated_data: Провалидированные данные цели.
        :return: Обновлённая цель OKR.
        """
        return update_okr(
            okr=instance,
            title=validated_data['title'],
            description=validated_data['description'],
            owner_id=validated_data['owner_id'],
            team_id=validated_data['team_id'],
            period_id=validated_data['period_id'],
            status=validated_data['status'],
            updated_by=self.context['request'].user,
        )
