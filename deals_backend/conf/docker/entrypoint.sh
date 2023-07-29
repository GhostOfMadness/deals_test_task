#!/bin/sh

echo "Apply migrations"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --no-input --clear

echo "Copy static files"
cp -r /app/$DJANGO_STATIC_ROOT/. /backend_static/static/

echo "Start server"
gunicorn --bind 0.0.0.0:8000 deals_backend.wsgi

exec "$@"