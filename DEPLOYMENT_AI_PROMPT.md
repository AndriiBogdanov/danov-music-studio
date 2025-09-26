# 🚀 Промпт для ИИ: Подготовка Danov Music Studio к Production/DNS

## 📋 Контекст проекта

Есть готовый сайт музыкальной студии на Django с **МАКСИМАЛЬНОЙ БЕЗОПАСНОСТЬЮ**. Нужно подготовить его для размещения на домене (DNS setup) и production развертывания.

## 🛡️ Текущий Уровень Безопасности: **МАКСИМАЛЬНЫЙ**

**УЖЕ РЕАЛИЗОВАНО:**
- ✅ 6-уровневая антиспам система (rate limiting, дубликаты, honey pot, валидация, IP трекинг, логирование)
- ✅ Django-axes брутфорс защита (5 попыток = блокировка на 1 час)
- ✅ Content Security Policy (CSP) против XSS атак
- ✅ Security headers (XSS-Protection, HSTS, X-Frame-Options, CSRF, etc.)
- ✅ Переменные окружения (.env) для всех секретов
- ✅ Безопасные error pages (400, 403, 404, 500) с логированием
- ✅ Security logging в logs/security.log
- ✅ Session security (HttpOnly, Secure, SameSite, signed cookies)
- ✅ File upload protection (размер, права доступа)
- ✅ Password validation (минимум 12 символов)
- ✅ IP tracking и автоматическая блокировка подозрительных адресов

**ФАЙЛЫ БЕЗОПАСНОСТИ:**
- `SECURITY_COMPREHENSIVE_REPORT.md` - подробный отчет о безопасности
- `ANTISPAM_QUICKSTART.md` - руководство по антиспам системе
- `booking/middleware.py` - AntiSpamMiddleware
- `booking/templates/booking/errors/` - безопасные error pages
- `.env` - переменные окружения
- `logs/security.log` - логи безопасности

## 🎯 Задача

Переделай сайт под реальный домен и production окружение. Выполни следующие задачи:

### 1. **Настройка для Production**

#### Обнови `settings.py`:
```python
# Измени эти настройки:
DEBUG = False
ALLOWED_HOSTS = ['danovmusic.com', 'www.danovmusic.com', 'yourdomain.com']

# Добавь security настройки:
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Настрой CSRF для домена:
CSRF_TRUSTED_ORIGINS = ['https://danovmusic.com', 'https://www.danovmusic.com']

# Настрой CORS если нужно:
CORS_ALLOWED_ORIGINS = ['https://danovmusic.com', 'https://www.danovmusic.com']
```

#### Создай переменные окружения `.env`:
```bash
SECRET_KEY=your-super-secret-production-key-here
DEBUG=False
ALLOWED_HOSTS=danovmusic.com,www.danovmusic.com

# Email settings
EMAIL_HOST_USER=danovwebsite@gmail.com
EMAIL_HOST_PASSWORD=your-real-app-password
BOOKING_NOTIFICATION_EMAIL=danovmusic@gmail.com

# reCAPTCHA (замени на реальные ключи)
RECAPTCHA_PUBLIC_KEY=your-real-public-key
RECAPTCHA_PRIVATE_KEY=your-real-private-key

# Database (если используешь PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/danovmusic_db
```

#### Обнови `requirements.txt`:
```txt
Django==5.2.4
django-recaptcha==4.1.0
python-decouple==3.8  # Для переменных окружения
gunicorn==21.2.0      # WSGI сервер
whitenoise==6.6.0     # Статика
psycopg2-binary==2.9.9  # PostgreSQL (опционально)
```

### 2. **Создай файлы для развертывания**

#### `nginx.conf`:
```nginx
server {
    listen 80;
    server_name danovmusic.com www.danovmusic.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name danovmusic.com www.danovmusic.com;
    
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/your/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### `docker-compose.yml` (если используешь Docker):
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
    env_file:
      - .env
    volumes:
      - static_volume:/app/staticfiles
    depends_on:
      - db
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: danovmusic_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your-db-password
    volumes:
      - postgres_data:/var/lib/postgresql/data/
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/var/www/html/static
      
volumes:
  postgres_data:
  static_volume:
```

