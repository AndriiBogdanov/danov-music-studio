# 🚀 VPS Deployment Guide для Danov Music Studio

Пошаговая инструкция по деплою Django сайта на VPS сервер.

## 📋 Требования

- **VPS сервер** с Ubuntu 20.04+ (или Debian)
- **Домен** настроенный на IP сервера
- **SSH доступ** к серверу
- **Email** для SSL сертификата

## 🎯 Быстрый деплой (рекомендуется)

### 1. Подготовка на локальном компьютере

```bash
# Упакуй проект в архив (исключая ненужные файлы)
tar -czf danov-studio.tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='db.sqlite3' \
  --exclude='logs/*.log' \
  .
```

### 2. Загрузка на сервер

```bash
# Скопируй архив на сервер
scp danov-studio.tar.gz user@your-server-ip:/tmp/

# Подключись к серверу
ssh user@your-server-ip
```

### 3. Распаковка и быстрая настройка

```bash
# Создай директорию проекта
sudo mkdir -p /var/www/danov-studio
cd /var/www/danov-studio

# Распакуй проект
sudo tar -xzf /tmp/danov-studio.tar.gz

# Смени владельца (замени 'user' на свое имя пользователя)
sudo chown -R $USER:$USER /var/www/danov-studio

# Сделай скрипты исполняемыми
chmod +x deploy_quick.sh
chmod +x deploy_vps.sh

# Запусти быстрый деплой
./deploy_quick.sh
```

### 4. Настройка переменных окружения

```bash
# Отредактируй файл .env
nano .env

# Обязательно измени:
# - SECRET_KEY (используй сгенерированный)
# - ALLOWED_HOSTS (добавь свой домен)
# - EMAIL_HOST_PASSWORD (пароль приложения Gmail)
# - RECAPTCHA ключи
```

### 5. Настройка базы данных PostgreSQL

```bash
# Установи PostgreSQL
sudo apt install postgresql postgresql-contrib

# Создай базу данных
sudo -u postgres createuser danovmusic_user
sudo -u postgres createdb danovmusic_db -O danovmusic_user
sudo -u postgres psql -c "ALTER USER danovmusic_user PASSWORD 'your-password';"

# Обнови .env с данными БД
```

### 6. Настройка Gunicorn и Supervisor

```bash
# Установи Supervisor
sudo apt install supervisor

# Создай конфигурацию Gunicorn
sudo nano /etc/supervisor/conf.d/danov-studio.conf
```

Добавь в файл:
```ini
[program:danov-studio]
command=/var/www/danov-studio/venv/bin/gunicorn --workers 3 --bind unix:/var/www/danov-studio/danov-studio.sock danovmusic_studio.wsgi:application
directory=/var/www/danov-studio
user=your-username
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/danov-studio.log
environment=DJANGO_SETTINGS_MODULE="danovmusic_studio.settings_vps"
```

```bash
# Перезапусти Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start danov-studio
```

### 7. Настройка Nginx

```bash
# Скопируй конфигурацию Nginx
sudo cp nginx_danov_studio.conf /etc/nginx/sites-available/danov-studio

# Отредактируй домен в конфигурации
sudo nano /etc/nginx/sites-available/danov-studio
# Замени 'yourdomain.com' на свой домен

# Активируй сайт
sudo ln -s /etc/nginx/sites-available/danov-studio /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Проверь конфигурацию
sudo nginx -t

# Перезапусти Nginx
sudo systemctl restart nginx
```

### 8. Настройка SSL с Let's Encrypt

```bash
# Установи Certbot
sudo apt install certbot python3-certbot-nginx

# Получи SSL сертификат
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 9. Финальная проверка

```bash
# Проверь статус сервисов
sudo systemctl status nginx
sudo supervisorctl status danov-studio

# Проверь логи если есть проблемы
sudo tail -f /var/log/danov-studio.log
sudo tail -f /var/log/nginx/danov-studio.error.log
```

## 🔧 Полный автоматический деплой

Если хочешь полностью автоматический деплой:

```bash
# Отредактируй переменные в deploy_vps.sh
nano deploy_vps.sh

# Запусти полный деплой (требует root)
sudo ./deploy_vps.sh
```

## 📱 После деплоя

1. **Протестируй сайт**: https://yourdomain.com
2. **Зайди в админку**: https://yourdomain.com/admin/
3. **Проверь email уведомления** через форму бронирования
4. **Настрой мониторинг** и бэкапы

## 🛠 Полезные команды

```bash
# Перезапуск приложения
sudo supervisorctl restart danov-studio

# Обновление кода
cd /var/www/danov-studio
git pull origin main
source venv/bin/activate
pip install -r requirements_vps.txt
python manage.py collectstatic --noinput
python manage.py migrate
sudo supervisorctl restart danov-studio

# Просмотр логов
sudo tail -f /var/log/danov-studio.log
sudo tail -f /var/log/nginx/danov-studio.error.log

# Создание суперпользователя
cd /var/www/danov-studio
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=danovmusic_studio.settings_vps
python manage.py createsuperuser
```

## 🔒 Безопасность

- ✅ SSL сертификат (HTTPS)
- ✅ Firewall (UFW)
- ✅ Регулярные обновления системы
- ✅ Надежные пароли
- ✅ Backup базы данных

## 📞 Поддержка

Если возникли проблемы, проверь:
1. Логи приложения и Nginx
2. Статус сервисов
3. Настройки DNS домена
4. Firewall и порты (80, 443)

---

🎵 **Удачи с деплоем Danov Music Studio!** 🎵





