# 🔄 Синхронизация между Desktop и Laptop

## 📋 Quick Start

### На Desktop (Windows):
```powershell
# 🤖 Умная синхронизация (рекомендуется)
.\smart_sync.ps1

# 📝 С кастомным сообщением коммита
.\smart_sync.ps1 -Message "добавил новую фичу"

# ⚡ Принудительная синхронизация при конфликтах
.\smart_sync.ps1 -Force

# 📦 Простая синхронизация
.\sync.ps1  # или .\sync.bat
```

### На Laptop (Mac/Linux):
```bash
# 🤖 Умная синхронизация (рекомендуется)
./smart_sync.sh

# 📝 С кастомным сообщением
./smart_sync.sh "добавил новую фичу"

# 📦 Ручная синхронизация
git pull  # получить изменения
git add . && git commit -m "описание" && git push  # отправить
```

## 🎯 Workflow

### 1️⃣ Desktop → Laptop
1. Работаешь на Desktop
2. Запускаешь `sync.bat` 
3. На laptop: `git pull`

### 2️⃣ Laptop → Desktop  
1. Работаешь на laptop
2. Коммитишь: `git add . && git commit -m "..." && git push`
3. На Desktop: `git pull` (или `sync.bat` покажет что есть изменения)

## 🛠 Первоначальная настройка Laptop

```bash
# Клонируем репозиторий
git clone https://github.com/AndriiBogdanov/danov-music-studio.git
cd danov-music-studio

# Настраиваем Python окружение
python3 -m venv venv
source venv/bin/activate  # Mac/Linux

# Устанавливаем зависимости
pip install -r requirements.txt

# Настраиваем базу данных
python manage.py migrate
python manage.py collectstatic --noinput

# Запускаем сервер
python manage.py runserver
```

## 🤖 Умная синхронизация

**Smart Sync автоматически:**
- ✅ Получает изменения с сервера (`git pull`)
- ✅ Разрешает простые конфликты автоматически  
- ✅ Создает backup перед операциями
- ✅ Восстанавливает состояние при ошибках
- ✅ Очищает старые backups
- ✅ Использует безопасные Git стратегии

## ⚠️ Важные моменты

- **Smart Sync делает все автоматически** - просто запускай скрипт
- При серьезных конфликтах → будет создан backup
- База данных `db.sqlite3` не синхронизируется (исключена в .gitignore)
- Backups создаются в папках `.git_backup_*`

## 🔧 Полезные команды

```bash
# Проверить статус
git status

# Посмотреть историю
git log --oneline

# Отменить последний коммит (но оставить изменения)
git reset --soft HEAD~1

# Посмотреть удаленные изменения
git fetch && git log HEAD..origin/master --oneline
```

## 📱 GitHub репозиторий
https://github.com/AndriiBogdanov/danov-music-studio
