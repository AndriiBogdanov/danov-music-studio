# 🚀 Инструкции по деплою для твоего VPS

## 📋 Данные сервера:
- **User:** root / adminuser  
- **Password:** 8mAsOR27
- **SSH Key:** ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMRdAobdouVlPapDjX7a3SOz2+Y6M9AnZ5esOYsa3OLn

## 🎯 Что нужно знать:
- **IP адрес сервера** - ?
- **Домен** - какой домен будем использовать?

## 🚀 Варианты деплоя:

### Вариант 1: Автоматический деплой (рекомендую)

1. **Настрой скрипт деплоя:**
```bash
# Отредактируй deploy_to_vps.sh
nano deploy_to_vps.sh

# Измени эти строки:
SERVER_IP="YOUR_SERVER_IP"    # Твой IP сервера
DOMAIN="yourdomain.com"       # Твой домен
```

2. **Запусти деплой:**
```bash
chmod +x deploy_to_vps.sh
./deploy_to_vps.sh
```

### Вариант 2: Ручной деплой

1. **Упакуй проект:**
```bash
tar -czf danov-studio.tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='db.sqlite3' \
  .
```

2. **Загрузи на сервер:**
```bash
scp danov-studio.tar.gz root@YOUR_SERVER_IP:/tmp/
```

3. **Подключись к серверу:**
```bash
ssh root@YOUR_SERVER_IP
# Пароль: 8mAsOR27
```

4. **Распакуй и настрой:**
```bash
cd /var/www
mkdir danov-studio
cd danov-studio
tar -xzf /tmp/danov-studio.tar.gz

# Запусти быстрый деплой
chmod +x deploy_quick.sh
./deploy_quick.sh
```

## 🔧 После деплоя:

### 1. Настрой переменные окружения
```bash
nano .env

# Обязательно измени:
SECRET_KEY=сгенерированный-ключ
ALLOWED_HOSTS=твой-домен.com,www.твой-домен.com,IP-сервера
EMAIL_HOST_PASSWORD=твой-пароль-приложения-gmail
```

### 2. Настрой Nginx
```bash
# Скопируй конфигурацию
cp nginx_danov_studio.conf /etc/nginx/sites-available/danov-studio

# Измени домен
nano /etc/nginx/sites-available/danov-studio
# Замени 'yourdomain.com' на свой домен

# Активируй сайт
ln -s /etc/nginx/sites-available/danov-studio /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
```

### 3. Настрой SSL
```bash
# Установи сертификат
certbot --nginx -d твой-домен.com -d www.твой-домен.com
```

## 🎵 Готово!

Сайт будет доступен по адресу: **https://твой-домен.com**

## 📞 Если нужна помощь:

Скажи мне:
1. **IP адрес сервера**
2. **Домен который будем использовать**

И я настрою автоматический деплой! 🚀





