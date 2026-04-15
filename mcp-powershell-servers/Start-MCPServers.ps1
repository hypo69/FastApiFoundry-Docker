## \file Start-MCPServers.ps1
# -*- coding: utf-8 -*-
#! .pyenv/bin/pwsh

<#
.SYNOPSIS
    Start-MCPServers для MCP PowerShell серверов
    
.DESCRIPTION
    Start-MCPServers автоматически запускает все MCP серверы в фоновых процессах.
    
.PARAMETER StopServers
    Остановить все запущенные MCP серверы
    
.PARAMETER ConfigPath
    Путь к директории с конфигурациями (по умолчанию: src/config)
    
.PARAMETER Force
    Принудительный запуск, игнорируя PID файл
    
.EXAMPLE
    .\Start-MCPServers.ps1
    
.EXAMPLE
    .\Start-MCPServers.ps1 -StopServers

.EXAMPLE
    .\Start-MCPServers.ps1 -Force

.NOTES
    Version: 1.1.2
    Author: hypo69
    License: MIT (https://opensource.org/licenses/MIT)
    Copyright: @hypo69 - 2025
#>

#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$StopServers,
    
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = 'src\config',
    
    [Parameter(Mandatory = $false)]
    [switch]$Force,
    
    [Parameter(Mandatory = $false)]
    [switch]$Help
)

#region Global Variables

$script:LauncherVersion = '1.1.2'
$script:ServerProcesses = @{}
$script:LogFile = Join-Path $env:TEMP 'mcp-launcher.log'
$script:PidFile = Join-Path $env:TEMP 'mcp-servers.pid'

#endregion

#region Utility Functions

function Write-Log {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter(Mandatory = $false)]
        [ValidateSet('DEBUG', 'INFO', 'WARNING', 'ERROR', 'SUCCESS')]
        [string]$Level = 'INFO'
    )
    
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logMessage = "[$timestamp] [$Level] $Message"
    
    Add-Content -Path $script:LogFile -Value $logMessage -Encoding UTF8 -ErrorAction SilentlyContinue
    
    $color = switch ($Level) {
        'SUCCESS' { 'Green' }
        'WARNING' { 'Yellow' }
        'ERROR'   { 'Red' }
        'INFO'    { 'Cyan' }
        'DEBUG'   { 'Gray' }
        default   { 'White' }
    }
    
    $prefix = switch ($Level) {
        'SUCCESS' { '[✓]' }
        'WARNING' { '[!]' }
        'ERROR'   { '[✗]' }
        'INFO'    { '[i]' }
        'DEBUG'   { '[d]' }
        default   { '[-]' }
    }
    
    Write-Host "$prefix $Message" -ForegroundColor $color
}

function Save-ServerPIDs {
    try {
        $processData = @{}
        foreach ($serverName in $script:ServerProcesses.Keys) {
            $process = $script:ServerProcesses[$serverName]
            if ($process -and -not $process.HasExited) {
                $processData[$serverName] = $process.Id
            }
        }
        
        if ($processData.Count -gt 0) {
            $processData | ConvertTo-Json | Set-Content -Path $script:PidFile -Encoding UTF8 -ErrorAction Stop
            Write-Log "Информация о процессах сохранена в файл: $script:PidFile" -Level 'DEBUG'
        } else {
            Write-Log "Нет активных процессов для сохранения" -Level 'DEBUG'
            Remove-PidFile
        }
    }
    catch {
        Write-Log "Ошибка сохранения информации о процессах: $($_.Exception.Message)" -Level 'WARNING'
    }
}

