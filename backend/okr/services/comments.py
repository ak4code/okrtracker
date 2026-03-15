from okr.models import Comment, Okr


def create_comment(*, okr: Okr, author, text: str) -> Comment:
    """
    Создаёт комментарий к цели OKR.

    :param okr: Цель, к которой относится комментарий.
    :param author: Пользователь, оставивший комментарий.
    :param text: Текст комментария.
    :return: Созданный комментарий.
    """
    return Comment.objects.create(
        okr=okr,
        author=author,
        text=text,
    )
