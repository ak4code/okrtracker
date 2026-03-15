from rest_framework import serializers

from core.selectors import get_user_display_name
from okr.models import ChangeLog, CheckIn, Comment, KeyResult, Okr


class ChangeLogSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    entity_type = serializers.CharField()
    entity_id = serializers.IntegerField()
    entity_label = serializers.SerializerMethodField()
    entity_name = serializers.SerializerMethodField()
    action = serializers.CharField()
    author = serializers.SerializerMethodField()
    payload = serializers.JSONField()
    details = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_author(self, obj: ChangeLog) -> str:
        """
        Возвращает автора записи аудита.

        :param obj: Экземпляр записи журнала изменений.
        :return: Имя и фамилия автора или email.
        """
        return get_user_display_name(obj.author)

    def get_entity_label(self, obj: ChangeLog) -> str:
        """
        Возвращает отображаемое название типа сущности журнала.

        :param obj: Экземпляр записи журнала изменений.
        :return: Название типа сущности.
        """
        return obj.get_entity_type_display()

    def get_entity_name(self, obj: ChangeLog) -> str:
        """
        Возвращает краткое имя изменённой сущности.

        :param obj: Экземпляр записи журнала изменений.
        :return: Имя сущности или пустая строка.
        """
        payload = obj.payload or {}
        if obj.entity_type in {'okr', 'key_result'}:
            return str(payload.get('title') or '')
        if obj.entity_type == 'check_in':
            return str(payload.get('key_result_title') or '')
        return ''

    def _get_model_for_entity(self, entity_type: str):
        """
        Возвращает модель, связанную с типом сущности журнала.

        :param entity_type: Тип сущности.
        :return: Класс модели или None.
        """
        mapping = {
            'okr': Okr,
            'key_result': KeyResult,
            'check_in': CheckIn,
            'comment': Comment,
        }
        return mapping.get(entity_type)

    def _get_field_label(self, obj: ChangeLog, field_name: str) -> str:
        """
        Возвращает verbose_name поля модели, если оно существует.

        :param obj: Экземпляр записи журнала изменений.
        :param field_name: Системное имя поля.
        :return: Человекочитаемая подпись поля.
        """
        model_class = self._get_model_for_entity(obj.entity_type)
        if model_class is None:
            return field_name

        try:
            return str(model_class._meta.get_field(field_name).verbose_name)
        except Exception:
            return field_name

    def get_details(self, obj: ChangeLog) -> list[str]:
        """
        Возвращает человекочитаемое описание изменённых полей.

        :param obj: Экземпляр записи журнала изменений.
        :return: Список строк для отображения в интерфейсе.
        """
        payload = obj.payload or {}
        changes = payload.get('changes')
        if isinstance(changes, list):
            details = []
            for item in changes:
                field = str(item.get('field') or '')
                label = item.get('label') or (self._get_field_label(obj, field) if field else '')
                previous = item.get('from', '')
                current = item.get('to', '')
                if label:
                    details.append(f'{label}: {previous} -> {current}')
            if details:
                return details

        if obj.entity_type == 'check_in':
            details = [f'Значение check-in: {payload.get("new_value", "")}']
            comment = payload.get('comment')
            if comment:
                details.append(f'Комментарий: {comment}')
            return details

        if obj.entity_type == 'comment':
            text = str(payload.get('text') or '').strip()
            return [f'Комментарий: {text}'] if text else []

        fallback_details = []
        for key, value in payload.items():
            if key in {'okr_id', 'key_result_id', 'title'}:
                continue
            fallback_details.append(f'{key}: {value}')
        return fallback_details
