@echo off
setlocal
cd /d "%~dp0"

REM Find Python executable
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python315\python.exe"

if not exist "%PYTHON_EXE%" (
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_EXE=python"
    ) else (
        echo [ERROR] Python not found. Please install Python or check your path.
        pause
        exit /b 1
    )
)

echo ======================================================================
echo   PiClock - Lightweight Smart Display for Raspberry Pi ^& Windows 11
echo ======================================================================
echo   📱 Mobile Remote Control is enabled on Port 8080.
echo   💡 Note: If your phone cannot connect, run 'allow_firewall.bat' once
echo      as Administrator to allow Port 8080 through Windows Firewall.
echo ======================================================================
echo.
echo Starting PiClock on Windows 11...
"%PYTHON_EXE%" main.py %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo PiClock exited with error code %ERRORLEVEL%.
    pause
)
