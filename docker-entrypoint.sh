#!/bin/bash
set -e

if [ "$1" = 'back' ]; then
	# Apply database migrations
	echo "Apply database migrations"
	python manage.py migrate

	# Start server
	echo "Starting server"
	gunicorn project.wsgi:application --bind 0.0.0.0:8000 --timeout 300
fi

exec "$@"


