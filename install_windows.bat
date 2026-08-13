@echo off
setlocal enabledelayedexpansion


echo ==========================================
echo       Monki Labs Windows Installer
echo ==========================================


echo.
echo Checking Python...

python --version >nul 2>&1

if %errorlevel% neq 0 (
    echo ERROR: Python not found.
    echo Please install Python 3.12 first.
    pause
    exit /b 1
)

echo Python detected.


echo.
echo Creating virtual environment...

if not exist ".venv" (
    python -m venv .venv
)

echo Virtual environment ready.


echo.
echo Activating environment...

call .venv\Scripts\activate


echo.
echo Upgrading pip...

python -m pip install --upgrade pip

if %errorlevel% neq 0 (
    echo Failed upgrading pip.
    pause
    exit /b 1
)


echo.
echo Checking NVIDIA GPU...

nvidia-smi >nul 2>&1

if %errorlevel% equ 0 (

    echo NVIDIA GPU detected.
    echo Installing CUDA PyTorch...

    pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

) else (

    echo No NVIDIA GPU detected.
    echo Installing CPU PyTorch...

    pip install --upgrade torch torchvision torchaudio

)

if %errorlevel% neq 0 (
    echo Failed installing PyTorch.
    pause
    exit /b 1
)


echo.
echo Installing Monki Labs dependencies...

pip install --upgrade -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed installing dependencies.
    pause
    exit /b 1
)


echo.
echo Checking FFmpeg...

ffmpeg -version >nul 2>&1

if %errorlevel% neq 0 (

    echo FFmpeg not found.
    echo Installing FFmpeg using winget...

    winget install Gyan.FFmpeg --accept-package-agreements --accept-source-agreements

    if %errorlevel% neq 0 (
        echo Failed installing FFmpeg.
        pause
        exit /b 1
    )

) else (

    echo FFmpeg detected.

)


echo.
echo Checking Ollama...

ollama --version >nul 2>&1

if %errorlevel% neq 0 (

    echo Ollama not found.
    echo Installing Ollama using winget...

    winget install Ollama.Ollama --accept-package-agreements --accept-source-agreements

    if %errorlevel% neq 0 (
        echo Failed installing Ollama.
        pause
        exit /b 1
    )

) else (

    echo Ollama detected.

)


echo.
echo Reading Ollama configuration...

for /f "delims=" %%i in ('python -c "import json; c=json.load(open('config/ai_models.json', encoding='utf-8')); m=c.get('models',{}).get('language_model',{}); print(m.get('model','')); print(m.get('provider','')); print(str(m.get('enabled',False)).lower())"') do (

    if not defined OLLAMA_CONFIG_MODEL (
        set "OLLAMA_CONFIG_MODEL=%%i"
    ) else if not defined OLLAMA_CONFIG_PROVIDER (
        set "OLLAMA_CONFIG_PROVIDER=%%i"
    ) else if not defined OLLAMA_CONFIG_ENABLED (
        set "OLLAMA_CONFIG_ENABLED=%%i"
    )

)


if /i "!OLLAMA_CONFIG_ENABLED!"=="true" if /i "!OLLAMA_CONFIG_PROVIDER!"=="ollama" (

    echo Configured Ollama model: !OLLAMA_CONFIG_MODEL!

    echo.
    echo Starting Ollama...

    tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I "ollama.exe" >NUL

    if !errorlevel! neq 0 (
        start "" /B ollama serve
        timeout /t 5 /nobreak >nul
    ) else (
        echo Ollama is already running.
    )


    echo.
    echo Checking configured Ollama model...

    ollama list | findstr /I /C:"!OLLAMA_CONFIG_MODEL!" >nul

    if !errorlevel! neq 0 (

        echo Model not found.
        echo Pulling !OLLAMA_CONFIG_MODEL!...

        ollama pull !OLLAMA_CONFIG_MODEL!

        if !errorlevel! neq 0 (
            echo Failed pulling Ollama model.
            pause
            exit /b 1
        )

    ) else (

        echo Ollama model already available.

    )

) else (

    echo Ollama language model is disabled or provider is not Ollama.
    echo Skipping Ollama model setup.

)


echo.
echo Running hardware verification...

python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"


echo.
echo ==========================================
echo   Monki Labs Windows Installation Complete
echo ==========================================


echo.
echo Run:
echo.
echo run_windows.bat
echo.

pause