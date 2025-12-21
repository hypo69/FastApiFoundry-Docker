# Тестирование API endpoints
# ============================================================================

param(
    [int]$Port = 8000,
    [string]$Host = "localhost"
)

$BaseURL = "http://$Host`:$Port/api/v1"

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method = "GET",
        [string]$Endpoint,
        [object]$Body = $null
    )

    $fullUrl = "$BaseURL$Endpoint"
    Write-Host "Testing: $Name" -ForegroundColor Cyan
    Write-Host "URL: $fullUrl" -ForegroundColor Gray

    try {
        $params = @{
            Uri     = $fullUrl
            Method  = $Method
            TimeoutSec = 30
            ErrorAction = 'Stop'
        }

        if ($Body) {
            $params['ContentType'] = 'application/json'
            $params['Body'] = $Body | ConvertTo-Json
        }

        $response = Invoke-RestMethod @params

        Write-Host "✅ Status: OK" -ForegroundColor Green
        Write-Host "Response:" -ForegroundColor Gray
        $response | ConvertTo-Json | Write-Host
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
    Write-Host ""
}

Clear-Host
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          FastAPI Foundry - API Test Suite                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing URL: $BaseURL" -ForegroundColor Yellow
Write-Host ""

# Test 1: Health Check
Write-Host "═" * 60 -ForegroundColor Gray
Test-Endpoint "Health Check" "GET" "/health"

# Test 2: Config
Write-Host "═" * 60 -ForegroundColor Gray
Test-Endpoint "Get Configuration" "GET" "/config"

# Test 3: List Models
Write-Host "═" * 60 -ForegroundColor Gray
Test-Endpoint "List Connected Models" "GET" "/models/connected"

# Test 4: Generate Text
Write-Host "═" * 60 -ForegroundColor Gray
$generateBody = @{
    prompt = "What is AI?"
    temperature = 0.5
    max_tokens = 50
    use_rag = $false
}
Test-Endpoint "Generate Text" "POST" "/generate" $generateBody

# Test 5: Foundry Status
Write-Host "═" * 60 -ForegroundColor Gray
Test-Endpoint "Foundry Service Status" "GET" "/foundry/status"

# Test 6: List Foundry Models
Write-Host "═" * 60 -ForegroundColor Gray
Test-Endpoint "List Foundry Models" "GET" "/foundry/models/list"

Write-Host "═" * 60 -ForegroundColor Gray
Write-Host "✅ API TEST SUITE COMPLETED" -ForegroundColor Green
Write-Host ""
