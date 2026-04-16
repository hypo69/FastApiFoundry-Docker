# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Windows Sandbox Setup and Launch
# =============================================================================
# Description:
#   Checks hardware virtualization, enables required Windows features
#   (Hyper-V, VirtualMachinePlatform, Containers-DisposableClientVM),
#   generates a .wsb config file and launches Windows Sandbox with the
#   project folder mapped from the host.
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\run-sandbox.ps1
#   powershell -ExecutionPolicy Bypass -File .\run-sandbox.ps1 -Silent
#
# File: run-sandbox.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param (
    [switch]$Silent
)

$ErrorActionPreference = 'Stop'

# Path to the project on the host machine
$PROJECT_PATH = 'D:\repos\public_repositories\FastApiFoundry-Docker'

# Path to the project inside the sandbox
$SANDBOX_PATH = 'C:\Users\WDAGUtilityAccount\Desktop\FastApiFoundry-Docker'

# Temporary .wsb configuration file path
$WSB_FILE = Join-Path $env:TEMP 'sandbox_auto.wsb'


function Test-Virtualization {
    <#
    .SYNOPSIS
        Checks whether hardware virtualization is enabled in firmware.
    .OUTPUTS
        bool — True if virtualization is enabled, False otherwise.
    #>
    $sysinfo = systeminfo
    return ($sysinfo -match 'Virtualization Enabled In Firmware:\s+Yes')
}


function Enable-Feature {
    <#
    .SYNOPSIS
        Enables a Windows optional feature if not already enabled.
    .PARAMETER name
        Name of the Windows optional feature.
    .OUTPUTS
        bool — True if the feature was just enabled, False if already active.
    #>
    param ([string]$name)

    $feature = Get-WindowsOptionalFeature -Online -FeatureName $name

    if ($feature.State -ne 'Enabled') {
        Write-Host "➡️ Включается $name ..."
        Enable-WindowsOptionalFeature -Online -FeatureName $name -All -NoRestart
        return $true
    }

    return $false
}


function Ensure-Sandbox {
    <#
    .SYNOPSIS
        Verifies and enables Windows Sandbox and its required dependencies.
    .OUTPUTS
        bool — True if a system reboot is required, False otherwise.
    .NOTES
        Throws if hardware virtualization is disabled in BIOS.
    #>
    $rebootRequired = $false

    if (-not (Test-Virtualization)) {
        throw 'Виртуализация отключена в BIOS'
    }

    $features = @(
        'Microsoft-Hyper-V',
        'VirtualMachinePlatform',
        'Containers-DisposableClientVM'
    )

    foreach ($f in $features) {
        if (Enable-Feature -name $f) {
            $rebootRequired = $true
        }
    }

    # Set hypervisor to launch automatically on boot
    bcdedit /set hypervisorlaunchtype Auto | Out-Null

    return $rebootRequired
}


function New-WSBConfig {
    <#
    .SYNOPSIS
        Generates the Windows Sandbox configuration (.wsb) file.
    .PARAMETER silent
        When set, runs autostart.ps1 hidden; otherwise opens interactive start.ps1.
    #>
    param ([bool]$silent)

    if ($silent) {
        $command = "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command `"cd '$SANDBOX_PATH'; ./autostart.ps1`""
    }
    else {
        $command = "powershell.exe -NoExit -ExecutionPolicy Bypass -Command `"cd '$SANDBOX_PATH'; ./start.ps1`""
    }

    $content = @"
<Configuration>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>$PROJECT_PATH</HostFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>

  <LogonCommand>
    <Command>$command</Command>
  </LogonCommand>

  <Networking>Enable</Networking>
  <ClipboardRedirection>Enable</ClipboardRedirection>
</Configuration>
"@

    $content | Set-Content -Path $WSB_FILE -Encoding UTF8
}


function Start-Sandbox {
    <#
    .SYNOPSIS
        Launches Windows Sandbox using the generated .wsb config file.
    #>
    Write-Host '🚀 Запуск Windows Sandbox ...'
    Start-Process $WSB_FILE
}


# --- main ---

Write-Host '🔍 Проверка окружения...'

$needsReboot = Ensure-Sandbox

if ($needsReboot) {
    Write-Host '⚠️ Требуется перезагрузка для завершения установки.'
    Write-Host 'Повтори запуск скрипта после рестарта.'
    Restart-Computer
    return
}

Write-Host '⚙️ Генерация конфигурации sandbox...'
New-WSBConfig -silent:$Silent

Start-Sandbox
