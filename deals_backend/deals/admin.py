from rangefilter.filters import DateTimeRangeFilterBuilder

from django.contrib import admin

from .models import Deal


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    """Конфиг админ-зоны для модели Deal."""

    list_display = ('pk', 'customer', 'item', 'total', 'quantity', 'date')
    search_fields = ('customer', 'item')
    list_filter = (
        ('date', DateTimeRangeFilterBuilder(title='Дата')),
    )
