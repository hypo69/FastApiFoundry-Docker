Write-Host "Checking Foundry service status..." -ForegroundColor Yellow

try {
    $result = foundry service status 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Service status retrieved successfully" -ForegroundColor Green
        Write-Output $result
        exit 0
    } else {
        Write-Host "❌ Failed to get service status" -ForegroundColor Red
        Write-Error $result
        exit 1
    }
} catch {
    Write-Host "❌ Error checking service status: $_" -ForegroundColor Red
    exit 1
}