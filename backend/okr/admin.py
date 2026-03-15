import json

from django.contrib import admin
from django.db.models import Count, Max
from django.utils.html import format_html

from okr.models import ChangeLog, CheckIn, Comment, KeyResult, Okr, Quarter


@admin.register(Quarter)
class QuarterAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'quarter', 'start_date', 'end_date', 'is_active')
    list_filter = ('year', 'quarter', 'is_active')
    search_fields = ('name',)
    ordering = ('-year', '-quarter')
    readonly_fields = ('name',)
    save_on_top = True
    fieldsets = (
        (
            'Период',
            {
                'fields': ('name', 'year', 'quarter'),
            },
        ),
        (
            'Даты',
            {
                'fields': ('start_date', 'end_date', 'is_active'),
            },
        ),
    )


class KeyResultInline(admin.TabularInline):
    model = KeyResult
    extra = 0
    autocomplete_fields = ('okr',)
    fields = (
        'title',
        'metric_type',
        'value',
        'status',
        'start_value',
        'current_value',
        'target_value',
        'updated_at',
    )
    readonly_fields = ('updated_at',)
    show_change_link = True

    def get_queryset(self, request):
        """
        Оптимизирует выборку ключевых результатов для inline-блока.

        :param request: HTTP-запрос администратора.
        :return: Оптимизированный queryset ключевых результатов.
        """
        return super().get_queryset(request).select_related('okr')


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    autocomplete_fields = ('author',)
    fields = ('author', 'text', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True

    def get_queryset(self, request):
        """
        Оптимизирует выборку комментариев для inline-блока.

        :param request: HTTP-запрос администратора.
        :return: Оптимизированный queryset комментариев.
        """
        return super().get_queryset(request).select_related('author')


class CheckInInline(admin.TabularInline):
    model = CheckIn
    extra = 0
    autocomplete_fields = ('author',)
    fields = ('author', 'previous_value', 'new_value', 'comment', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True

    def get_queryset(self, request):
        """
        Оптимизирует выборку check-in для inline-блока.

        :param request: HTTP-запрос администратора.
        :return: Оптимизированный queryset check-in.
        """
        return super().get_queryset(request).select_related('author')


@admin.register(Okr)
class OkrAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'team',
        'owner',
        'period',
        'status',
        'progress_badge',
        'key_results_count',
        'comments_count',
        'updated_at',
    )
    list_filter = ('status', 'period', 'team', 'created_by')
    search_fields = (
        'title',
        'description',
        'team__name',
        'owner__email',
        'owner__first_name',
        'owner__last_name',
    )
    list_select_related = ('team', 'owner', 'period', 'created_by')
    autocomplete_fields = ('owner', 'team', 'period', 'created_by')
    readonly_fields = ('progress', 'archived_at', 'created_at', 'updated_at')
    ordering = ('-updated_at', '-id')
    save_on_top = True
    list_per_page = 25
    inlines = [KeyResultInline, CommentInline]
    fieldsets = (
        (
            'Objective',
            {
                'fields': ('title', 'description'),
            },
        ),
        (
            'Ответственные',
            {
                'fields': ('owner', 'team', 'period', 'created_by'),
            },
        ),
        (
            'Состояние',
            {
                'fields': ('status', 'progress', 'archived_at'),
            },
        ),
        (
            'Системные поля',
            {
                'classes': ('collapse',),
                'fields': ('created_at', 'updated_at'),
            },
        ),
    )

    def get_queryset(self, request):
        """
        Возвращает queryset OKR с аннотациями для списка админки.

        :param request: HTTP-запрос администратора.
        :return: Оптимизированный queryset целей.
        """
        return (
            super()
            .get_queryset(request)
            .select_related('team', 'owner', 'period', 'created_by')
            .annotate(
                key_results_total=Count('key_results', distinct=True),
                comments_total=Count('comments', distinct=True),
            )
        )

    @admin.display(description='Прогресс')
    def progress_badge(self, obj: Okr) -> str:
        """
        Рендерит компактный индикатор прогресса цели.

        :param obj: Экземпляр цели OKR.
        :return: HTML-представление прогресса.
        """
        tone = '#0f766e' if obj.progress >= 1 else '#d97706' if obj.progress >= 0.7 else '#0284c7'
        return format_html(
            '<strong style="color: {};">{}</strong>',
            tone,
            obj.progress,
        )

    @admin.display(ordering='key_results_total', description='KR')
    def key_results_count(self, obj: Okr) -> int:
        """
        Возвращает число ключевых результатов цели.

        :param obj: Экземпляр цели OKR.
        :return: Число ключевых результатов.
        """
        return obj.key_results_total

    @admin.display(ordering='comments_total', description='Комментарии')
    def comments_count(self, obj: Okr) -> int:
        """
        Возвращает число комментариев цели.

        :param obj: Экземпляр цели OKR.
        :return: Число комментариев.
        """
        return obj.comments_total


@admin.register(KeyResult)
class KeyResultAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'okr',
        'value',
        'metric_type',
        'status',
        'current_value',
        'target_value',
        'check_ins_count',
        'last_check_in',
        'updated_at',
    )
    list_filter = ('metric_type', 'status', 'okr__period', 'okr__team')
    search_fields = ('title', 'description', 'okr__title', 'okr__team__name')
    list_select_related = ('okr', 'okr__team', 'okr__owner', 'okr__period')
    autocomplete_fields = ('okr',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('okr', 'value', 'id')
    save_on_top = True
    list_per_page = 25
    inlines = [CheckInInline]
    fieldsets = (
        (
            'Key Result',
            {
                'fields': ('okr', 'title', 'description', 'metric_type', 'status', 'value'),
            },
        ),
        (
            'Метрика',
            {
                'fields': ('start_value', 'current_value', 'target_value'),
            },
        ),
        (
            'Системные поля',
            {
                'classes': ('collapse',),
                'fields': ('created_at', 'updated_at'),
            },
        ),
    )

    def get_queryset(self, request):
        """
        Возвращает queryset ключевых результатов с агрегатами для списка.

        :param request: HTTP-запрос администратора.
        :return: Оптимизированный queryset ключевых результатов.
        """
        return (
            super()
            .get_queryset(request)
            .select_related('okr', 'okr__team', 'okr__owner', 'okr__period')
            .annotate(
                check_ins_total=Count('check_ins', distinct=True),
                last_check_in_at=Max('check_ins__created_at'),
            )
        )

    @admin.display(ordering='check_ins_total', description='Check-in')
    def check_ins_count(self, obj: KeyResult) -> int:
        """
        Возвращает число check-in по ключевому результату.

        :param obj: Экземпляр ключевого результата.
        :return: Число check-in.
        """
        return obj.check_ins_total

    @admin.display(ordering='last_check_in_at', description='Последний check-in')
    def last_check_in(self, obj: KeyResult):
        """
        Возвращает дату последнего check-in по ключевому результату.

        :param obj: Экземпляр ключевого результата.
        :return: Дата последнего check-in или прочерк.
        """
        return obj.last_check_in_at or '—'


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = (
        'key_result',
        'okr',
        'author',
        'previous_value',
        'new_value',
        'delta',
        'created_at',
    )
    list_filter = ('author', 'key_result__metric_type', 'key_result__status', 'key_result__okr__period')
    search_fields = ('comment', 'key_result__title', 'key_result__okr__title', 'author__email')
    list_select_related = ('key_result', 'key_result__okr', 'author')
    autocomplete_fields = ('key_result', 'author')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at', '-id')
    save_on_top = True
    date_hierarchy = 'created_at'
    fieldsets = (
        (
            'Check-in',
            {
                'fields': ('key_result', 'author', 'previous_value', 'new_value', 'comment'),
            },
        ),
        (
            'Системные поля',
            {
                'classes': ('collapse',),
                'fields': ('created_at', 'updated_at'),
            },
        ),
    )

    @admin.display(ordering='key_result__okr', description='OKR')
    def okr(self, obj: CheckIn) -> Okr:
        """
        Возвращает цель, к которой относится check-in.

        :param obj: Экземпляр check-in.
        :return: Цель OKR.
        """
        return obj.key_result.okr

    @admin.display(description='Δ')
    def delta(self, obj: CheckIn):
        """
        Возвращает изменение значения в рамках check-in.

        :param obj: Экземпляр check-in.
        :return: Дельта между новым и предыдущим значением.
        """
        return obj.new_value - obj.previous_value


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'okr', 'author', 'created_at', 'updated_at')
    list_filter = ('okr__period', 'okr__team', 'author')
    search_fields = ('text', 'okr__title', 'author__email')
    list_select_related = ('okr', 'okr__team', 'author')
    autocomplete_fields = ('okr', 'author')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at', '-id')
    save_on_top = True
    date_hierarchy = 'created_at'
    fieldsets = (
        (
            'Комментарий',
            {
                'fields': ('okr', 'author', 'text'),
            },
        ),
        (
            'Системные поля',
            {
                'classes': ('collapse',),
                'fields': ('created_at', 'updated_at'),
            },
        ),
    )

    @admin.display(description='Текст')
    def short_text(self, obj: Comment) -> str:
        """
        Возвращает сокращённый текст комментария для списка.

        :param obj: Экземпляр комментария.
        :return: Сокращённый текст комментария.
        """
        return obj.text[:80]


