# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Inject i18next CDN Script into index.html
# =============================================================================
# Description:
#   One-time utility that inserts the i18next CDN <script> tag into
#   static/index.html, just before the closing </head> tag.
#   Run this once after a fresh checkout if the tag is missing.
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\add_i18next.ps1
#
# File: add_i18next.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

# Read the entire file as a single UTF-8 string to preserve encoding
$content = [System.IO.File]::ReadAllText('static\index.html', [System.Text.Encoding]::UTF8)

# The exact block we are looking for — the closing </head> preceded by the CSS link
$old = "    <link href=""/static/css/main.css"" rel=""stylesheet"">
</head>"

# The replacement block adds the i18next CDN script between the CSS link and </head>
$new = "    <link href=""/static/css/main.css"" rel=""stylesheet"">
    <script src=""https://cdn.jsdelivr.net/npm/i18next@23.11.5/i18next.min.js""></script>
</head>"

$content = $content.Replace($old, $new)

# Write back with UTF-8 encoding (no BOM) to avoid breaking the browser
[System.IO.File]::WriteAllText('static\index.html', $content, [System.Text.Encoding]::UTF8)

Write-Host "✅ i18next script tag injected into static\index.html" -ForegroundColor Green
