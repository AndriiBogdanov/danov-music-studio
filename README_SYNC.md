# 🔄 Синхронизация между Desktop и Laptop

## 📋 Quick Start

### На Desktop (Windows):
```bash
# После внесения изменений
sync.bat
```

### На Laptop (Mac/Linux):
```bash
# Получить изменения с Desktop
git pull

# После внесения изменений на laptop
git add .
git commit -m "описание изменений"
git push
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

## ⚠️ Важные моменты

- **Всегда делай `git pull` перед началом работы**
- **Не забывай синхронизировать изменения после работы**
- Если есть конфликты → разбирай их в IDE
- База данных `db.sqlite3` не синхронизируется (исключена в .gitignore)

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
