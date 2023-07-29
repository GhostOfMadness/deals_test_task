from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


User = get_user_model()

# class DealManager(models.Manager):
#     """Менеджер для работы с объектами модели Deal."""

#     def top_five_customers(self):
#         """Топ 5 покупателей по общей сумме покупок."""
#         return self.values(
#             'customer',
#         ).annotate(
#             spent_money=models.Sum('total'),
#         ).order_by(
#             '-spent_money',
#         ).values_list(
#             'customer', flat=True,
#         )[:5]

#     def items_purchased_by_top_five_customers(self):
#         """Товары, которые купили минимум 2 из топ-5 покупателей."""
#         return self.filter(
#             customer__in=self.top_five_customers(),
#         ).values(
#             'item',
#         ).annotate(
#             customer_count=models.Count('customer', distinct=True),
#         ).filter(
#             customer_count__gte=2,
#         ).values_list(
#             'item', flat=True,
#         )

#     def top_five_customers_with_items(self):
#         items_list = self.items_purchased_by_top_five_customers()
#         top_customers_with_items = self.filter(
#             customer__in=models.Subquery(self.top_five_customers()),
#         ).annotate(
#             spent_money=models.Window(
#                 expression=models.Sum('total'),
#                 partition_by=models.F('customer'),
#             ),
#         ).values(
#             'customer', 'spent_money', 'item',
#         ).distinct().order_by(
#             '-spent_money',
#         )
#         result = {}
#         for customer in top_customers_with_items:
#             if not customer['customer'] in result.keys():
#                 result[customer['customer']] = {
#                     'spent_money': customer['spent_money'],
#                     'gems': [],
#                 }
#             if customer['item'] in items_list:
#                 result[customer['customer']]['gems'].append(customer['item'])
#         return result


class GemstoneManager(models.Manager):
    """Менеджер для работы с объектами модели Gemstone."""

    def items_purchased_by_top_customers(self):
        """Камни, которые купили минимум 2 из топ-5 покупателей."""
        return self.filter(
            users__in=User.objects.top_five_customers(),
        ).annotate(
            count=models.Count('name'),
        ).filter(
            count__gte=2,
        )


class Gemstone(models.Model):
    """Модель описания драгоценного камня."""

    name = models.CharField(_('Название'), max_length=255, unique=True)
    users = models.ManyToManyField(User, related_name='gemstones')

    objects = GemstoneManager()

    class Meta:
        ordering = ['name']
        verbose_name = _('Драгоценный камень')
        verbose_name_plural = _('Драгоценные камни')

    def __str__(self) -> str:
        return self.name


class Deal(models.Model):
    """Модель описания сделки."""

    number_validator = MinValueValidator(
        limit_value=1,
        message=_('Значение не может быть меньше 1'),
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Логин покупателя'),
        related_name='deals',
    )
    item = models.ForeignKey(
        Gemstone,
        on_delete=models.CASCADE,
        verbose_name=_('Наименование товара'),
        related_name='deals',
    )
    total = models.PositiveIntegerField(
        _('Сумма сделки'),
        validators=[number_validator],
    )
    quantity = models.PositiveSmallIntegerField(
        _('Количество товара'),
        validators=[number_validator],
    )
    date = models.DateTimeField()

    class Meta:
        ordering = ['-date']
        verbose_name = _('Сделка')
        verbose_name_plural = _('Сделки')

    def __str__(self) -> str:
        return (
            f'Покупатель - {self.customer}, '
            f'сумма - {self.total}, '
            f'дата - {self.date.strftime("%Y-%m-%d %H-%M-%S")}'
        )
