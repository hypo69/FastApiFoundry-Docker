# -*- coding: utf-8 -*-
# =============================================================================
# Process name: EXE Wrapper Generator
# =============================================================================
# Description:
#   Compiles tiny C# wrappers into EXE files that launch PowerShell scripts.
#   This allows users to double-click an EXE instead of running PS1.
#   Uses the built-in Windows CSC (C# Compiler).
# =============================================================================

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
if ($Root -match 'scripts$') { $Root = Split-Path $Root -Parent }

# Find CSC.exe (Standard path in Windows)
$csc = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (-not (Test-Path $csc)) {
    $csc = "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"
}

if (-not (Test-Path $csc)) {
    Write-Host "❌ C# Compiler (csc.exe) not found. Cannot build EXE wrappers." -ForegroundColor Red
    exit 1
}

function Build-Wrapper([string]$name, [string]$scriptName, [string]$iconPath) {
    Write-Host "Building $name.exe..." -ForegroundColor Yellow
    
    $source = @"
using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;

class Program {
    static void Main(string[] args) {
        string root = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
        string psScript = Path.Combine(root, "$scriptName");
        
        if (!File.Exists(psScript)) {
            Console.WriteLine("Error: " + psScript + " not found.");
            Console.ReadLine();
            return;
        }

        ProcessStartInfo psi = new ProcessStartInfo();
        psi.FileName = "powershell.exe";
        // -ExecutionPolicy Bypass allows running the script even if system policy is restricted
        psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -File \"" + psScript + "\"";
        psi.UseShellExecute = false;
        // For install.exe we want to see the console, for others maybe not.
        // But for installer, visibility is good.
        
        Process.Start(psi);
    }
}
"@
    $sourcePath = Join-Path $Root "$name.cs"
    $outputPath = Join-Path $Root "$name.exe"
    
    $source | Out-File -FilePath $sourcePath -Encoding UTF8
    
    $cmdArgs = @("/out:$outputPath", "/target:exe", $sourcePath)
    if ($iconPath -and (Test-Path $iconPath)) {
        $cmdArgs += "/win32icon:$iconPath"
    }

    & $csc $cmdArgs | Out-Null
    
    if (Test-Path $outputPath) {
        Write-Host "✅ Created $outputPath" -ForegroundColor Green
        Remove-Item $sourcePath
    } else {
        Write-Host "❌ Failed to create $name.exe" -ForegroundColor Red
    }
}

# --- Build the wrappers ---

# 1. install.exe
Build-Wrapper -name "install" -scriptName "install.ps1"

# 2. launcher.exe (optional, for starting the app)
Build-Wrapper -name "launcher" -scriptName "launcher.ps1"

Write-Host "`nDone! You now have EXE files in the root directory." -ForegroundColor Cyan
