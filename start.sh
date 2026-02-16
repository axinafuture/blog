#!/bin/bash
set -e

echo "=== Running migrations ==="
python manage.py migrate

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Creating/updating superuser ==="
python manage.py ensure_superuser

echo "=== Starting gunicorn ==="
exec gunicorn config.wsgi --timeout 120
