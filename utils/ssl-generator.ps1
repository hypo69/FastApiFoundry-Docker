# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Генерация SSL сертификатов для FastApiFoundry (Docker)
# =============================================================================
# Описание:
#   PowerShell скрипт для создания самоподписанных SSL сертификатов
#   Создает сертификаты в директории ~/.ssl для HTTPS поддержки
#
# Примеры:
#   .\ssl-generator.ps1
#   .\ssl-generator.ps1 -Force
#
# File: ssl-generator.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

# Установка политики выполнения для текущего пользователя
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

param(
    [switch]$Force = $false
)

# Функция для создания SSL сертификатов
function New-SSLCertificates {
    param(
        [string]$SSLDir,
        [bool]$ForceCreate = $false
    )
    
    Write-Host "🔐 SSL Certificate Generator for FastApiFoundry" -ForegroundColor Cyan
    Write-Host "=" * 60
    
    # Проверка существующих сертификатов
    $certFile = Join-Path $SSLDir "cert.pem"
    $keyFile = Join-Path $SSLDir "key.pem"
    
    if ((Test-Path $certFile) -and (Test-Path $keyFile) -and !$ForceCreate) {
        Write-Host "✅ SSL certificates already exist:" -ForegroundColor Green
        Write-Host "   Certificate: $certFile"
        Write-Host "   Private Key: $keyFile"
        return $true
    }
    
    # Создание директории
    if (!(Test-Path $SSLDir)) {
        New-Item -ItemType Directory -Path $SSLDir -Force | Out-Null
        Write-Host "📁 Created SSL directory: $SSLDir" -ForegroundColor Yellow
    }
    
    try {
        Write-Host "🔧 Generating SSL certificate..." -ForegroundColor Yellow
        
        # Создание самоподписанного сертификата
        $cert = New-SelfSignedCertificate `
            -DnsName "localhost", "127.0.0.1", "fastapi-foundry" `
            -CertStoreLocation "cert:\CurrentUser\My" `
            -KeyAlgorithm RSA `
            -KeyLength 2048 `
            -HashAlgorithm SHA256 `
            -NotAfter (Get-Date).AddYears(1) `
            -Subject "CN=FastApiFoundry,O=AiStros,C=US"
        
        # Экспорт сертификата в PEM формат
        $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
        $certPem = "-----BEGIN CERTIFICATE-----`n"
        $certPem += [System.Convert]::ToBase64String($certBytes, [System.Base64FormattingOptions]::InsertLineBreaks)
        $certPem += "`n-----END CERTIFICATE-----"
        
        # Сохранение сертификата
        $certPem | Out-File -FilePath $certFile -Encoding ASCII
        
        # Экспорт приватного ключа
        $keyBytes = $cert.PrivateKey.ExportPkcs8PrivateKey()
        $keyPem = "-----BEGIN PRIVATE KEY-----`n"
        $keyPem += [System.Convert]::ToBase64String($keyBytes, [System.Base64FormattingOptions]::InsertLineBreaks)
        $keyPem += "`n-----END PRIVATE KEY-----"
        
        # Сохранение приватного ключа
        $keyPem | Out-File -FilePath $keyFile -Encoding ASCII
        
        # Удаление сертификата из хранилища
        Remove-Item "cert:\CurrentUser\My\$($cert.Thumbprint)" -Force
        
        Write-Host "✅ SSL certificates generated successfully!" -ForegroundColor Green
        Write-Host "   Certificate: $certFile"
        Write-Host "   Private Key: $keyFile"
        Write-Host ""
        Write-Host "🔒 Certificate Details:" -ForegroundColor Cyan
        Write-Host "   Subject: $($cert.Subject)"
        Write-Host "   Valid Until: $($cert.NotAfter.ToString('yyyy-MM-dd HH:mm:ss'))"
        Write-Host "   Thumbprint: $($cert.Thumbprint)"
        
        return $true
        
    } catch {
        Write-Host "❌ Failed to generate SSL certificates: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Функция проверки SSL сертификатов
function Test-SSLCertificates {
    param([string]$SSLDir)
    
    $certFile = Join-Path $SSLDir "cert.pem"
    $keyFile = Join-Path $SSLDir "key.pem"
    
    if ((Test-Path $certFile) -and (Test-Path $keyFile)) {
        try {
            # Проверка валидности сертификата
            $certContent = Get-Content $certFile -Raw
            if ($certContent -match "-----BEGIN CERTIFICATE-----" -and $certContent -match "-----END CERTIFICATE-----") {
                Write-Host "✅ SSL certificates are valid" -ForegroundColor Green
                return $true
            }
        } catch {
            Write-Host "❌ SSL certificates are corrupted" -ForegroundColor Red
        }
    }
    
    Write-Host "❌ SSL certificates not found or invalid" -ForegroundColor Red
    return $false
}

# Основная логика
$SSLDir = Join-Path $env:USERPROFILE ".ssl"

Write-Host "🔍 Checking SSL certificates in: $SSLDir" -ForegroundColor Cyan

if (Test-SSLCertificates -SSLDir $SSLDir) {
    if ($Force) {
        Write-Host "🔄 Force regenerating certificates..." -ForegroundColor Yellow
        New-SSLCertificates -SSLDir $SSLDir -ForceCreate $true
    } else {
        Write-Host "✅ SSL certificates already exist and are valid" -ForegroundColor Green
    }
} else {
    Write-Host "🔧 SSL certificates not found. Generating new ones..." -ForegroundColor Yellow
    New-SSLCertificates -SSLDir $SSLDir -ForceCreate $false
}

Write-Host ""
Write-Host "📋 Usage in FastApiFoundry:" -ForegroundColor Cyan
Write-Host "   Set SSL_CERT_FILE=$SSLDir\cert.pem"
Write-Host "   Set SSL_KEY_FILE=$SSLDir\key.pem"
Write-Host "   Set HTTPS_ENABLED=true"
Write-Host ""
Write-Host "🚀 Start with HTTPS: .\start-https.ps1" -ForegroundColor Green