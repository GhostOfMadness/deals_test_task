from rest_framework import serializers

from django.contrib.auth import get_user_model

from .validators import CSVFileValidator


User = get_user_model()


class FileUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки файлов."""

    deals = serializers.FileField(
        allow_empty_file=False,
        validators=[CSVFileValidator()],
    )


class TopCustomersSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения пользователей."""

    spent_money = serializers.IntegerField(read_only=True)
    gems = serializers.SlugRelatedField(
        slug_field='name',
        source='gemstones',
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'spent_money',
            'gems',
        )
