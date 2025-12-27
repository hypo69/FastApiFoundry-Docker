param(
    [Parameter(Mandatory=$false)]
    [string]$Type = "available"
)

Write-Host "Getting models list: $Type" -ForegroundColor Yellow

try {
    if ($Type -eq "loaded") {
        # Список загруженных моделей в сервисе
        $result = foundry service list 2>&1
    } else {
        # Список всех доступных моделей
        $result = foundry model list 2>&1
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Models list retrieved successfully" -ForegroundColor Green
        Write-Output $result
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