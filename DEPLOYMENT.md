# 🚀 Deployment Guide - Seat Booking System

## Overview
This guide covers deploying your Django seat booking system to production.

---

## 📋 Pre-Deployment Checklist

### 1. **Environment Configuration**

Create a production `.env` file:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recommended for production)
USE_MYSQL=False
DB_NAME=seat_booking_prod
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Security
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

### 2. **Update settings.py for Production**

Add to `seat_booking/settings.py`:

```python
import os
from pathlib import Path

# Security Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-test-key-for-interview')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# HTTPS Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Static Files (for production)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Database - PostgreSQL for production
if os.getenv('DATABASE_URL'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600
        )
    }
```

---

## 🐳 Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate

EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "seat_booking.wsgi:application"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=seat_booking
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5432:5432"

  web:
    build: .
    command: gunicorn seat_booking.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Build and Run

```bash
# Build the containers
docker-compose build

# Run migrations
docker-compose run web python manage.py migrate

# Create superuser
docker-compose run web python manage.py createsuperuser

# Seed data
docker-compose run web python manage.py seed_data

# Start services
docker-compose up -d
```

---

## 🌐 Platform-Specific Deployments

### **Heroku**

1. **Install Heroku CLI**
```bash
# Windows
choco install heroku-cli
```

2. **Create Heroku App**
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
```

3. **Update requirements.txt**
```txt
django>=5.1
requests
django-cors-headers
python-dotenv
pillow
gunicorn
dj-database-url
psycopg2-binary
whitenoise
```

4. **Create Procfile**
```
web: gunicorn seat_booking.wsgi --log-file -
release: python manage.py migrate
```

5. **Deploy**
```bash
git add .
git commit -m "Ready for deployment"
git push heroku main

# Seed data
heroku run python manage.py seed_data
```

---

### **Railway**

1. **Create `railway.json`**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn seat_booking.wsgi",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. **Deploy**
- Connect GitHub repo to Railway
- Add PostgreSQL plugin
- Set environment variables
- Deploy automatically

---

### **DigitalOcean App Platform**

1. **Create `.do/app.yaml`**
```yaml
name: seat-booking-system
services:
- name: web
  github:
    repo: your-username/seat-booking-system
    branch: main
  build_command: pip install -r requirements.txt
  run_command: gunicorn --worker-tmp-dir /dev/shm seat_booking.wsgi
  envs:
  - key: DEBUG
    value: "False"
  http_port: 8000
databases:
- name: db
  engine: PG
  version: "15"
```

---

## 🔧 Production Dependencies

Update `requirements.txt`:

```txt
# Core
django>=5.1
requests
django-cors-headers
python-dotenv
pillow

# Production Server
gunicorn==21.2.0
whitenoise==6.6.0

# Database
psycopg2-binary==2.9.9
dj-database-url==2.1.0

# Monitoring (Optional)
sentry-sdk==1.39.1

# Performance (Optional)
redis==5.0.1
django-redis==5.4.0
```

---

## 🔒 Security Hardening

### 1. **Generate Secret Key**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 2. **Update CORS Settings**
```python
# In production, be specific
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
CORS_ALLOW_CREDENTIALS = True
```

### 3. **Rate Limiting**
Install django-ratelimit:
```bash
pip install django-ratelimit
```

Add to views:
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m')
def hold_multiple_seats(request):
    # ... existing code
```

---

## 📊 Database Migration

### PostgreSQL Setup

```bash
# Install PostgreSQL
# Windows: Download from postgresql.org

# Create database
psql -U postgres
CREATE DATABASE seat_booking;
CREATE USER seat_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE seat_booking TO seat_user;
\q

# Update .env
USE_MYSQL=False
DATABASE_URL=postgresql://seat_user:secure_password@localhost:5432/seat_booking

# Migrate
python manage.py migrate
python manage.py seed_data
```

---

## 🚀 Performance Optimization

### 1. **Enable Caching**

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 2. **Database Indexing**

```python
# models.py
class Seat(models.Model):
    # ... existing fields
    
    class Meta:
        indexes = [
            models.Index(fields=['show_time', 'status']),
            models.Index(fields=['held_by', 'status']),
        ]
```

### 3. **Static File Serving**

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... other middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## 📈 Monitoring & Logging

### Sentry Integration

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )
```

### Logging Configuration

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/seat_booking.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## ✅ Post-Deployment Checklist

- [ ] SSL certificate installed (Let's Encrypt)
- [ ] Environment variables set correctly
- [ ] Database backed up
- [ ] Static files collected
- [ ] CORS configured properly
- [ ] Admin panel accessible
- [ ] Stress test passed on production
- [ ] Monitoring/logging active
- [ ] Error tracking configured (Sentry)
- [ ] Backup strategy in place

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
    
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.14
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "your-app-name"
        heroku_email: "your-email@example.com"
```

---

## 📞 Support & Maintenance

### Backup Strategy
```bash
# Automated daily backups
0 2 * * * pg_dump seat_booking > /backups/seat_booking_$(date +\%Y\%m\%d).sql
```

### Health Check Endpoint
```python
# views.py
def health_check(request):
    return JsonResponse({'status': 'healthy', 'timestamp': timezone.now()})
```

---

**Your system is ready for production! 🚀**
