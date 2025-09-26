#!/bin/bash

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start Gunicorn
gunicorn danovmusic_studio.wsgi:application --bind 0.0.0.0:$PORT 