#!/bin/sh
set -e
echo "▶ Starting Celery worker..."
exec celery -A LigaPay worker -l info
