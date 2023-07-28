from rest_framework import serializers

from .validators import CSVFileValidator


class FileUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки файлов."""

    deals = serializers.FileField(
        allow_empty_file=False,
        validators=[CSVFileValidator()],
    )