function Load-ServerPIDs {
    try {
        if (-not (Test-Path $script:PidFile)) {
            Write-Log "Файл PID не найден, процессы не загружены" -Level 'DEBUG'
            return
        }
        
        $processData = Get-Content -Path $script:PidFile -Raw -ErrorAction Stop | ConvertFrom-Json
        $loadedCount = 0
        $deadCount = 0
        
        foreach ($property in $processData.PSObject.Properties) {
            $serverName = $property.Name
            $processId = $property.Value
            
            try {
                # Проверка существования процесса
                $process = Get-Process -Id $processId -ErrorAction Stop
                
                # Двойная проверка - процесс найден и не завершился
                if (-not $process.HasExited) {
                    $script:ServerProcesses[$serverName] = $process
                    Write-Log "Загружен процесс для $serverName : PID $processId" -Level 'DEBUG'
                    $loadedCount++
                } else {
                    Write-Log "Процесс $serverName (PID: $processId) завершен" -Level 'DEBUG'
                    $deadCount++
                }
            }
            catch {
                # Процесс не найден - это нормально, если был убит вручную
                Write-Log "Процесс $serverName (PID: $processId) не найден (был убит вручную)" -Level 'DEBUG'
                $deadCount++
            }
        }
        
        Write-Log "Загружено процессов: $loadedCount, мертвых: $deadCount" -Level 'INFO'
        
        # Если все процессы мертвые - очищаем файл PID
        if ($loadedCount -eq 0 -and $deadCount -gt 0) {
            Write-Log "Все сохраненные процессы мертвые, очистка PID файла" -Level 'WARNING'
            Remove-PidFile
            $script:ServerProcesses = @{}
        }
    }
    catch {
        Write-Log "Ошибка загрузки информации о процессах: $($_.Exception.Message)" -Level 'DEBUG'
        Remove-PidFile
    }
}

function Remove-PidFile {
    try {
        if (Test-Path $script:PidFile) {
            Remove-Item $script:PidFile -Force -ErrorAction Stop
            Write-Log "Файл PID удален" -Level 'DEBUG'
        }
    }
    catch {
        Write-Log "Ошибка удаления файла PID: $($_.Exception.Message)" -Level 'WARNING'
    }
}

function Show-Help {
    $helpText = @"

MCP PowerShell Server Launcher v$script:LauncherVersion

ОПИСАНИЕ:
    Автоматический запуск всех MCP PowerShell серверов.

ИСПОЛЬЗОВАНИЕ:
    .\Start-MCPServers.ps1 [параметры]

ПАРАМЕТРЫ:
    -StopServers            Остановить все запущенные MCP серверы
    -ConfigPath <путь>      Путь к директории с конфигурациями
    -Force                  Принудительный запуск (игнорировать PID файл)
    -Help                   Показать эту справку

ПРИМЕРЫ:
    .\Start-MCPServers.ps1
    .\Start-MCPServers.ps1 -StopServers
    .\Start-MCPServers.ps1 -Force

ЗАПУСКАЕМЫЕ СЕРВЕРЫ:
    - powershell-stdio
    - powershell-https
    - wordpress-cli
    - wordpress-mcp
    - huggingface-mcp

АВТОР:
    hypo69

ЛИЦЕНЗИЯ:
    MIT (https://opensource.org/licenses/MIT)

"@
    Write-Host $helpText -ForegroundColor Cyan
}

function Find-ServerScript {
    param([string]$ServerName)
    $possiblePaths = @(
        "src\servers\$ServerName.ps1",
        "servers\$ServerName.ps1",
        "$ServerName.ps1",
        $ServerName
    )
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            return (Resolve-Path $path).Path
        }
    }
    Write-Log "Файл $ServerName не найден" -Level 'DEBUG'
    return $null
}

function Test-ServerRunning {
    param([string]$ServerName)
    
    if (-not $script:ServerProcesses.ContainsKey($ServerName)) {
        return $false
    }
    
    $p = $script:ServerProcesses[$ServerName]
    
    # Проверка: объект существует, это процесс, и он не завершился
    if ($p -and $p -is [System.Diagnostics.Process]) {
        try {
            # Попытка обновить информацию о процессе
            $p.Refresh()
            
            if (-not $p.HasExited) {
                return $true
            } else {
                Write-Log "Процесс $ServerName завершен" -Level 'DEBUG'
                $script:ServerProcesses.Remove($ServerName)
                return $false
            }
        }
        catch {
            # Процесс больше не существует
            Write-Log "Процесс $ServerName не существует: $($_.Exception.Message)" -Level 'DEBUG'
            $script:ServerProcesses.Remove($ServerName)
            return $false
        }
    }
    
    return $false
}

