param(
    [Parameter(Mandatory=$true)]
    [string]$ModelId
)

Write-Host "Loading model: $ModelId" -ForegroundColor Green

try {
    foundry model load $ModelId
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Model $ModelId loaded successfully" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ Failed to load model $ModelId" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error loading model: $_" -ForegroundColor Red
    exit 1
}