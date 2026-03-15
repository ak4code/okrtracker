from django.db.models.signals import post_save
from django.dispatch import receiver

from okr.models import ChangeLog, ChangeLogAction, ChangeLogEntityType, CheckIn, Comment
from okr.services.progress import apply_check_in_updates


@receiver(post_save, sender=CheckIn)
def handle_check_in_created(sender, instance: CheckIn, created: bool, **kwargs) -> None:
    """
    Применяет check-in и пишет запись аудита после создания.

    :param sender: Модель-источник сигнала.
    :param instance: Сохранённый check-in.
    :param created: Признак нового объекта.
    :param kwargs: Дополнительные аргументы сигнала.
    """
    if not created:
        return

    apply_check_in_updates(check_in=instance)
    ChangeLog.objects.create(
        entity_type=ChangeLogEntityType.CHECK_IN,
        entity_id=instance.id,
        action=ChangeLogAction.CREATED,
        author=instance.author,
        payload={
            'key_result_id': instance.key_result_id,
            'key_result_title': instance.key_result.title,
            'previous_value': str(instance.previous_value),
            'new_value': str(instance.new_value),
            'comment': instance.comment,
        },
    )


@receiver(post_save, sender=Comment)
def handle_comment_saved(sender, instance: Comment, created: bool, **kwargs) -> None:
    """
    Пишет запись аудита после сохранения комментария.

    :param sender: Модель-источник сигнала.
    :param instance: Сохранённый комментарий.
    :param created: Признак нового объекта.
    :param kwargs: Дополнительные аргументы сигнала.
    """
    ChangeLog.objects.create(
        entity_type=ChangeLogEntityType.COMMENT,
        entity_id=instance.id,
        action=ChangeLogAction.CREATED if created else ChangeLogAction.UPDATED,
        author=instance.author,
        payload={
            'okr_id': instance.okr_id,
            'text': instance.text,
        },
    )
