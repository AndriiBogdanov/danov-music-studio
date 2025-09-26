# 🔧 После включения виртуализации в BIOS

## 📋 Что включить в BIOS:
- **Intel VT-x** (для Intel) или **AMD-V** (для AMD)
- **Hyper-V** 
- **Virtualization Technology**
- **SVM Mode** (для AMD)

## 🚀 Команды после перезагрузки:

### 1. Проверяем WSL:
```powershell
wsl --version
```

### 2. Устанавливаем Ubuntu:
```powershell
wsl --install Ubuntu
```

### 3. После установки Ubuntu:
```bash
wsl
sudo apt update
sudo apt install sshpass -y
```

### 4. Автоматический деплой:
```bash
sshpass -p '8mAsOR27' ssh adminuser@217.154.120.187 "cd /var/www/danov-studio && git pull origin master && source venv/bin/activate && python manage.py collectstatic --noinput && echo 'Qaz444666!' | sudo -S systemctl restart danov-studio"
```

## 🎯 Альтернативный план (если WSL не работает):

### Git Bash способ:
```bash
# В Git Bash терминале
ssh adminuser@217.154.120.187
# Ввести пароль: 8mAsOR27
```

### PuTTY способ:
1. Скачать PuTTY
2. Подключиться к 217.154.120.187
3. Логин: adminuser, пароль: 8mAsOR27

## 📱 Результат:
После деплоя на мобильной версии логотип Danov Music будет отображаться **перед** текстом "Create professional sound"!

**Сайт доступен**: http://217.154.120.187:8847

