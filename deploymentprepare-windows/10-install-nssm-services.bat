@echo off
REM ============================================================
REM 使用 NSSM 将 MyProject 注册为 Windows 服务
REM 前置：需先下载 nssm.exe 到本目录
REM 下载地址（在有网机器）：https://nssm.cc/release/nssm-2.24.zip
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo  注册 MyProject 为 Windows 服务 (NSSM)
echo ============================================================
echo.

REM 检查 nssm
where nssm >nul 2>&1
if errorlevel 1 (
    if not exist "nssm.exe" (
        echo [X] 未找到 nssm.exe
        echo     请从 https://nssm.cc/release/nssm-2.24.zip 下载
        echo     解压后将 nssm.exe 放到本目录: %CD%
        pause
        exit /b 1
    )
    set NSSM=%CD%\nssm.exe
) else (
    set NSSM=nssm
)

REM 项目路径
set PROJECT_DIR=%~dp0..
set PYTHON=%PROJECT_DIR%\Myprojectvenv\Scripts\python.exe

echo 项目目录: %PROJECT_DIR%
echo Python:   %PYTHON%
echo.

REM 以管理员权限检查
net session >nul 2>&1
if errorlevel 1 (
    echo [X] 需要管理员权限运行此脚本
    echo     右键此脚本 -^> 以管理员身份运行
    pause
    exit /b 1
)

echo [1/4] 安装 MyProject-Django 服务...
%NSSM% install MyProject-Django %PYTHON% "%PROJECT_DIR%\manage.py" runserver 0.0.0.0:8000
%NSSM% set MyProject-Django AppDirectory %PROJECT_DIR%
%NSSM% set MyProject-Django AppStdout "%PROJECT_DIR%\logs\django.log"
%NSSM% set MyProject-Django AppStderr "%PROJECT_DIR%\logs\django.log"
%NSSM% set MyProject-Django AppRotateFiles 1
%NSSM% set MyProject-Django AppRotateBytes 10485760
%NSSM% set MyProject-Django Start SERVICE_AUTO_START
echo [OK] MyProject-Django 已安装

echo.
echo [2/4] 安装 MyProject-Daphne 服务...
%NSSM% install MyProject-Daphne "%PROJECT_DIR%\Myprojectvenv\Scripts\daphne.exe" -b 0.0.0.0 -p 8001 config.asgi:application
%NSSM% set MyProject-Daphne AppDirectory %PROJECT_DIR%
%NSSM% set MyProject-Daphne AppStdout "%PROJECT_DIR%\logs\daphne.log"
%NSSM% set MyProject-Daphne AppStderr "%PROJECT_DIR%\logs\daphne.log"
%NSSM% set MyProject-Daphne Start SERVICE_AUTO_START
echo [OK] MyProject-Daphne 已安装

echo.
echo [3/4] 安装 MyProject-Celery 服务...
%NSSM% install MyProject-Celery "%PROJECT_DIR%\Myprojectvenv\Scripts\celery.exe" -A config worker -l info
%NSSM% set MyProject-Celery AppDirectory %PROJECT_DIR%
%NSSM% set MyProject-Celery AppStdout "%PROJECT_DIR%\logs\celery.log"
%NSSM% set MyProject-Celery AppStderr "%PROJECT_DIR%\logs\celery.log"
%NSSM% set MyProject-Celery Start SERVICE_AUTO_START
echo [OK] MyProject-Celery 已安装

echo.
echo [4/4] 创建日志目录...
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"
echo [OK] 日志目录已创建

echo.
echo ============================================================
echo  所有服务已安装!
echo ============================================================
echo.
echo 启动服务:
echo   net start MyProject-Django
echo   net start MyProject-Daphne
echo   net start MyProject-Celery
echo.
echo 停止服务:
echo   net stop MyProject-Django
echo   net stop MyProject-Daphne
echo   net stop MyProject-Celery
echo.
echo 卸载服务:
echo   %NSSM% remove MyProject-Django confirm
echo   %NSSM% remove MyProject-Daphne confirm
echo   %NSSM% remove MyProject-Celery confirm
echo.
echo 服务列表可在 services.msc 中查看
echo.
pause
