Write-Host "🔄 Синхронизация изменений с GitHub..." -ForegroundColor Cyan

# Добавляем все изменения
git add .

# Проверяем есть ли изменения для коммита
$gitStatus = git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Нет изменений для синхронизации" -ForegroundColor Green
    Read-Host "Нажмите Enter для выхода"
    exit 0
}

# Запрашиваем сообщение коммита или используем автоматическое
$commitMsg = Read-Host "💬 Сообщение коммита (Enter для авто)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $date = Get-Date -Format "yyyy-MM-dd HH:mm"
    $commitMsg = "chore: sync changes $date"
}

# Делаем коммит
Write-Host "📝 Создание коммита..." -ForegroundColor Yellow
git commit -m $commitMsg
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при коммите" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# Отправляем в GitHub
Write-Host "📤 Отправка в GitHub..." -ForegroundColor Yellow
git push
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при push в GitHub" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "✅ Синхронизация завершена!" -ForegroundColor Green
Write-Host "📱 Теперь можно работать с ноутбука: git pull" -ForegroundColor Cyan
Read-Host "Нажмите Enter для выхода"