@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'entity_id', 'action', 'author', 'created_at')
    list_filter = ('entity_type', 'action', 'author')
    search_fields = ('entity_id', 'payload')
    list_select_related = ('author',)
    readonly_fields = ('entity_type', 'entity_id', 'action', 'author', 'payload_pretty', 'created_at', 'updated_at')
    ordering = ('-created_at', '-id')
    date_hierarchy = 'created_at'
    fieldsets = (
        (
            'Событие',
            {
                'fields': ('entity_type', 'entity_id', 'action', 'author'),
            },
        ),
        (
            'Данные',
            {
                'fields': ('payload_pretty',),
            },
        ),
        (
            'Системные поля',
            {
                'classes': ('collapse',),
                'fields': ('created_at', 'updated_at'),
            },
        ),
    )

    def get_queryset(self, request):
        """
        Оптимизирует queryset истории изменений для списка админки.

        :param request: HTTP-запрос администратора.
        :return: Оптимизированный queryset журнала изменений.
        """
        return super().get_queryset(request).select_related('author')

    @admin.display(description='Payload')
    def payload_pretty(self, obj: ChangeLog) -> str:
        """
        Отображает JSON payload в удобочитаемом виде.

        :param obj: Экземпляр записи журнала изменений.
        :return: HTML-представление JSON payload.
        """
        return format_html(
            '<pre style="white-space: pre-wrap; margin: 0;">{}</pre>',
            json.dumps(obj.payload, ensure_ascii=False, indent=2),
        )

    def has_add_permission(self, request) -> bool:
        """
        Запрещает ручное создание записей аудита в админке.

        :param request: HTTP-запрос администратора.
        :return: Флаг доступности создания.
        """
        return False
