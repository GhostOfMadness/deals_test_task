from typing import Sequence

import pandas as pd
from query_counter.decorators import queries_counter
from rest_framework import generics, parsers, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.db.models import Model, Prefetch, Sum
from django.utils.decorators import method_decorator

from deals.models import Deal, Gemstone

from .serializers import FileUploadSerializer, TopCustomersSerializer


User = get_user_model()


@method_decorator(queries_counter, name='dispatch')
class TopCustomersView(generics.ListAPIView):
    """Возвращает список топ-5 покупателей по обшей сумме покупок."""

    queryset = User.objects.annotate(
        spent_money=Sum('deals__total', default=0),
    ).prefetch_related(
        Prefetch(
            'gemstones',
            queryset=Gemstone.objects.items_purchased_by_top_customers(),
        ),
    ).order_by(
        '-spent_money',
    )[:5]
    serializer_class = TopCustomersSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(
            {'response': response.data},
            status=response.status_code,
        )


@method_decorator(queries_counter, name='dispatch')
class FileUploadView(generics.CreateAPIView):
    """Загрузка и обработка файлов."""

    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = FileUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            file_obj = serializer.validated_data['deals']
            reader = pd.read_csv(file_obj, parse_dates=['date'])

            unique_customers = reader['customer'].unique().tolist()
            current_customers = self._bulk_create_objects_by_lookup(
                unique_file_values=unique_customers,
                model=User,
                lookup_field='username',
            )

            unique_items = reader['item'].unique().tolist()
            current_items = self._bulk_create_objects_by_lookup(
                unique_file_values=unique_items,
                model=Gemstone,
                lookup_field='name',
            )

            self._bulk_create_user_item_objects(
                reader=reader,
                current_customers=current_customers,
                current_items=current_items,
            )

            Deal.objects.bulk_create(
                [
                    Deal(
                        customer=current_customers[row['customer']],
                        item=current_items[row['item']],
                        quantity=row['quantity'],
                        total=row['total'],
                        date=row['date'],
                    )
                    for _, row in reader.iterrows()
                ],
            )
            return Response({'Status': 'OK'}, status=status.HTTP_201_CREATED)
        return Response(
            {
                'Status': 'Error',
                'Desc': serializer.errors['deals'],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _bulk_create_objects_by_lookup(
        self,
        unique_file_values: Sequence[str],
        model: Model,
        lookup_field: str,
    ) -> dict[str, Model]:
        """
        Создание объектов из файла, которых нет в базе.

        Метод возвращает словарь используемых в файле объектов, ключ -
        значение lookup_field (например, имя пользователя), значение -
        объект соответствующей модели.
        """
        db_values = model.objects.all().values_list(lookup_field, flat=True)
        objs_not_in_db = set(unique_file_values).difference(set(db_values))
        model.objects.bulk_create(
            [
                model(**{lookup_field: lookup_value})
                for lookup_value in objs_not_in_db
            ],
        )
        qs = model.objects.filter(
            **{f'{lookup_field}__in': unique_file_values},
        )
        return {
            getattr(model_obj, lookup_field): model_obj for model_obj in qs
        }

    def _bulk_create_user_item_objects(
        self,
        reader: pd.DataFrame,
        current_customers: dict[str, User],
        current_items: dict[str, Gemstone],
    ) -> None:
        """Создание объектов покуптель-товар в промежуточной таблице."""
        unique_customer_item = reader[
            ['customer', 'item']
        ].value_counts().index
        db_values = Gemstone.users.through.objects.all().values_list(
            'customuser__username', 'gemstone__name',
        )
        objs_not_in_db = [
            obj for obj in unique_customer_item if obj not in db_values
        ]
        Gemstone.users.through.objects.bulk_create(
            [
                Gemstone.users.through(
                    customuser=current_customers[obj[0]],
                    gemstone=current_items[obj[1]],
                )
                for obj in objs_not_in_db
            ],
        )
