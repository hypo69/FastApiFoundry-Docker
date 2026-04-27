# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Generate PowerShell Docs
# =============================================================================
# Description:
#   Generates Markdown documentation from PowerShell comment-based help.
#   Used by GitHub Actions deploy-docs.yml workflow.
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\scripts\generate-ps-docs.ps1
#
# File: generate-ps-docs.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

$ErrorActionPreference = 'Stop'

$OUT_DIR = "docs/ru/dev/powershell"
New-Item -ItemType Directory -Force -Path $OUT_DIR | Out-Null

$files = Get-ChildItem -Path "mcp-powershell-servers/src/servers", "scripts" -Filter "*.ps1" -Recurse -ErrorAction SilentlyContinue

foreach ($file in $files) {
    try {
        $name = $file.BaseName
        $content = Get-Content $file.FullName -Raw

        $synopsis    = if ($content -match '\.SYNOPSIS\s*\r?\n\s*(.+)')                                          { $Matches[1].Trim() } else { $name }
        $description = if ($content -match '\.DESCRIPTION\s*\r?\n([\s\S]+?)(?=\r?\n\.[A-Z]|\r?\n#>)')           { $Matches[1].Trim() } else { '' }
        $notes       = if ($content -match '\.NOTES\s*\r?\n([\s\S]+?)(?=\r?\n\.[A-Z]|\r?\n#>)')                 { $Matches[1].Trim() } else { '' }

        $relativeSource = $file.FullName.Replace((Get-Location).Path + "\", "").Replace("\", "/")

        $md = "# $name`n`n$synopsis`n`n## Description`n`n$description`n"
        if ($notes) { $md += "`n## Notes`n`n$notes`n" }
        $md += "`n## Source`n`nFile: $relativeSource"

        $md | Set-Content -Path "$OUT_DIR/$name.md" -Encoding UTF8
    } catch {
        Write-Warning "Failed to process $($file.Name): $_"
    }
}

# Index page
$index = "# PowerShell MCP Servers`n`n"
foreach ($file in $files) {
    $index += "- [$($file.BaseName)]($($file.BaseName).md)`n"
}
$index | Set-Content -Path "$OUT_DIR/index.md" -Encoding UTF8

Write-Host "Done: $OUT_DIR"
