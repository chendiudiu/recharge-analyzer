@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo Recharge Analyzer - Build Script
echo ========================================
echo.

echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo [3/4] Cleaning old build...
if exist dist rmdir /s /q
if exist build rmdir /s /q

echo [4/4] Building executable...
pyinstaller --onefile --name "RechargeAnalyzer" -w src/main.py

if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo Output: dist\RechargeAnalyzer.exe
echo ========================================
echo.
pause