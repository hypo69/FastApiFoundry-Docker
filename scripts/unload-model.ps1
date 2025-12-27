param(
    [Parameter(Mandatory=$true)]
    [string]$ModelId
)

Write-Host "Unloading model: $ModelId" -ForegroundColor Yellow

try {
    foundry model unload $ModelId
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Model $ModelId unloaded successfully" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ Failed to unload model $ModelId" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error unloading model: $_" -ForegroundColor Red
    exit 1
}