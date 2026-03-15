from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group as DjangoGroup

from core.models import Group, Role, Team, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'updated_at')
    search_fields = ('name', 'code')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'updated_at')
    search_fields = ('name', 'code')


@admin.register(User)
class CoreUserAdmin(UserAdmin):
    list_display = ('email', 'role', 'primary_team', 'is_staff', 'is_superuser')
    list_select_related = ('role', 'primary_team')
    fieldsets = (
        (
            'Учётные данные',
            {
                'fields': ('email', 'password'),
            },
        ),
        (
            'Личные данные',
            {
                'fields': ('first_name', 'last_name'),
            },
        ),
        (
            'Права доступа',
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            },
        ),
        (
            'Важные даты',
            {
                'fields': ('last_login', 'created_at', 'updated_at'),
            },
        ),
        (
            'Структура команды',
            {
                'fields': ('role', 'primary_team', 'teams'),
            },
        ),
    )
    add_fieldsets = (
        (
            'Новый пользователь',
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser'),
            },
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('email',)


admin.site.unregister(DjangoGroup)
admin.site.register(Group, GroupAdmin)
