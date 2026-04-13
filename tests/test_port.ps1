function Get-FoundryPort {
    try {
        $foundryProcess = Get-Process | Where-Object { $_.ProcessName -like "Inference.Service.Agent*" }
        if (-not $foundryProcess) {
            Write-Host "No Foundry process found" -ForegroundColor Gray
            return $null
        }
        
        Write-Host "Found Foundry process: $($foundryProcess.ProcessName) (PID: $($foundryProcess.Id))" -ForegroundColor Green
        
        $netstatOutput = netstat -ano | Select-String "$($foundryProcess.Id)" | Select-String "LISTENING"
        
        foreach ($line in $netstatOutput) {
            if ($line -match ':(\d+)\s') {
                $port = $matches[1]
                Write-Host "Testing port: $port" -ForegroundColor Cyan
                
                try {
                    $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/v1/models" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
                    if ($response.StatusCode -eq 200) {
                        Write-Host "SUCCESS: Foundry API confirmed on port $port" -ForegroundColor Green
                        return $port
                    }
                } catch {
                    Write-Host "Port $port not responding" -ForegroundColor Yellow
                }
            }
        }
        
        Write-Host "Foundry process found but no working API port detected" -ForegroundColor Yellow
    } catch {
        Write-Host "Error searching for Foundry: $_" -ForegroundColor Red
    }
    return $null
}

$port = Get-FoundryPort
if ($port) {
    $env:FOUNDRY_BASE_URL = "http://localhost:$port/v1/"
    Write-Host "FOUNDRY_BASE_URL = $env:FOUNDRY_BASE_URL" -ForegroundColor Green
} else {
    Write-Host "Foundry not found" -ForegroundColor Red
}