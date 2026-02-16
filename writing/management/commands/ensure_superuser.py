import os
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class Command(BaseCommand):
    help = 'Create superuser from environment variables (skip if exists)'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

        print(f'[ensure_superuser] username={username}, password length={len(password) if password else 0}', flush=True)

        if not username or not password:
            print('[ensure_superuser] ENV not set, skipping.', flush=True)
            return

        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f'[ensure_superuser] User "{username}" exists, password updated.', flush=True)
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f'[ensure_superuser] Superuser "{username}" created.', flush=True)

        # 검증: 로그인 테스트
        test_user = authenticate(username=username, password=password)
        if test_user:
            print(f'[ensure_superuser] Auth test PASSED for "{username}"', flush=True)
        else:
            print(f'[ensure_superuser] Auth test FAILED for "{username}"', flush=True)
