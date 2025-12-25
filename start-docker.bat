@echo off
echo Docker FastAPI Foundry Launcher
echo.

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker not found! Install Docker Desktop.
    pause
    exit /b 1
)

echo Docker found
echo.

REM Check if image exists
docker images -q fastapi-foundry:0.2.1 >nul 2>&1
if %errorlevel% neq 0 (
    echo Building Docker image...
    docker build -t fastapi-foundry:0.2.1 .
    if %errorlevel% neq 0 (
        echo ERROR: Failed to build Docker image
        pause
        exit /b 1
    )
)

REM Kill process on port 8000 if exists
echo Checking port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Killing process %%a on port 8000
    taskkill /f /pid %%a >nul 2>&1
)

echo Starting FastAPI Foundry via Docker...
docker run --rm -it -v "%cd%":/app -p 8000:8000 -w /app fastapi-foundry:0.2.1 python run.py

pause