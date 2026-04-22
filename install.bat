@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
set "PY_ZIP=%ROOT%\bin\Python-3.11.9.zip"
set "PY_DIR=%ROOT%\bin\Python-3.11.9"
set "PYTHON=%PY_DIR%\Python-3.11.9\python.exe"
set "VENV_PY=%ROOT%\venv\Scripts\python.exe"
set "VENV_PIP=%ROOT%\venv\Scripts\pip.exe"

if exist "%PYTHON%" goto :venv

if not exist "%PY_ZIP%" (
    echo [ERROR] bin\Python-3.11.9.zip not found.
    pause
    exit /b 1
)

echo [install] Extracting Python...
powershell -NoProfile -Command "Expand-Archive -Path '%PY_ZIP%' -DestinationPath '%PY_DIR%' -Force"
if errorlevel 1 ( echo [ERROR] Extraction failed. & pause & exit /b 1 )

:venv
if exist "%VENV_PY%" goto :pip
echo [install] Creating venv...
"%PYTHON%" -m venv "%ROOT%\venv"
if errorlevel 1 ( echo [ERROR] venv failed. & pause & exit /b 1 )

:pip
echo [install] Installing base packages...
"%VENV_PIP%" install --quiet fastapi uvicorn python-dotenv psutil
if errorlevel 1 ( echo [ERROR] pip failed. & pause & exit /b 1 )

:run
echo.
echo Opening installer at http://localhost:9698
echo.
"%VENV_PY%" "%ROOT%\install\server.py"

echo.
echo Done. Run start.ps1 to launch FastAPI Foundry.
echo.
pause
endlocal
