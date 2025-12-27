param(
    [Parameter(Mandatory=$true)]
    [string]$ModelId
)

Write-Host "Downloading model to cache: $ModelId" -ForegroundColor Yellow

try {
    foundry model download $ModelId
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Model $ModelId downloaded successfully" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ Failed to download model $ModelId" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error downloading model: $_" -ForegroundColor Red
    exit 1
}