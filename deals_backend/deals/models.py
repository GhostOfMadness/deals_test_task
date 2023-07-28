from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Deal(models.Model):
    """Модель описания сделки."""

    number_validator = MinValueValidator(
        limit_value=1,
        message=_('Значение не может быть меньше 1'),
    )

    customer = models.CharField(_('Логин покупателя'), max_length=128)
    item = models.CharField(_('Наименование товара'), max_length=128)
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
