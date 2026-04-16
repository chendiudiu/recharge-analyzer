@echo off
echo ========================================
echo 充值明细统计工具 - Windows 构建脚本
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [2/4] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 依赖安装失败
    pause
    exit /b 1
)

echo [3/4] 清理旧构建...
if exist dist rmdir /s /q
if exist build rmdir /s /q
if exist *.spec del /q *.spec

echo [4/4] 打包为Windows可执行程序...
pyinstaller --onefile --name "充值明细统计" -w src/main.py

if errorlevel 1 (
    echo 构建失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 构建完成！
echo 可执行文件位于: dist\充值明细统计.exe
echo ========================================
echo.
pause