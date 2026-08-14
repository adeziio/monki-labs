@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo ==========================================
echo Starting Monki Labs
echo ==========================================
echo.

set "OLLAMA_URL=http://localhost:11434"

echo Checking Ollama...

where ollama >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Ollama is not installed.
    echo Please run install_windows.bat first.
    exit /b 1
)

echo Ollama detected.
echo.

echo Stopping existing Ollama processes...

taskkill /F /IM ollama.exe >nul 2>&1
taskkill /F /IM ollama_llama_server.exe >nul 2>&1
taskkill /F /IM llama-server.exe >nul 2>&1

timeout /t 3 /nobreak >nul

echo Existing Ollama processes stopped.
echo.

echo Starting Ollama on CPU...

set "OLLAMA_NUM_GPU=0"
set "OLLAMA_VULKAN=0"
set "OLLAMA_NO_CLOUD=1"

start "" /B cmd /c "ollama serve >nul 2>&1"

echo Ollama started.
echo.

echo Waiting for Ollama...

set "OLLAMA_READY=0"

for /L %%i in (1,1,30) do (

    curl -s --max-time 2 "%OLLAMA_URL%/api/tags" >nul 2>&1

    if not errorlevel 1 (
        set "OLLAMA_READY=1"
        goto :ollama_ready
    )

    timeout /t 1 /nobreak >nul
)

:ollama_ready

if "%OLLAMA_READY%"=="0" (

    echo.
    echo ERROR: Ollama failed to start.
    echo.

    exit /b 1
)

echo Ollama is ready.
echo.

echo Checking Ollama model...

ollama list | findstr /C:"qwen3:8b" >nul 2>&1

if errorlevel 1 (

    echo qwen3:8b not found.
    echo Pulling qwen3:8b...
    echo.

    ollama pull qwen3:8b

    if errorlevel 1 (
        echo.
        echo ERROR: Failed to pull qwen3:8b.
        exit /b 1
    )

) else (

    echo qwen3:8b detected.

)

echo.

echo Checking GPU memory...

where nvidia-smi >nul 2>&1

if not errorlevel 1 (
    nvidia-smi
    echo.
)

echo.

REM Ollama is already running separately in CPU-only mode.
REM Clear the Ollama-specific environment variables before
REM launching Monki Labs so the video pipeline can use its GPU.

set "OLLAMA_NUM_GPU="
set "OLLAMA_VULKAN="
set "OLLAMA_NO_CLOUD="

python main.py

set "EXIT_CODE=%errorlevel%"

echo.

if "%EXIT_CODE%"=="0" (

    echo ==========================================
    echo        Monki Labs Complete
    echo ==========================================

) else (

    echo ==========================================
    echo        Monki Labs Failed
    echo ==========================================
    echo.
    echo Exit code: %EXIT_CODE%

)

exit /b %EXIT_CODE%