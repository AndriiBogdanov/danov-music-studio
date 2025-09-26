# Danov Music Studio - Сайт-визитка с бронированием

Современный сайт-визитка для музыкальной студии с системой бронирования на Django.

## Функциональность

- 🎵 Главная страница с информацией о студии
- 📅 Система бронирования студии
- 📧 Автоматическая отправка email на danovmusic@gmail.com
- 👨‍💼 Админ-панель для управления заявками
- 📱 Адаптивный дизайн
- 🎨 Современный UI/UX

## Технологии

- **Backend**: Django 5.2.4
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Email**: Django SMTP
- **Database**: SQLite (можно переключить на PostgreSQL/MySQL)

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd danovmusic-studio
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
```

### 3. Активация виртуального окружения

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 5. Настройка базы данных
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 7. Настройка email (опционально)

Отредактируйте файл `danovmusic_studio/settings.py`:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### 8. Запуск сервера
```bash
python manage.py runserver
```

Сайт будет доступен по адресу: http://127.0.0.1:8000/

## Структура проекта

```
danovmusic_studio/
├── booking/                 # Приложение для бронирования
│   ├── models.py           # Модель Booking
│   ├── views.py            # Представления
│   ├── forms.py            # Формы
│   ├── admin.py            # Админка
│   └── templates/          # HTML шаблоны
├── danovmusic_studio/      # Основные настройки проекта
├── static/                 # Статические файлы (CSS, JS, изображения)
├── manage.py              # Управление Django
└── requirements.txt       # Зависимости
```

## Страницы сайта

- **Главная** (`/`) - Информация о студии, услуги, преимущества
- **О студии** (`/about/`) - Подробная информация о студии и команде
- **Услуги** (`/services/`) - Список услуг и тарифы
- **Галерея** (`/gallery/`) - Фотографии студии и оборудования
- **Контакты** (`/contact/`) - Контактная информация
- **Бронирование** (`/booking/`) - Форма бронирования студии

## Админ-панель

Доступ к админ-панели: http://127.0.0.1:8000/admin/

Возможности:
- Просмотр всех заявок на бронирование
- Изменение статуса заявок
- Фильтрация и поиск заявок
- Экспорт данных

## Настройка email

Для работы отправки email необходимо:

1. Создать пароль приложения в Google аккаунте
2. Обновить настройки в `settings.py`:
   ```python
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-app-password'
   ```

## Разработка

### Добавление новых страниц

1. Создайте представление в `booking/views.py`
2. Добавьте URL в `booking/urls.py`
3. Создайте шаблон в `booking/templates/booking/`

### Изменение дизайна

Основные стили находятся в `static/css/style.css`

### Добавление новых полей в форму бронирования

1. Обновите модель в `booking/models.py`
2. Обновите форму в `booking/forms.py`
3. Создайте и примените миграции

## Лицензия

MIT License

## Контакты

- Email: danovmusic@gmail.com
- Телефон: +7 (999) 123-45-67 