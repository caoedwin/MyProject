@echo off
REM ============================================================
REM 离线安装 Python 依赖（在无网服务器执行）
REM 前置：已执行 02-download-pip-packages.bat 并将 pip_packages 拷贝过来
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo  离线安装 Python 依赖
echo ============================================================
echo.

REM 激活虚拟环境（如果存在）
if exist "..\Myprojectvenv\Scripts\activate.bat" (
    call "..\Myprojectvenv\Scripts\activate.bat"
    echo [OK] 已激活虚拟环境
) else (
    echo [!] 虚拟环境不存在，将使用系统 Python
)

if not exist "pip_packages" (
    echo [X] 未找到 pip_packages 目录
    echo     请先在有网机器执行 02-download-pip-packages.bat
    pause
    exit /b 1
)

if not exist "..\requirements.txt" (
    echo [X] 未找到 ..\requirements.txt
    pause
    exit /b 1
)

echo.
echo [1/1] 从 pip_packages\ 离线安装依赖...
pip install --no-index --find-links=pip_packages\ -r ..\requirements.txt

if errorlevel 1 (
    echo.
    echo [X] 安装失败，请检查 pip_packages 目录是否完整
    pause
    exit /b 1
)

echo.
echo [OK] 依赖安装完成
echo.
echo 下一步:
echo   1. 执行 04-init-mysql.bat 初始化数据库
echo   2. 执行 05-migrate.bat 执行数据库迁移
echo.
pause
