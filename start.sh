#!/bin/bash
set -e

echo "🚀 Starting Deployment Script..."

echo "🎨 Collecting Static Files..."
python manage.py collectstatic --noinput

echo "📦 Running Migrations..."
python manage.py migrate

echo "🌱 Seeding Data..."
python manage.py seed_data

echo "🔥 Starting Server on port $PORT..."
gunicorn seat_booking.wsgi:application --bind 0.0.0.0:$PORT
