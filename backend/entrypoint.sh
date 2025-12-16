#!/usr/bin/env sh
set -e

python backend/manage.py migrate --noinput

exec "$@"
