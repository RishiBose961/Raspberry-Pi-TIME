@echo off
setlocal
title PiClock - Allow Firewall Port 8080 & Python
echo ======================================================================
echo   PiClock - Windows Defender Firewall Configuration
echo ======================================================================
echo.
echo Opening Inbound TCP Port 8080 so your smartphone/tablet on the same
echo Wi-Fi can connect to the PiClock Remote Control and Clock Display.
echo.

set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python315\python.exe"

REM Check for administrative privileges
net session >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Running with Administrator privileges.
    goto :ADD_RULE
) else (
    echo [INFO] Requesting Administrator elevation to update Windows Firewall...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c netsh advfirewall firewall delete rule name=\"PiClock Remote (Port 8080)\" & netsh advfirewall firewall add rule name=\"PiClock Remote (Port 8080)\" dir=in action=allow protocol=TCP localport=8080 & netsh advfirewall firewall delete rule name=\"PiClock Python\" & if exist \"%PY_EXE%\" (netsh advfirewall firewall add rule name=\"PiClock Python\" dir=in action=allow program=\"%PY_EXE%\" enable=yes) & echo. & echo [SUCCESS] Port 8080 and Python are now ALLOWED through Windows Firewall! & echo Your phone can now connect freely. & echo Press any key to exit. & pause' -Verb RunAs"
    if %ERRORLEVEL% EQU 0 (
        echo [DONE] Elevated setup launched. Please click 'Yes' on the Windows prompt.
    ) else (
        echo [ERROR] Could not request Administrator privileges.
    )
    goto :END
)

:ADD_RULE
netsh advfirewall firewall delete rule name="PiClock Remote (Port 8080)" >nul 2>&1
netsh advfirewall firewall add rule name="PiClock Remote (Port 8080)" dir=in action=allow protocol=TCP localport=8080
if exist "%PY_EXE%" (
    netsh advfirewall firewall delete rule name="PiClock Python" >nul 2>&1
    netsh advfirewall firewall add rule name="PiClock Python" dir=in action=allow program="%PY_EXE%" enable=yes
)

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Windows Firewall rules added:
    echo   - Inbound TCP Port 8080: ALLOWED
    echo   - Python executable: ALLOWED
    echo Your phone on the same Wi-Fi can now open: http://%~1:8080
) else (
    echo [ERROR] Failed to add firewall rule. Error code: %ERRORLEVEL%
)

:END
echo.
pause

