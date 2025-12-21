# Открыть веб-интерфейс в браузере
param(
    [int]$Port = 8000
)

$url = "http://localhost:$Port"
Write-Host "🌐 Открываю $url в браузере..." -ForegroundColor Cyan

Start-Process $url

Write-Host "✅ Браузер открыт!" -ForegroundColor Green
