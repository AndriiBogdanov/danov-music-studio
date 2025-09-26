@echo off
echo ========================================
echo    Деплой Danov Music Studio на Vercel
echo ========================================

echo.
echo 1. Проверка установки Vercel CLI...
vercel --version >nul 2>&1
if errorlevel 1 (
    echo Vercel CLI не установлен. Устанавливаем...
    npm install -g vercel
) else (
    echo Vercel CLI уже установлен.
)

echo.
echo 2. Проверка логина...
vercel whoami >nul 2>&1
if errorlevel 1 (
    echo Требуется логин в Vercel...
    vercel login
) else (
    echo Уже авторизован в Vercel.
)

echo.
echo 3. Сборка статических файлов...
python manage.py collectstatic --noinput

echo.
echo 4. Деплой на Vercel...
vercel --prod

echo.
echo ========================================
echo    Деплой завершен!
echo ========================================
pause 