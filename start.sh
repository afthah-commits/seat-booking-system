#!/bin/bash
set -e

echo "🚀 Starting Deployment Script..."

echo "📦 Running Migrations..."
python manage.py migrate

echo "🌱 Seeding Data..."
python manage.py seed_data

echo "🔥 Starting Server on port $PORT..."
gunicorn seat_booking.wsgi:application --bind 0.0.0.0:$PORT
