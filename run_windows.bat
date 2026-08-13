@echo off
setlocal

echo ==========================================
echo       Starting Monki Labs
echo ==========================================

echo.
echo Activating virtual environment...

if not exist ".venv\Scripts\activate.bat" (

    echo ERROR: Virtual environment not found.
    echo Please run install_windows.bat first.

    pause
    exit /b 1

)

call .venv\Scripts\activate

echo.
echo Checking Ollama...

where ollama >nul 2>&1

if %errorlevel% neq 0 (

    echo ERROR: Ollama not found.
    echo Please run install_windows.bat first.

    pause
    exit /b 1

)

echo Ollama detected.

echo.
echo Checking Ollama service...

curl -s http://localhost:11434/api/tags >nul 2>&1

if %errorlevel% neq 0 (

    echo Ollama is not running.
    echo Starting Ollama in CPU-only mode...

    start "" /B cmd /c "set CUDA_VISIBLE_DEVICES=^& set NVIDIA_VISIBLE_DEVICES=^& set OLLAMA_VULKAN=0^& set OLLAMA_NUM_GPU=0^& ollama serve > ollama.log 2>&1"

    echo Waiting for Ollama...

    set OLLAMA_READY=0

    for /L %%i in (1,1,30) do (

        curl -s http://localhost:11434/api/tags >nul 2>&1

        if not errorlevel 1 (

            set OLLAMA_READY=1
            goto :ollama_ready

        )

        timeout /t 1 /nobreak >nul

    )

    :ollama_ready

    if "%OLLAMA_READY%" neq "1" (

        echo.
        echo ERROR: Ollama failed to start.

        echo.
        echo Ollama log:

        if exist ollama.log (
            type ollama.log
        )

        pause
        exit /b 1

    )

    echo Ollama started successfully.

) else (

    echo Ollama is already running.

)

echo.
echo Checking Ollama model...

ollama list | findstr /C:"qwen3:8b" >nul

if %errorlevel% neq 0 (

    echo ERROR: qwen3:8b is not installed.
    echo Please run install_windows.bat first.

    pause
    exit /b 1

)

echo qwen3:8b detected.

echo.
echo Running Monki Labs...

python main.py

if %errorlevel% neq 0 (

    echo.
    echo ==========================================
    echo       Monki Labs Failed
    echo ==========================================
    echo.
    echo Ollama log:

    if exist ollama.log (
        type ollama.log
    )

    echo.
    pause
    exit /b 1

)

echo.
echo ==========================================
echo       Monki Labs Complete
echo ==========================================

echo.
pause