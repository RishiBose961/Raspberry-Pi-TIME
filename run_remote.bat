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
        echo [ERROR] Python not found. Please install Python or check your PATH.
        pause
        exit /b 1
    )
)

echo ======================================================================
echo   Starting PiClock Web Remote Control Server...
echo ======================================================================
echo.

"%PYTHON_EXE%" server.py %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server exited with error code %ERRORLEVEL%.
    pause
)
