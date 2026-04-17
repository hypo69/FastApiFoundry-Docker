# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Sandbox Launcher Pipeline
# =============================================================================
# Description:
#   Orchestrates the full sandbox lifecycle:
#   1. Optional preparation step (sandbox-mapper.ps1)
#   2. Project synchronization into sandbox mount directory
#   3. Launch of Windows Sandbox using predefined .wsb configuration
#
#   All paths are resolved relative to the script location to ensure
#   deterministic execution regardless of working directory.
#
# Execution model:
#   Host filesystem → sync → staging directory → mapped into Sandbox → manual runtime
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\sandbox-launcher.ps1
#
# File: sandbox-launcher.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.3.3
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param (
    # Delay between synchronization step and sandbox startup.
    # This helps avoid race conditions where filesystem changes
    # are not fully flushed before Sandbox initialization.
    [int]$DelayMs = 2000
)

# Ensures that any error immediately stops execution.
# This is important for pipeline integrity (fail-fast behavior).
$ErrorActionPreference = 'Stop'


# --- resolve base directory ---------------------------------------------------
# The script location is used as the single source of truth for all paths.
# This avoids dependency on PowerShell current working directory.

$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Optional preprocessing script.
# Intended for environment preparation (cleanup, validation, setup).
$MapperScript = Join-Path $BaseDir 'sandbox-mapper.ps1'

# Main synchronization script.
# Responsible for copying project into sandbox staging directory.
$SyncScript   = Join-Path $BaseDir 'sync-sandbox.ps1'

# Windows Sandbox configuration file.
# Defines mapped folders, networking, and startup behavior.
$WsbPath      = Join-Path $BaseDir 'sandbox.wsb'


function Invoke-SandboxScript {
    <#
    .SYNOPSIS
        Executes a sandbox-related PowerShell script in an isolated process.
    .DESCRIPTION
        Runs a script via PowerShell child process to ensure that:
        - Execution context is clean
        - Side effects do not leak into parent session
        - Script failure does not corrupt launcher state
    .PARAMETER Path
        Full path to the script being executed.
    .OUTPUTS
        bool
            True if script executed successfully, False otherwise.
    #>
    param (
        [string]$Path
    )

    # Validate existence before execution to avoid runtime failures.
    if (!(Test-Path $Path)) {
        throw "Sandbox script not found: $Path"
    }

    # Execute script in a separate PowerShell process.
    # This ensures isolation between pipeline stages.
    $result = & powershell -ExecutionPolicy Bypass -File $Path

    ...
    # Convert script output into boolean success indicator.
    # Convention: script must return truthy value on success.
    return [bool]$result
}


function Invoke-SandboxPipeline {
    <#
    .SYNOPSIS
        Executes full sandbox orchestration pipeline.
    .DESCRIPTION
        Runs steps in strict order:
        1. Optional mapper execution
        2. Mandatory project synchronization
        3. Delay to ensure filesystem stability
        4. Sandbox launch
    .OUTPUTS
        bool
            True if pipeline completed successfully.
    #>
    try {

        # --- optional preparation step --------------------------------------
        # This step may perform:
        # - environment cleanup
        # - directory validation
        # - pre-sync checks
        if (Test-Path $MapperScript) {
            Write-Host '🧱 Running sandbox mapper...'
            Invoke-SandboxScript -Path $MapperScript | Out-Null
        }

        # --- synchronization step -------------------------------------------
        # This is the core step of the pipeline:
        # - copies project into sandbox staging directory
        # - excludes heavy / runtime artifacts (venv, cache, etc.)
        Write-Host '🔄 Running sandbox sync...'
        $syncOk = Invoke-SandboxScript -Path $SyncScript

        # Fail-fast behavior:
        # If sync fails, sandbox should NOT start.
        if (-not $syncOk) {
            throw 'Sandbox sync failed'
        }

        # --- stabilization delay --------------------------------------------
        # Windows filesystem + Sandbox mount can require a short delay
        # to ensure all file operations are flushed and visible.
        Write-Host "⏳ Waiting $DelayMs ms..."
        Start-Sleep -Milliseconds $DelayMs

        # --- sandbox launch --------------------------------------------------
        # Starts Windows Sandbox using predefined .wsb configuration.
        # At this point:
        # - staging directory must be fully prepared
        # - no further modifications are expected
        Write-Host '🚀 Launching Windows Sandbox...'
        Start-Process $WsbPath

        ...
        return $true
    }
    catch {
        # Centralized error handling for entire pipeline.
        # Any failure in mapper/sync/launch will be captured here.
        Write-Host "❌ Sandbox pipeline error: $_"
        return $false
    }
}


# --- main entry point ---------------------------------------------------------

Write-Host '🔧 Sandbox pipeline started...'

# Execute full pipeline as a single atomic operation.
$result = Invoke-SandboxPipeline

if ($result) {
    Write-Host '✅ Sandbox launched successfully'
} else {
    Write-Host '❌ Sandbox launch failed'
}