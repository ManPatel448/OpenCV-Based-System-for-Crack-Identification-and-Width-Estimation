@echo off
setlocal EnableExtensions

cd /d "%~dp0"
set "APP_URL=http://127.0.0.1:5000"
set "PYTHON_EXE=.venv\Scripts\python.exe"

echo ===================================================================
echo  OpenCV-Based-System-for-Crack-Identification-and-Width-Estimation
echo ===================================================================

if not exist "%PYTHON_EXE%" (
    echo Creating the virtual environment...
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -m venv .venv
    ) else (
        where python >nul 2>&1
        if errorlevel 1 (
            echo Python was not found. Install Python 3.10 or newer and try again.
            pause
            exit /b 1
        )
        python -m venv .venv
    )
    if errorlevel 1 (
        echo Could not create the virtual environment.
        pause
        exit /b 1
    )
)

if not exist ".env" (
    echo Creating .env from .env.example...
    copy /Y ".env.example" ".env" >nul
)

echo Installing or updating dependencies...
"%PYTHON_EXE%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

echo Checking whether Flask is already running...
curl.exe --silent --show-error --fail --max-time 2 "%APP_URL%/" >nul 2>&1
if not errorlevel 1 goto open_browser

echo Starting Flask...
start "Crack Detaction Flask Server" /min "%CD%\%PYTHON_EXE%" "%CD%\app.py"

echo Waiting for the web server...
set /a ATTEMPTS=0
:wait_for_server
set /a ATTEMPTS+=1
curl.exe --silent --show-error --fail --max-time 2 "%APP_URL%/" >nul 2>&1
if not errorlevel 1 goto open_browser
if %ATTEMPTS% GEQ 30 (
    echo The Flask server did not respond within 30 seconds.
    echo Check the "Crack Detaction Flask Server" window for the error.
    pause
    exit /b 1
)
powershell.exe -NoProfile -Command "Start-Sleep -Seconds 1"
goto wait_for_server

:open_browser
echo Opening %APP_URL% ...
start "" "%APP_URL%"
echo Crack Detaction is running. Close the Flask server window to stop it.
exit /b 0
