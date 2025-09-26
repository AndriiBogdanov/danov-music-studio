# Email Setup Instructions / Инструкция по настройке Email

## 🔐 Настройка Gmail для сайта Danov Music Studio

### 1. Создание пароля приложения для `danovwebsite@gmail.com`

**🇩🇪 Für deutsche Benutzeroberfläche / Для немецкого интерфейса:**

1. **Войдите в аккаунт** `danovwebsite@gmail.com`
2. **Перейдите в настройки Google**: https://myaccount.google.com/
3. **Sicherheit** (Безопасность) → **Bestätigung in zwei Schritten** (Двухэтапная аутентификация)
   - ⚠️ **Wichtig**: Muss aktiviert sein! / Должна быть включена!
4. **App-Passwörter** (Пароли приложений) → **App auswählen**: Sonstige (eigener Name)
5. **Name eingeben**: `Danov Music Studio Website`
6. **Generiertes Passwort kopieren** (16 Zeichen) / Скопируйте сгенерированный пароль

**🔍 Если не можете найти "App-Passwörter":**

**Способ 1 - Прямая ссылка:**
https://myaccount.google.com/apppasswords

**Способ 2 - Пошагово:**
1. https://myaccount.google.com/
2. Links: **Sicherheit** (Безопасность)
3. Unter "Bei Google anmelden" → **Bestätigung in zwei Schritten**
4. Scrollen Sie nach unten → **App-Passwörter**

**Способ 3 - Если нет "App-Passwörter":**
1. Сначала включите **Bestätigung in zwei Schritten** (2FA)
2. После включения 2FA появится опция **App-Passwörter**

### 2. Обновление настроек Django

Откройте файл `danovmusic_studio/settings.py` и замените:

```python
EMAIL_HOST_PASSWORD = 'your-app-password'
```

На:

```python
EMAIL_HOST_PASSWORD = 'ваш-16-символьный-пароль-приложения'
```

### 3. Как работает система

✅ **От кого отправляются письма**: `danovwebsite@gmail.com`  
✅ **Куда приходят бронирования**: `danovmusic@gmail.com`  
✅ **Название отправителя**: "Danov Music Studio"

### 4. Пример письма о бронировании

```
От: Danov Music Studio <danovwebsite@gmail.com>
Кому: danovmusic@gmail.com
Тема: New booking request from John Doe

New studio booking request:

Name: John Doe
Email: john@example.com
Phone: +49 175 413 75 18
Date: 2025-01-15
Time: 14:00
Duration: 2 hours
Service: Recording
Message: Need to record vocals for new track

Request created: 2025-01-15 12:30:45
```

### 5. Тестирование

После настройки пароля приложения:

1. Перезапустите Django сервер
2. Перейдите на страницу бронирования
3. Заполните форму и отправьте
4. Проверьте почту `danovmusic@gmail.com`

### 6. Безопасность

⚠️ **Важно**:
- Никогда не публикуйте пароль приложения в коде
- Используйте переменные окружения для production
- Пароль приложения работает только для этого сайта

### 7. Возможные проблемы

**Если письма не отправляются**:
1. Проверьте, что двухэтапная аутентификация включена
2. Убедитесь, что пароль приложения введен правильно
3. Проверьте, что в Gmail разрешены "менее безопасные приложения" (обычно не нужно)

**В логах Django смотрите ошибки**:
```bash
venv\Scripts\python.exe manage.py runserver
```

---

**Готово!** 🎉 Теперь сайт будет отправлять все бронирования с аккаунта `danovwebsite@gmail.com` на почту `danovmusic@gmail.com`. 