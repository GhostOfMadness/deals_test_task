import pandas as pd
from rest_framework import generics, parsers, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.db.models import Sum, Prefetch

from deals.models import Deal, Gemstone

from .serializers import FileUploadSerializer, TopCustomersSerializer


User = get_user_model()


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


class FileUploadView(generics.CreateAPIView):
    """Загрузка файлов."""

    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = FileUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            file_obj = serializer.validated_data['deals']
            reader = pd.read_csv(file_obj, parse_dates=['date'])
            model_objs = []
            for _, row in reader.iterrows():
                customer, _ = User.objects.get_or_create(
                    username=row['customer'],
                )
                item, _ = Gemstone.objects.get_or_create(
                    name=row['item'],
                )
                Gemstone.users.through.objects.get_or_create(
                    gemstone=item,
                    customuser=customer,
                )
                row['customer'] = customer
                row['item'] = item
                model_objs.append(Deal(**row))
            Deal.objects.bulk_create(model_objs)
            return Response({'Status': 'OK'}, status=status.HTTP_201_CREATED)
        return Response(
            {
                'Status': 'Error',
                'Desc': serializer.errors['deals'],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
