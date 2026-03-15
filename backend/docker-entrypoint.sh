#!/bin/sh
set -eu

uv sync --frozen
uv run python manage.py migrate

if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  if ! uv run python manage.py shell -c "from core.models import User; import os; raise SystemExit(0 if User.objects.filter(email=os.environ['DJANGO_SUPERUSER_EMAIL']).exists() else 1)"; then
    uv run python manage.py createsuperuser --no-input
  fi
fi

exec "$@"
