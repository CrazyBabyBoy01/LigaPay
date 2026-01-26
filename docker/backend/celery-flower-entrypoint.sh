#!/bin/sh
set -e
echo "▶ Starting Flower..."
exec celery -A LigaPay flower --port=5555