function Start-MCPServer {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ServerName,
        [Parameter(Mandatory = $true)]
        [string]$ScriptPath,
        [Parameter(Mandatory = $false)]
        [hashtable]$Environment = @{}
    )
    Write-Log "Запуск сервера: $ServerName" -Level 'INFO'
    if (-not (Test-Path $ScriptPath)) {
        Write-Log "ОШИБКА: файл не найден: $ScriptPath" -Level 'ERROR'
        return $false
    }
    if (Test-ServerRunning -ServerName $ServerName) {
        Write-Log "Сервер $ServerName уже запущен" -Level 'WARNING'
        return $true
    }
    try {
        $si = [System.Diagnostics.ProcessStartInfo]::new()
        $si.FileName = 'pwsh'
        $si.Arguments = "-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$ScriptPath`""
        $si.UseShellExecute = $false
        $si.RedirectStandardOutput = $true
        $si.RedirectStandardError  = $true
        $si.CreateNoWindow = $true
        foreach ($k in $Environment.Keys) { $si.EnvironmentVariables[$k] = $Environment[$k] }
        $p = [System.Diagnostics.Process]::new()
        $p.StartInfo = $si
        if (-not $p.Start()) { Write-Log "Не удалось запустить процесс $ServerName" -Level 'ERROR'; return $false }
        Start-Sleep -Milliseconds 800
        if ($p.HasExited) {
            $err = $p.StandardError.ReadToEnd()
            Write-Log "Ошибка запуска ${ServerName}: $err" -Level 'ERROR'
            return $false
        }
        $script:ServerProcesses[$ServerName] = $p
        Write-Log "Сервер $ServerName запущен (PID: $($p.Id))" -Level 'SUCCESS'
        Save-ServerPIDs
        return $true
    } catch {
        Write-Log "Ошибка запуска сервера ${ServerName}: $($_.Exception.Message)" -Level 'ERROR'
        return $false
    }
}

function Stop-MCPServers {
    param([switch]$Force)
    Write-Log 'Остановка всех MCP серверов...' -Level 'INFO'
    Load-ServerPIDs
    $stopped = 0
    foreach ($s in $script:ServerProcesses.Keys) {
        $p = $script:ServerProcesses[$s]
        if ($p -and -not $p.HasExited) {
            try {
                Stop-Process -Id $p.Id -Force -ErrorAction Stop
                Write-Log "$s остановлен" -Level 'SUCCESS'
                $stopped++
            } catch {
                Write-Log "Ошибка остановки ${s}: $($_.Exception.Message)" -Level 'ERROR'
            }
        }
    }
    Remove-PidFile
    Write-Log "Остановлено серверов: $stopped" -Level 'INFO'
}

function Show-ServerStatus {
    Write-Host ''
    Write-Host '=== СТАТУС MCP СЕРВЕРОВ ===' -ForegroundColor Cyan
    
    if ($script:ServerProcesses.Count -eq 0) {
        Write-Host '  (нет запущенных серверов)' -ForegroundColor Gray
        return
    }
    
    $running = 0
    $dead = 0
    
    foreach ($s in $script:ServerProcesses.Keys) {
        if (Test-ServerRunning -ServerName $s) {
            $p = $script:ServerProcesses[$s]
            Write-Host "  ✓ $s (PID: $($p.Id))" -ForegroundColor Green
            $running++
        } else {
            Write-Host "  ✗ $s (остановлен)" -ForegroundColor Red
            $dead++
        }
    }
    
    Write-Host "Запущено серверов: $running / $($script:ServerProcesses.Count)" -ForegroundColor Yellow
    
    # Если все серверы мертвые - очистить
    if ($running -eq 0 -and $dead -gt 0) {
        Write-Log "Все серверы мертвые, очистка данных" -Level 'WARNING'
        $script:ServerProcesses = @{}
        Remove-PidFile
    }
}

#endregion

#region Main Logic

