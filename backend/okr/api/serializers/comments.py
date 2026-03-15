from rest_framework import serializers

from core.selectors import get_user_display_name
from okr.models import Comment
from okr.services.comments import create_comment


class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author = serializers.SerializerMethodField()
    text = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_author(self, obj: Comment) -> str:
        """
        Возвращает автора комментария.

        :param obj: Экземпляр комментария.
        :return: Имя и фамилия автора или email.
        """
        return get_user_display_name(obj.author)


class CommentCreateSerializer(serializers.Serializer):
    text = serializers.CharField()

    def validate_text(self, value: str) -> str:
        """
        Проверяет, что текст комментария не пуст после trim.

        :param value: Текст комментария.
        :return: Нормализованный текст комментария.
        """
        normalized_value = value.strip()
        if not normalized_value:
            raise serializers.ValidationError('Комментарий не может быть пустым.')

        return normalized_value

    def create(self, validated_data: dict) -> Comment:
        """
        Создаёт комментарий через service-слой.

        :param validated_data: Провалидированные данные комментария.
        :return: Созданный комментарий.
        """
        return create_comment(
            okr=self.context['okr'],
            author=self.context['request'].user,
            text=validated_data['text'],
        )
