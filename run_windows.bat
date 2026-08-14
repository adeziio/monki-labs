@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo ==========================================
echo Starting Monki Labs
echo ==========================================
echo.

set "OLLAMA_URL=http://localhost:11434"
set "OLLAMA_LOG=ollama.log"

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

echo Checking GPU memory...

where nvidia-smi >nul 2>&1

if not errorlevel 1 (
nvidia-smi
echo.
)

echo Starting Ollama on CPU...

del /Q "%OLLAMA_LOG%" >nul 2>&1

set "OLLAMA_NUM_GPU=0"
set "OLLAMA_VULKAN=0"
set "OLLAMA_NO_CLOUD=1"

start "" /B ollama serve >"%OLLAMA_LOG%" 2>&1

echo Ollama started.
echo.

echo Waiting for Ollama...

set "OLLAMA_READY=0"

for /L %%i in (1,1,30) do (
curl -s --max-time 2 "%OLLAMA_URL%/api/tags" >nul 2>&1

if not errorlevel 1 (
    set "OLLAMA_READY=1"
)

if "!OLLAMA_READY!"=="1" (
    rem Ollama is ready.
    set "OLLAMA_WAIT_DONE=1"
)

if "!OLLAMA_WAIT_DONE!"=="1" (
    rem Continue looping silently until loop completes.
)

if "!OLLAMA_READY!"=="1" (
    rem Give the service a moment to fully initialize.
    timeout /t 1 /nobreak >nul
    set "OLLAMA_LOOP_DONE=1"
)

)

if "%OLLAMA_READY%"=="0" (

echo.
echo ERROR: Ollama failed to start.
echo.

echo Ollama log:
echo ------------------------------------------

if exist "%OLLAMA_LOG%" (
    type "%OLLAMA_LOG%"
) else (
    echo Ollama log not found.
)

echo ------------------------------------------
echo.

exit /b 1

)

echo Ollama is ready.
echo.

echo Verifying GPU memory is still available...

where nvidia-smi >nul 2>&1

if not errorlevel 1 (
nvidia-smi
echo.
)

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
echo.

echo Ollama log:
echo ------------------------------------------

if exist "%OLLAMA_LOG%" (
    type "%OLLAMA_LOG%"
) else (
    echo Ollama log not found.
)

echo ------------------------------------------

)

exit /b %EXIT_CODE%