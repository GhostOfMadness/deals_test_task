from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    """Менеджер для работы с пользователями."""

    def top_five_customers(self):
        """Топ 5 покупателей по общей сумме покупок."""
        return self.annotate(
            spent_money=Sum('deals__total', default=0),
        ).order_by(
            '-spent_money',
        )[:5]


class CustomUser(AbstractUser):
    """Модель описания пользователя."""

    objects = CustomUserManager()

    class Meta:
        ordering = ['username']
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
