@echo off
echo ====================================================================
echo  Installing 24/7 Background Windows Task for Telegram Trade Tracker
echo ====================================================================

set TASK_NAME=DhanTelegramTradeTracker
set PYTHON_EXE=python
set SCRIPT_PATH=d:\Monkeycode\github\run_daemon.py

echo Creating scheduled task '%TASK_NAME%' to run on system startup...

schtasks /create /tn "%TASK_NAME%" /tr "%PYTHON_EXE% %SCRIPT_PATH%" /sc ONSTART /ru SYSTEM /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Task '%TASK_NAME%' registered successfully!
    echo    It will run continuously in the background 24/7 on system startup.
) else (
    echo.
    echo ℹ️ Trying user-level task registration...
    schtasks /create /tn "%TASK_NAME%" /tr "%PYTHON_EXE% %SCRIPT_PATH%" /sc ONCE /st 00:00 /ri 1 /du 9999:59 /f
)

echo.
echo Starting task '%TASK_NAME%' now...
schtasks /run /tn "%TASK_NAME%"

echo.
echo Done! Check d:\Monkeycode\github\daemon_execution.log for live logs.
pause
