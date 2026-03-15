from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as DjangoGroup
from django.db import models
from django.utils import timezone


class AutoTimestampMixin(models.Model):
    """Добавляет автоматические временные метки создания и обновления."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        abstract = True


class Group(DjangoGroup):
    """Проксирует встроенную модель групп Django в приложение core."""

    class Meta:
        proxy = True
        app_label = 'core'
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Role(AutoTimestampMixin):
    """Хранит бизнес-роли, используемые внутри продукта."""

    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    code = models.SlugField(max_length=64, unique=True, verbose_name='Код')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self) -> str:
        """
        Возвращает отображаемое название роли.

        :return: Название роли.
        """
        return self.name


class Team(AutoTimestampMixin):
    """Хранит продуктовые и инженерные команды."""

    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    code = models.SlugField(max_length=64, unique=True, verbose_name='Код')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

    def __str__(self) -> str:
        """
        Возвращает отображаемое название команды.

        :return: Название команды.
        """
        return self.name


class UserManager(BaseUserManager):
    """Управляет созданием пользователей и суперпользователей."""

    use_in_migrations = True

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        """
        Создаёт обычного пользователя с логином по email.

        :param email: Email пользователя, используемый как логин.
        :param password: Пароль пользователя.
        :return: Созданный пользователь.
        :raises ValueError: Если email не передан.
        """
        if not email:
            raise ValueError('Необходимо указать email.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        """
        Создаёт суперпользователя с полным набором прав.

        :param email: Email суперпользователя, используемый как логин.
        :param password: Пароль суперпользователя.
        :return: Созданный суперпользователь.
        :raises ValueError: Если обязательные флаги суперпользователя заданы неверно.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractUser, AutoTimestampMixin):
    """Описывает пользователя приложения."""

    username = None
    password = models.CharField(max_length=128, verbose_name='Пароль')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='Последний вход')
    is_superuser = models.BooleanField(
        default=False,
        help_text='Указывает, что пользователь имеет все права без явного назначения.',
        verbose_name='Суперпользователь',
    )
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Фамилия')
    is_staff = models.BooleanField(
        default=False,
        help_text='Указывает, может ли пользователь входить в административную панель.',
        verbose_name='Доступ в админку',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Определяет, считается ли пользователь активным.',
        verbose_name='Активен',
    )
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Дата регистрации')
    email = models.EmailField(unique=True, verbose_name='Email')
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text='Группы, к которым принадлежит пользователь.',
        related_name='user_set',
        related_query_name='user',
        verbose_name='Группы',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text='Индивидуальные права пользователя.',
        related_name='user_set',
        related_query_name='user',
        verbose_name='Права пользователя',
    )
    role = models.ForeignKey(
        'core.Role',
        on_delete=models.SET_NULL,
        related_name='users',
        null=True,
        blank=True,
        verbose_name='Роль',
    )
    primary_team = models.ForeignKey(
        'core.Team',
        on_delete=models.SET_NULL,
        related_name='primary_users',
        null=True,
        blank=True,
        verbose_name='Основная команда',
    )
    teams = models.ManyToManyField(
        'core.Team',
        related_name='members',
        blank=True,
        verbose_name='Команды',
    )
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        """
        Возвращает идентификатор пользователя для admin и логов.

        :return: Email пользователя.
        """
        return self.email
