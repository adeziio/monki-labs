@echo off
setlocal


echo ==========================================
echo       Monki Labs Installer
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


echo.
echo Checking NVIDIA GPU...


nvidia-smi >nul 2>&1


if %errorlevel% equ 0 (

    echo NVIDIA GPU detected.

    echo Installing CUDA PyTorch...

    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128


) else (

    echo No NVIDIA GPU detected.

    echo Installing CPU PyTorch...

    pip install torch torchvision torchaudio

)


echo.
echo Installing Monki Labs dependencies...

pip install -r requirements.txt


echo.
echo Checking FFmpeg...


ffmpeg -version >nul 2>&1


if %errorlevel% neq 0 (

    echo FFmpeg not found.

    echo Installing FFmpeg using winget...

    winget install Gyan.FFmpeg --accept-package-agreements --accept-source-agreements


) else (

    echo FFmpeg detected.

)


echo.
echo Running hardware verification...


python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"


echo.
echo ==========================================
echo       Monki Labs Installation Complete
echo ==========================================

echo.
echo Run:
echo.
echo python main.py
echo.


pause