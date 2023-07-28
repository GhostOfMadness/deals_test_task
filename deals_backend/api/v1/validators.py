import csv
import os
import re
from typing import Any, ClassVar, Optional

import pandas as pd
from rest_framework import serializers

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import gettext_lazy as _


class CSVFileValidator:
    """Валидатор поступающего csv-файла."""

    FILE_EXTENSIONS: ClassVar[tuple[str]] = ('.csv', '.CSV')
    FILE_COLUMN_NAME_DTYPE_MAP: ClassVar[dict[str, Any]] = {
        'customer': re.compile(r'^object$'),
        'item': re.compile(r'^object$'),
        'total': re.compile(r'^int\d+$'),
        'quantity': re.compile(r'^int\d+$'),
        'date': re.compile(r'^datetime\S+$'),
    }

    ERROR_MESSAGES: ClassVar[dict[str, str]] = {
        'extension': _(
            'Файлы с расширением <%(extension)s> не поддерживаются. '
            'Файл должен иметь одно из этих расширений: %(exp_values)s.',
        ),
        'csv_format': _(
            'Невозможно определить параметры данного CSV-файла. '
            'Пожалуйста, проверьте формат данных.',
        ),
        'column_names': _(
            'Имеющиеся поля файла <%(column_names)s> не совпадают с '
            'ожидаемыми. Ожидаются <%(exp_values)s> в указанном порядке.',
        ),
        'date_format': _(
            'Дата в столбце <date> представлена в неверном формате. '
            'Ожидается <YYYY-MM-DD hh:mm:ss.ms>',
        ),
        'column_dtype': _(
            'Столбец <%(column_name)s> имеет неверный тип '
            '<%(column_dtype)s>. Ожидается тип, соответствующий '
            'регулярному выражению <%(exp_value)s>.',
        ),
    }

    def __call__(self, file_obj: InMemoryUploadedFile) -> None:
        self._validate_extension(file_obj)
        csv_dialect = self._validate_file_params(file_obj)
        self._validate_file_content(file_obj, csv_dialect)
        file_obj.seek(0)

    def _validate_extension(self, file_obj: InMemoryUploadedFile) -> None:
        """Проверка расширения файла."""
        name_, extension = os.path.splitext(file_obj.name)
        if extension not in self.FILE_EXTENSIONS:
            params = {
                'extension': extension,
                'exp_values': ', '.join(self.FILE_EXTENSIONS),
            }
            raise serializers.ValidationError(
                self.ERROR_MESSAGES['extension'] % params,
                code='invalid_extension',
            )

    def _validate_file_params(
        self,
        file_obj: InMemoryUploadedFile,
    ) -> Optional[csv.Dialect]:
        """Определение параметров CSV-файла."""
        try:
            dialect = csv.Sniffer().sniff(file_obj.read(2048).decode('utf-8'))
            file_obj.seek(0)
            return dialect
        except csv.Error:
            raise serializers.ValidationError(
                self.ERROR_MESSAGES['csv_format'],
                code='invalid_csv_format',
            )

    def _validate_file_content(
        self,
        file_obj: InMemoryUploadedFile,
        dialect: csv.Dialect,
    ) -> None:
        """Проверка содержимого файла."""
        data = pd.read_csv(file_obj, dialect=dialect)
        column_names = data.columns.values.tolist()
        self._validate_file_headers(column_names)
        try:
            data['date'] = pd.to_datetime(data['date'], format='ISO8601')
        except Exception:
            raise serializers.ValidationError(
                self.ERROR_MESSAGES['date_format'],
                code='invalid_date_format',
            )
        self._validate_file_column_dtypes(data.dtypes.to_dict())

    def _validate_file_headers(self, column_names: list[str]) -> None:
        """Проверка заголовков файла."""
        exp_column_names = list(self.FILE_COLUMN_NAME_DTYPE_MAP.keys())
        if not column_names == exp_column_names:
            params = {
                'column_names': ', '.join(column_names),
                'exp_values': ', '.join(exp_column_names),
            }
            raise serializers.ValidationError(
                self.ERROR_MESSAGES['column_names'] % params,
                code='invalid_column_names',
            )

    def _validate_file_column_dtypes(
        self,
        column_dtype_map: dict[str, Any],
    ) -> None:
        """Проверка типов столбцов файла."""
        for column_name, column_dtype in column_dtype_map.items():
            exp_column_dtype = self.FILE_COLUMN_NAME_DTYPE_MAP[column_name]
            if not exp_column_dtype.match(str(column_dtype)):
                params = {
                    'column_name': column_name,
                    'column_dtype': column_dtype,
                    'exp_value': exp_column_dtype.pattern,
                }
                raise serializers.ValidationError(
                    self.ERROR_MESSAGES['column_dtype'] % params,
                    code='invalid_column_dtype',
                )
