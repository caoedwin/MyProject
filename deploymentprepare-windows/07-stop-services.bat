@echo off
REM ============================================================
REM 停止 MyProject 所有服务
REM ============================================================
chcp 65001 >nul

echo ============================================================
echo  停止 MyProject 服务
echo ============================================================
echo.

echo [1/3] 停止 Django...
taskkill /FI "WINDOWTITLE eq MyProject-Django*" /F /T 2>nul
echo [OK] Django 已停止

echo.
echo [2/3] 停止 Daphne...
taskkill /FI "WINDOWTITLE eq MyProject-Daphne*" /F /T 2>nul
echo [OK] Daphne 已停止

echo.
echo [3/3] 停止 Celery...
taskkill /FI "WINDOWTITLE eq MyProject-Celery*" /F /T 2>nul
echo [OK] Celery 已停止

echo.
echo ============================================================
echo  所有服务已停止
echo ============================================================
pause
