@echo off
setlocal


echo ==========================================
echo       Starting Monki Labs
echo ==========================================


echo.
echo Checking virtual environment...


if not exist ".venv\Scripts\activate.bat" (

    echo ERROR: Virtual environment not found.
    echo Please run install_windows.bat first.
    pause
    exit /b 1

)


echo Activating virtual environment...

call .venv\Scripts\activate


echo.
echo Running Monki Labs...


python main.py


if %errorlevel% neq 0 (

    echo.
    echo Monki Labs exited with an error.

)


pause