function Start-AllServers {
    Write-Host ''
    Write-Host "=== MCP PowerShell Server Launcher v$script:LauncherVersion ===" -ForegroundColor Cyan
    $servers = @{
        'powershell-stdio'  = @{ Script='McpStdioServer';       Description='STDIO сервер PowerShell' }
        'powershell-https'  = @{ Script='McpHttpsServer';       Description='HTTPS сервер REST API' }
        'wordpress-cli'     = @{ Script='McpWpCliServer';       Description='WordPress CLI сервер' }
        'wordpress-mcp'     = @{ Script='McpWpServer';          Description='WordPress MCP сервер (REST + HuggingFace)' }
        'huggingface-mcp'   = @{ Script='McpHuggingFaceServer'; Description='Hugging Face MCP сервер' }
    }
    $found=@{}
    foreach ($s in $servers.Keys) {
        $path = Find-ServerScript $servers[$s].Script
        if ($path) { $found[$s]=$path }
    }
    if ($found.Count -eq 0) { Write-Log "Не найдено ни одного серверного скрипта" -Level 'ERROR'; return $false }
    foreach ($s in $found.Keys) {
        Write-Log "Запуск $s ($($servers[$s].Description))" -Level 'INFO'
        $env=@{POWERSHELL_EXECUTION_POLICY='RemoteSigned';HF_TOKEN=$env:HF_TOKEN;WP_PATH='C:\xampp\htdocs\wordpress'}
        Start-MCPServer -ServerName $s -ScriptPath $found[$s] -Environment $env | Out-Null
        Start-Sleep -Milliseconds 300
    }
    Show-ServerStatus
    return $true
}

#endregion

#region Entry Point

try {
    if ($Help) { Show-Help; exit 0 }
    if ($StopServers) { Stop-MCPServers; exit 0 }

    # Если -Force, то удаляем PID файл и начинаем с чистого листа
    if ($Force) {
        Write-Log "Режим Force: игнорирование PID файла" -Level 'WARNING'
        Remove-PidFile
        $script:ServerProcesses = @{}
    } else {
        # Загружаем сохраненные PID
        Load-ServerPIDs
    }
    
    # Проверяем, есть ли живые серверы
    $aliveCount = 0
    foreach ($serverName in @($script:ServerProcesses.Keys)) {
        if (Test-ServerRunning -ServerName $serverName) {
            $aliveCount++
        }
    }
    
    if ($aliveCount -gt 0) {
        Write-Log "Обнаружено $aliveCount запущенных серверов" -Level 'WARNING'
        Show-ServerStatus
        Write-Host ""
        Write-Host "Для перезапуска используйте: .\Start-MCPServers.ps1 -Force" -ForegroundColor Yellow
        Write-Host "Для остановки используйте: .\Start-MCPServers.ps1 -StopServers" -ForegroundColor Yellow
        exit 1
    }

    # Все процессы мертвые или их нет - запускаем
    if (-not (Start-AllServers)) { exit 1 }

    Write-Host "=== СЕРВЕРЫ УСПЕШНО ЗАПУЩЕНЫ ===" -ForegroundColor Green
    Write-Host "Для остановки: .\Start-MCPServers.ps1 -StopServers" -ForegroundColor Yellow

    $null = Register-EngineEvent -SourceIdentifier Console.CancelKeyPress -Action {
        Write-Host "`nСохранение PID..." -ForegroundColor Yellow
        Save-ServerPIDs
        Write-Host "Информация сохранена. Серверы продолжают работу." -ForegroundColor Green
        [Environment]::Exit(0)
    }

    while ($true) {
        Start-Sleep -Seconds 5
        
        # Проверка живых серверов
        $alive = 0
        foreach ($serverName in @($script:ServerProcesses.Keys)) {
            if (Test-ServerRunning -ServerName $serverName) {
                $alive++
            }
        }
        
        if ($alive -eq 0) { 
            Write-Log "Все серверы завершены" -Level 'WARNING'
            Remove-PidFile
            break 
        }
    }
}
catch {
    Write-Log "Критическая ошибка: $($_.Exception.Message)" -Level 'ERROR'
    Stop-MCPServers
}
finally {
    Write-Log 'Launcher завершен' -Level 'INFO'
}
#endregion