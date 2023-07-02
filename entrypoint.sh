#!/bin/sh
service redis-server start
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn wsgi:application --workers 1 --timeout 600 --bind 0.0.0.0:80