### 3. **Дополнительная Безопасность и Производительность**

#### 🔒 ВАЖНО: Проверь и доделай безопасность (если нужно)

**Убедись что все настроено:**
- [ ] Все security headers работают (проверь в браузере F12 → Network)
- [ ] CSP правильно настроен для домена
- [ ] Axes блокирует после 5 неудачных попыток входа
- [ ] Антиспам система работает на /booking/
- [ ] Error pages показывают 400, 403, 404, 500 без раскрытия информации
- [ ] Логи security.log пишутся в logs/
- [ ] .env файл не попадает в git (добавь в .gitignore)

**Дополнительные настройки для production:**

#### Добавь middleware для безопасности:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Для статики
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Если нужно CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'booking.middleware.AntiSpamMiddleware',
]
```

#### Настрой кэширование:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

#### Настрой логирование:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/danovmusic.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'booking': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 4. **Управляющие команды**

#### Создай `manage_production.py`:
```python
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'danovmusic_studio.settings_production')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
```

#### `deploy.sh` скрипт:
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Danov Music Studio..."

# Обновить код
git pull origin main

# Установить зависимости
pip install -r requirements.txt

# Миграции
python manage.py migrate --noinput

# Собрать статику
python manage.py collectstatic --noinput

# Перезапустить Gunicorn
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Deployment completed!"
```

### 5. **Обнови URL-ы в коде**

#### В `views.py` замени все localhost на реальный домен:
```python
# Найди и замени:
base_url = request.build_absolute_uri('/')[:-1]
# На:
base_url = 'https://danovmusic.com'  # или используй request.build_absolute_uri

# В email шаблонах тоже замени ссылки
```

#### В `templates` обнови метатеги:
```html
<meta property="og:url" content="https://danovmusic.com">
<meta property="og:site_name" content="Danov Music Studio">
<link rel="canonical" href="https://danovmusic.com">
```

### 6. **SEO и производительность**

#### Добавь `sitemap.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://danovmusic.com/</loc>
        <priority>1.0</priority>
        <changefreq>weekly</changefreq>
    </url>
    <url>
        <loc>https://danovmusic.com/booking/</loc>
        <priority>0.9</priority>
        <changefreq>weekly</changefreq>
    </url>
    <!-- Добавь все страницы -->
</urlset>
```

#### Создай `robots.txt`:
```txt
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /confirm/
Disallow: /reject/

Sitemap: https://danovmusic.com/sitemap.xml
```

### 7. **Мониторинг и аналитика**

#### Добавь Google Analytics в `base.html`:
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🔧 Дополнительные задачи

1. **Проверь все абсолютные пути** и замени их на относительные или используй переменные окружения
2. **Оптимизируй изображения** - добавь WebP версии, сжми PNG/JPG
3. **Настрой backup базы данных** - создай cron job для автоматических бэкапов
4. **Добавь health check** endpoint для мониторинга
5. **Настрой Let's Encrypt** для автоматического обновления SSL сертификатов

## 📁 Файлы которые нужно создать/изменить:

- `danovmusic_studio/settings_production.py`
- `.env.example` 
- `requirements_production.txt`
- `nginx.conf`
- `docker-compose.yml`
- `deploy.sh`
- `gunicorn.conf.py`
- `static/robots.txt`
- `static/sitemap.xml`

## ⚠️ Важные моменты:

1. **Никогда не коммить** `.env` файл в git
2. **Обязательно смени SECRET_KEY** для production
3. **Настрой мониторинг ошибок** (Sentry рекомендуется)
4. **Проверь все внешние ссылки** в письмах и на сайте
5. **Протестируй антиспам систему** на production

## 🎯 Результат:

После выполнения всех задач сайт будет полностью готов для размещения на реальном домене с максимальной безопасностью, производительностью и SEO оптимизацией.

---

**Выполни все эти задачи пошагово и создай production-ready версию сайта Danov Music Studio!** 