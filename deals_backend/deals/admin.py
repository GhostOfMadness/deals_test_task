from rangefilter.filters import DateTimeRangeFilterBuilder

from django.contrib import admin

from .admin_filters import DealCustomerFilter, DealItemFilter
from .models import Deal, Gemstone


class GemstoneUserInline(admin.TabularInline):
    """Конфиг для отображения пользователей на странице товара."""

    model = Gemstone.users.through
    extra = 1


@admin.register(Gemstone)
class GemstoneAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели Gemstone."""

    list_display = ('name',)
    search_fields = ('name',)
    fieldsets = [
        (
            None,
            {'fields': ['name']},
        ),
    ]
    inlines = [GemstoneUserInline]


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели Deal."""

    list_display = ('pk', 'customer', 'item', 'total', 'quantity', 'date')
    search_fields = ('customer', 'item')
    list_filter = (
        ('date', DateTimeRangeFilterBuilder(title='Дата')),
        DealItemFilter,
        DealCustomerFilter,
    )
