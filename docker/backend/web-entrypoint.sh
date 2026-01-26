#!/bin/sh
set -e

echo "▶ Waiting for Postgres..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  sleep 1
done
echo "✔ Postgres is ready"

echo "▶ Applying migrations..."
python manage.py migrate --noinput

echo "▶ Collect static..."
python manage.py collectstatic --noinput

if [ ! -f /tmp/fixtures_loaded ] && [ -d fixtures ] && [ "$(ls -A fixtures)" ]; then
  echo "📦 Loading fixtures..."
  python manage.py loaddata fixtures/*
  touch /tmp/fixtures_loaded
fi

echo "▶ Initial news parsing..."
python manage.py shell <<EOF
from news.tasks import scrape_news_task
print("▶ Parsing news on startup...")
scrape_news_task.delay()
print("✔ News parsed")
EOF

echo "▶ Ensure periodic news parsing task..."
python manage.py shell <<EOF
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import json

schedule, _ = CrontabSchedule.objects.get_or_create(
    minute="0",
    hour="3",
    day_of_week="*",
    day_of_month="*",
    month_of_year="*",
)

PeriodicTask.objects.get_or_create(
    name="Parse news daily",
    defaults={
        "crontab": schedule,
        "task": "news.tasks.scrape_news_task",
        "enabled": True,
        "args": json.dumps([]),
    },
)

print("✔ Periodic task ensured")
EOF


echo "▶ Create superuser (if not exists)..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin"
    )
    print("✔ Superuser created")
else:
    print("✔ Superuser already exists")
EOF

echo "▶ Create system user LigaPay..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model

User = get_user_model()

User.objects.get_or_create(
    username="LigaPay",
    defaults={
        "email": "system@ligapay.local",
        "is_active": True,
    }
)
print("✔ System user ensured")
EOF

echo "▶ Starting Daphne..."
exec daphne -b 0.0.0.0 -p 8000 LigaPay.asgi:application
