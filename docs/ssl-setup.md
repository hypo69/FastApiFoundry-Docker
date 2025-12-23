# 🔐 SSL/HTTPS Configuration Guide

**Project:** FastApiFoundry (Docker)  
**Version:** 0.2.1  
**Date:** 9 декабря 2025  

---

## 📋 SSL Certificate Management

### 🏠 Default SSL Directory
SSL certificates are stored in: `~/.ssl/`
- **Windows:** `C:\Users\{username}\.ssl\`
- **Linux/Mac:** `/home/{username}/.ssl/`

### 📁 Required Files
- `cert.pem` - SSL certificate
- `key.pem` - Private key

---

## 🚀 Quick Setup

### 1. Automatic Generation (Windows)
```powershell
# Generate SSL certificates
.\ssl-generator.ps1

# Force regenerate existing certificates
.\ssl-generator.ps1 -Force
```

### 2. Manual Generation (Linux/Mac)
```bash
# Create SSL directory
mkdir -p ~/.ssl

# Generate self-signed certificate
openssl req -x509 -newkey rsa:2048 \
  -keyout ~/.ssl/key.pem \
  -out ~/.ssl/cert.pem \
  -days 365 -nodes \
  -subj "/CN=localhost/O=FastApiFoundry/C=US"
```

---

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Enable HTTPS
HTTPS_ENABLED=true

# SSL Certificate paths
SSL_CERT_FILE=~/.ssl/cert.pem
SSL_KEY_FILE=~/.ssl/key.pem

# API Settings
API_HOST=0.0.0.0
API_PORT=8443
```

### Alternative Paths
```env
# Custom SSL directory
SSL_CERT_FILE=/path/to/custom/cert.pem
SSL_KEY_FILE=/path/to/custom/key.pem

# Relative paths (from project root)
SSL_CERT_FILE=./ssl/cert.pem
SSL_KEY_FILE=./ssl/key.pem
```

---

## 🔧 SSL Generator Features

### Certificate Details
- **Algorithm:** RSA 2048-bit
- **Hash:** SHA256
- **Validity:** 1 year
- **Subject:** CN=FastApiFoundry,O=AiStros,C=US
- **DNS Names:** localhost, 127.0.0.1, fastapi-foundry

### PowerShell Script Options
```powershell
# Basic generation
.\ssl-generator.ps1

# Force regeneration
.\ssl-generator.ps1 -Force

# Check existing certificates
.\ssl-generator.ps1 -Check
```

---

## 🚀 Starting with HTTPS

### 1. Using start-https.ps1
```powershell
.\start-https.ps1
```

### 2. Using run.py with SSL
```bash
# Set environment variables
export HTTPS_ENABLED=true
export SSL_CERT_FILE=~/.ssl/cert.pem
export SSL_KEY_FILE=~/.ssl/key.pem

# Start server
python run.py --port 8443
```

### 3. Docker with SSL
```bash
# Mount SSL directory
docker run -p 8443:8443 \
  -v ~/.ssl:/app/.ssl:ro \
  -e HTTPS_ENABLED=true \
  -e SSL_CERT_FILE=/app/.ssl/cert.pem \
  -e SSL_KEY_FILE=/app/.ssl/key.pem \
  fastapi-foundry:0.2.1
```

---

## 🔍 SSL Certificate Validation

### Automatic Checks
- **Installation:** `install.py` checks for SSL certificates
- **Startup:** `run.py` validates SSL files before starting
- **Generation:** `ssl-generator.ps1` verifies created certificates

### Manual Verification
```bash
# Check certificate details
openssl x509 -in ~/.ssl/cert.pem -text -noout

# Verify certificate and key match
openssl x509 -noout -modulus -in ~/.ssl/cert.pem | openssl md5
openssl rsa -noout -modulus -in ~/.ssl/key.pem | openssl md5
```

---

## 🌐 Accessing HTTPS Server

### URLs
- **HTTPS Web Interface:** https://localhost:8443
- **HTTPS API Docs:** https://localhost:8443/docs
- **Health Check:** https://localhost:8443/api/v1/health

### Browser Security Warning
Self-signed certificates will show security warnings:
1. Click "Advanced" or "Show Details"
2. Click "Proceed to localhost (unsafe)" or "Accept Risk"
3. Certificate will be trusted for the session

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Certificate Not Found
```
❌ SSL certificates not found in ~/.ssl
```
**Solution:** Run `.\ssl-generator.ps1` to create certificates

#### 2. Permission Denied
```
❌ Permission denied accessing SSL files
```
**Solution:** Check file permissions
```bash
chmod 600 ~/.ssl/key.pem
chmod 644 ~/.ssl/cert.pem
```

#### 3. Invalid Certificate Format
```
❌ SSL certificates are corrupted
```
**Solution:** Regenerate certificates
```powershell
.\ssl-generator.ps1 -Force
```

#### 4. Port Already in Use
```
❌ Port 8443 is already in use
```
**Solution:** Use different port or stop existing service
```bash
python run.py --port 9443
```

---

## 📚 Integration Examples

### FastAPI SSL Configuration
```python
import ssl
import uvicorn

# SSL context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(cert_file, key_file)

# Start with SSL
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8443,
    ssl_keyfile=key_file,
    ssl_certfile=cert_file
)
```

### Nginx Reverse Proxy
```nginx
server {
    listen 443 ssl;
    server_name localhost;
    
    ssl_certificate ~/.ssl/cert.pem;
    ssl_certificate_key ~/.ssl/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔒 Security Best Practices

### Certificate Management
1. **Rotate certificates** annually
2. **Use strong passwords** for production keys
3. **Restrict file permissions** (600 for keys, 644 for certs)
4. **Backup certificates** securely

### Production Considerations
1. **Use CA-signed certificates** for production
2. **Enable HSTS** headers
3. **Configure proper cipher suites**
4. **Regular security audits**

---

**Generated by FastApiFoundry (Docker) v0.2.1** 🚀