# Deployment Guide

This guide covers deploying the Crippple Backend to production.

## Pre-deployment Checklist

Before deploying to production, make sure to:

### 1. Security Settings

Update `crippple_backend/settings.py`:

```python
# Set DEBUG to False
DEBUG = False

# Set SECRET_KEY from environment variable
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configure ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'your-domain.com',
    'www.your-domain.com',
    'api.your-domain.com',
]

# Configure CORS for specific origins
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.com",
    "https://www.your-frontend.com",
]
```

### 2. Database Configuration

Set environment variables:

```bash
export DB_NAME=your_database_name
export DB_USER=your_database_user
export DB_PASSWORD=your_secure_password
export DB_HOST=your_database_host
export DB_PORT=5432
export DB_DIRECT_HOST=your_direct_database_host
export DB_DIRECT_PORT=5432
```

### 3. Install Production Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
```

### 4. Static Files

```bash
python manage.py collectstatic --noinput
```

### 5. Database Migrations

```bash
python manage.py migrate --settings=crippple_backend.settings --database=direct
```

## Deployment Options

### Option 1: Traditional Server (Ubuntu/Debian)

1. **Install system dependencies:**
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv nginx postgresql
```

2. **Set up virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

3. **Configure Gunicorn:**
```bash
pip install gunicorn
gunicorn crippple_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

4. **Configure Nginx as reverse proxy:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for scraping operations
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    location /static/ {
        alias /path/to/static/files/;
    }
}
```

5. **Set up systemd service:**

Create `/etc/systemd/system/crippple-backend.service`:
```ini
[Unit]
Description=Crippple Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Crippple-Backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn crippple_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable crippple-backend
sudo systemctl start crippple-backend
```

### Option 2: Docker

1. **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "crippple_backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

2. **Build and run:**
```bash
docker build -t crippple-backend .
docker run -p 8000:8000 \
  -e DB_NAME=your_db \
  -e DB_USER=your_user \
  -e DB_PASSWORD=your_password \
  -e DB_HOST=your_host \
  crippple-backend
```

### Option 3: Cloud Platforms

#### Heroku

1. Create `Procfile`:
```
web: gunicorn crippple_backend.wsgi:application --log-file -
```

2. Create `runtime.txt`:
```
python-3.11.6
```

3. Deploy:
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python manage.py migrate
```

#### Railway

1. Add to `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "gunicorn crippple_backend.wsgi:application",
    "restartPolicyType": "on_failure"
  }
}
```

## Performance Optimization

### 1. Caching

Add Redis for caching search results:

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 2. Celery for Background Tasks

For long-running scraping operations, consider using Celery:

```python
# celery.py
from celery import Celery

app = Celery('crippple_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 3. Rate Limiting

Add rate limiting to prevent abuse:

```bash
pip install django-ratelimit
```

```python
# views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m')
@api_view(['GET'])
def search_apparel(request):
    # ... existing code
```

## Monitoring

### Application Monitoring

Use tools like:
- **Sentry** for error tracking
- **New Relic** or **Datadog** for performance monitoring
- **Prometheus** + **Grafana** for metrics

### Logs

Configure logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/crippple-backend/app.log',
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

## Troubleshooting

### Playwright Issues in Production

If Playwright browsers don't work:

1. Install dependencies:
```bash
playwright install-deps chromium
```

2. Run with --no-sandbox:
```python
browser = p.chromium.launch(
    headless=True,
    args=['--no-sandbox', '--disable-setuid-sandbox']
)
```

### Memory Issues

Scraping is memory-intensive. Recommended:
- Minimum 2GB RAM
- 4GB RAM recommended
- Use swap space if needed

### Timeout Issues

Increase timeouts in Nginx/Gunicorn:
```bash
gunicorn --timeout 300 crippple_backend.wsgi:application
```

## Backup Strategy

1. **Database backups:**
```bash
pg_dump -h hostname -U username dbname > backup.sql
```

2. **Automated backups:**
Set up cron jobs or use cloud provider backup features.

## Scaling

For high traffic:

1. **Horizontal scaling:** Use load balancer with multiple instances
2. **Background workers:** Use Celery with multiple workers
3. **CDN:** Use CDN for static assets
4. **Database optimization:** Use read replicas for database

## Security

1. Keep dependencies updated: `pip install -U -r requirements.txt`
2. Use HTTPS (Let's Encrypt for free certificates)
3. Regular security audits
4. Rate limiting
5. Input validation
6. CSRF protection (enabled by default in Django)
