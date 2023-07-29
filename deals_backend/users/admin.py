from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    """Конфиг админ-зоны для модели пользователя."""

    list_display = (
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
    )
    search_fields = ('username',)
    fieldsets = [
        (
            None,
            {'fields': ('username', 'password')},
        ),
        (
            'Personal info',
            {'fields': ('first_name', 'last_name', 'email')},
        ),
        (
            'Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser')},
        ),
    ]
    add_fieldsets = [
        (
            None,
            {
                'fields': (
                    'username',
                    'password1',
                    'password2',
                ),
            },
        ),
    ]
