# 🚀 Деплой Django на Railway

## 📋 Подготовка

### 1. Установите Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Войдите в Railway
```bash
railway login
```

## 🚀 Деплой

### 1. Инициализируйте проект
```bash
railway init
```

### 2. Подключите базу данных PostgreSQL
```bash
railway add
# Выберите PostgreSQL
```

### 3. Настройте переменные окружения
В Railway Dashboard или через CLI:
```bash
railway variables set SECRET_KEY=your-secret-key-here
railway variables set DEBUG=False
railway variables set DJANGO_SETTINGS_MODULE=danovmusic_studio.settings_railway
```

### 4. Деплой
```bash
railway up
```

## 🔧 Настройка

### Переменные окружения:
- `SECRET_KEY` - секретный ключ Django
- `DEBUG` - False для продакшена
- `DJANGO_SETTINGS_MODULE` - danovmusic_studio.settings_railway
- `DATABASE_URL` - автоматически предоставляется Railway

### Команды:
```bash
# Посмотреть логи
railway logs

# Открыть сайт
railway open

# Запустить локально
railway run python manage.py runserver

# Выполнить миграции
railway run python manage.py migrate

# Создать суперпользователя
railway run python manage.py createsuperuser
```

## 🌐 Домен
Railway автоматически предоставит HTTPS домен вида:
`https://your-project-name-production.up.railway.app`

## 💰 Стоимость
- Бесплатно: $5 кредитов/месяц
- Достаточно для небольших проектов 