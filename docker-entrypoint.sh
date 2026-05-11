#!/bin/sh
set -e

if [ -f /app/.env ]; then
    set -o allexport
    # shellcheck disable=SC1091
    . /app/.env
    set +o allexport
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
if username and password:
        if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email, password=password)
                print(f"Superuser '{username}' created.")
        else:
                print(f"Superuser '{username}' already exists.")
PY
fi

exec "$@"
