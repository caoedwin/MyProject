@echo off
REM ============================================================
REM 启动 MyProject 所有服务（Django + Daphne + Celery）
REM 生产环境使用 NSSM 注册为 Windows 服务更稳定
REM 详见 README-windows-deploy.md
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0\.."

echo ============================================================
echo  启动 MyProject 服务
echo ============================================================
echo.

REM 激活虚拟环境
if exist "Myprojectvenv\Scripts\activate.bat" (
    call "Myprojectvenv\Scripts\activate.bat"
)

echo [1/3] 启动 Django (Gunicorn/Runserver) on :8000...
start "MyProject-Django" cmd /k "call Myprojectvenv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"
echo [OK] Django 已在新窗口启动 (端口 8000)

echo.
echo [2/3] 启动 Daphne (WebSocket) on :8001...
start "MyProject-Daphne" cmd /k "call Myprojectvenv\Scripts\activate.bat && daphne -b 0.0.0.0 -p 8001 config.asgi:application"
echo [OK] Daphne 已在新窗口启动 (端口 8001)

echo.
echo [3/3] 启动 Celery Worker...
start "MyProject-Celery" cmd /k "call Myprojectvenv\Scripts\activate.bat && celery -A config worker -l info"
echo [OK] Celery 已在新窗口启动

echo.
echo ============================================================
echo  所有服务已启动!
echo ============================================================
echo.
echo 服务端口:
echo   Django:     http://localhost:8000/
echo   Django Admin: http://localhost:8000/admin/
echo   WebSocket:  ws://localhost:8001/
echo.
echo 关闭服务: 关闭对应的命令行窗口
echo.
echo 生产环境推荐: 使用 NSSM 注册为 Windows 服务 (见 README)
echo.
pause
