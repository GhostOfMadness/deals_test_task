#!/bin/sh

# if [ "$DATABASE" = "postgres" ]
# then
#     echo "Waiting for postgres..."

#     while ! nc -z $SQL_HOST $SQL_PORT; do
#       sleep 0.1
#     done

#     echo "PostgreSQL started"
# fi

echo "Apply migrations"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --no-input --clear

echo "Copy static files"
cp -r /app/$DJANGO_STATIC_ROOT/. /backend_static/static/

echo "Start server"
gunicorn --bind 0.0.0.0:8000 deals_backend.wsgi

exec "$@"