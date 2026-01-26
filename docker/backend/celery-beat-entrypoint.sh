#!/bin/sh
set -e
echo "▶ Starting Celery beat..."
exec celery -A LigaPay beat -l info
