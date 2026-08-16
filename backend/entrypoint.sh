#!/bin/sh
set -e

python manage.py migrate --noinput

if [ "${DJANGO_DEBUG:-0}" != "1" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"
