from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


User = get_user_model()


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
