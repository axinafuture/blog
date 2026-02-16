"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Ensure superuser exists on app startup
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

    print(f'[WSGI] ensure_superuser: username={username}, pw_len={len(password) if password else 0}', flush=True)

    if username and password:
        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f'[WSGI] User "{username}" password updated.', flush=True)
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f'[WSGI] Superuser "{username}" created.', flush=True)
except Exception as e:
    print(f'[WSGI] ensure_superuser error: {e}', flush=True)
