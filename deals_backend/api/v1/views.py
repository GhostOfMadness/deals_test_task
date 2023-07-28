import pandas as pd
from rest_framework import generics, parsers, status
from rest_framework.response import Response

from deals.models import Deal

from .serializers import FileUploadSerializer


class FileUploadView(generics.CreateAPIView):
    """Загрузка файлов."""

    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            file_obj = serializer.validated_data['deals']
            reader = pd.read_csv(file_obj, parse_dates=['date'])
            model_objs = []
            for _, row in reader.iterrows():
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
