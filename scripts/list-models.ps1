param(
    [Parameter(Mandatory=$false)]
    [string]$Type = "available"
)

Write-Host "Getting models list: $Type" -ForegroundColor Yellow

try {
    if ($Type -eq "loaded") {
        # Список загруженных моделей в сервисе
        Write-Host "Checking loaded models..." -ForegroundColor Cyan
        $result = foundry service list 2>&1
        
        # Если команда не работает, пробуем альтернативный способ
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Trying alternative method..." -ForegroundColor Yellow
            # Проверяем через HTTP API
            try {
                $foundryUrl = "http://localhost:50477/v1/models"
                $response = Invoke-RestMethod -Uri $foundryUrl -TimeoutSec 5 -ErrorAction Stop
                if ($response -and $response.data) {
                    foreach ($model in $response.data) {
                        Write-Output $model.id
                    }
                    exit 0
                }
            } catch {
                Write-Host "No models loaded or Foundry not accessible" -ForegroundColor Yellow
                exit 0
            }
        }
    } else {
        # Список всех доступных моделей
        Write-Host "Getting available models..." -ForegroundColor Cyan
        $result = foundry model list 2>&1
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Models list retrieved successfully" -ForegroundColor Green
        # Фильтруем только строки с моделями
        $result | ForEach-Object {
            $line = $_.ToString().Trim()
            if ($line -and 
                -not $line.StartsWith('Available') -and 
                -not $line.StartsWith('Service') -and 
                -not $line.StartsWith('---') -and 
                -not $line.StartsWith('✅') -and 
                -not $line.StartsWith('Getting') -and
                -not $line.StartsWith('Checking') -and
                $line -notmatch '^\s*$') {
                Write-Output $line
            }
        }
        exit 0
    } else {
        Write-Host "❌ Failed to get models list" -ForegroundColor Red
        Write-Error $result
        exit 1
    }
} catch {
    Write-Host "❌ Error getting models list: $_" -ForegroundColor Red
    exit 1
}