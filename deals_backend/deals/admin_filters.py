from admin_auto_filters.filters import AutocompleteFilter

from django.utils.translation import gettext_lazy as _


class DealCustomerFilter(AutocompleteFilter):
    """Фильтр сделки по покупателю."""

    title = _('Покупатель')
    field_name = 'customer'


class DealItemFilter(AutocompleteFilter):
    """Фильтр сделки по наименованию товара."""

    title = _('Товар')
    field_name = 'item'
