#!/bin/bash

set -euo pipefail

APP_DIR="/app"
cd "$APP_DIR"

set -a
source "$APP_DIR/.env"
set +a


# wating for db
# echo "Waiting for DB ..."
# until pg_isready -h db -p ${DB_PORT} -U ${DB_USER}; do
#     echo "Waiting for DB..."
#     sleep 3
# done
# echo "Database is UP"


# migrations ...
echo "Running migrations ..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
    




sleep 1

# django setup...
echo "Starting Django server ..."
gunicorn excel.wsgi:application \
  --workers 4 \
  --bind 0.0.0.0:8001 \
  --timeout 60 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile -

