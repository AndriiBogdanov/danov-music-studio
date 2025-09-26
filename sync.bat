@echo off
echo 🔄 Синхронизация изменений с GitHub...

REM Добавляем все изменения
git add .

REM Проверяем есть ли изменения для коммита
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo ✅ Нет изменений для синхронизации
    pause
    exit /b 0
)

REM Запрашиваем сообщение коммита или используем автоматическое
set /p commit_msg="💬 Сообщение коммита (Enter для авто): "
if "%commit_msg%"=="" (
    for /f "tokens=1-3 delims=./ " %%a in ('date /t') do (
        for /f "tokens=1-2 delims=: " %%d in ('time /t') do (
            set commit_msg=chore: sync changes %%c-%%b-%%a %%d:%%e
        )
    )
)

REM Делаем коммит
git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo ❌ Ошибка при коммите
    pause
    exit /b 1
)

REM Отправляем в GitHub
echo 📤 Отправка в GitHub...
git push
if %errorlevel% neq 0 (
    echo ❌ Ошибка при push в GitHub
    pause
    exit /b 1
)

echo ✅ Синхронизация завершена!
echo 📱 Теперь можно работать с ноутбука: git pull
pause
