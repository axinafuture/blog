web: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py createsuperuser --noinput 2>/dev/null; gunicorn config.wsgi
