@echo off
REM ============================================================
REM 卸载 MyProject Windows 服务
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo  卸载 MyProject Windows 服务
echo ============================================================
echo.

REM 以管理员权限检查
net session >nul 2>&1
if errorlevel 1 (
    echo [X] 需要管理员权限
    pause
    exit /b 1
)

if exist "nssm.exe" (
    set NSSM=%CD%\nssm.exe
) else (
    set NSSM=nssm
)

echo [1/3] 停止并卸载 MyProject-Django...
net stop MyProject-Django 2>nul
%NSSM% remove MyProject-Django confirm 2>nul
echo [OK]

echo.
echo [2/3] 停止并卸载 MyProject-Daphne...
net stop MyProject-Daphne 2>nul
%NSSM% remove MyProject-Daphne confirm 2>nul
echo [OK]

echo.
echo [3/3] 停止并卸载 MyProject-Celery...
net stop MyProject-Celery 2>nul
%NSSM% remove MyProject-Celery confirm 2>nul
echo [OK]

echo.
echo ============================================================
echo  所有服务已卸载
echo ============================================================
pause
