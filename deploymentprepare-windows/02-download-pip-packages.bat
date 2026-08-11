@echo off
REM ============================================================
REM 下载 Python 依赖包（在有网机器执行）
REM 用途：把 requirements.txt 中所有依赖下载到 pip_packages 目录
REM 然后将 pip_packages 目录拷贝到无网服务器
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo  下载 Python 依赖包（离线安装用）
echo ============================================================
echo.

REM 确保在项目根目录执行
if not exist "..\requirements.txt" (
    echo [X] 未找到 ..\requirements.txt
    pause
    exit /b 1
)

REM 创建目录
if not exist "pip_packages" mkdir pip_packages

REM 下载依赖
echo [1/2] 下载依赖包到 pip_packages\ ...
pip download -r ..\requirements.txt -d pip_packages\ --python-version 3.11 --platform win_amd64 --only-binary=:all:

if errorlevel 1 (
    echo.
    echo [!] 部分包无预编译 wheel，尝试下载源码包...
    pip download -r ..\requirements.txt -d pip_packages\ --no-deps
)

echo.
echo [2/2] 下载完成
echo.
echo 依赖包已保存到: %CD%\pip_packages\
echo.
echo 下一步:
echo   1. 将整个 deploymentprepare-windows 文件夹拷贝到目标服务器
echo   2. 在目标服务器执行 03-install-python-deps.bat
echo.
pause
