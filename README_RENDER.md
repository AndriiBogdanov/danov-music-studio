# 🚀 Деплой Django на Render (БЕСПЛАТНО!)

## 🆓 **Render - Лучший бесплатный хостинг для Django**

### ✅ **Преимущества:**
- **Полностью бесплатно** для веб-сервисов
- **PostgreSQL** включен в бесплатный план
- **Автоматические деплои** из Git
- **SSL сертификаты** включены
- **Простая настройка** - один клик

## 📋 **Пошаговая инструкция:**

### **1. Зарегистрируйтесь на Render**
Перейдите на [render.com](https://render.com) и создайте аккаунт

### **2. Подключите GitHub репозиторий**
1. Нажмите "New +"
2. Выберите "Web Service"
3. Подключите ваш GitHub репозиторий

### **3. Настройте сервис**
- **Name:** `danov-music-studio`
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn danovmusic_studio.wsgi:application`

### **4. Добавьте базу данных**
1. Нажмите "New +"
2. Выберите "PostgreSQL"
3. Назовите `danov-music-studio-db`

### **5. Настройте переменные окружения**
В настройках веб-сервиса добавьте:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=danovmusic_studio.settings_render
DATABASE_URL=postgresql://... (автоматически от базы данных)
```

### **6. Деплой**
Нажмите "Create Web Service" - Render автоматически:
- Установит зависимости
- Применит миграции
- Запустит сервис

## 🌐 **Домен**
Render даст вам HTTPS домен вида:
`https://danov-music-studio.onrender.com`

## 💰 **Стоимость: 0$**
- **Бесплатно** для веб-сервисов
- **Бесплатно** PostgreSQL до 1GB
- **Бесплатно** SSL сертификаты
- **Бесплатно** автоматические деплои

## 🔧 **Управление**
- **Автоматические деплои** при push в Git
- **Логи** в реальном времени
- **Мониторинг** производительности
- **Масштабирование** одним кликом

## 🚀 **Готово!**
Ваш сайт будет доступен по адресу:
`https://danov-music-studio.onrender.com` 