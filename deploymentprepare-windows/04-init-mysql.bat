@echo off
REM ============================================================
REM 初始化 MySQL 数据库
REM 适用于: Docker MySQL 或 Windows 原生 MySQL
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo  MySQL 数据库初始化
echo ============================================================
echo.

REM 读取配置
set MYSQL_HOST=127.0.0.1
set MYSQL_PORT=3307
set MYSQL_ROOT_PASSWORD=DCT@2019
set MYSQL_DB=myproject
set MYSQL_USER=edwin
set MYSQL_PASSWORD=DCT@2019

echo 数据库配置:
echo   主机: %MYSQL_HOST%
echo   端口: %MYSQL_PORT%
echo   数据库: %MYSQL_DB%
echo   用户: %MYSQL_USER%
echo.
echo 确认无误后按任意键继续，或按 Ctrl+C 取消...
pause >nul

REM 方式1：使用 Docker MySQL
where docker >nul 2>&1
if not errorlevel 1 (
    echo [方式1] 使用 Docker MySQL...
    docker exec -i myproject_mysql84 mysql -uroot -p%MYSQL_ROOT_PASSWORD% < mysql_setup.sql
    if not errorlevel 1 (
        echo [OK] 数据库初始化成功 (Docker)
        goto done
    )
    echo [!] Docker 方式失败，尝试本机 MySQL...
)

REM 方式2：使用本机 MySQL 客户端
where mysql >nul 2>&1
if not errorlevel 1 (
    echo [方式2] 使用本机 MySQL 客户端...
    mysql -h%MYSQL_HOST% -P%MYSQL_PORT% -uroot -p%MYSQL_ROOT_PASSWORD% < mysql_setup.sql
    if not errorlevel 1 (
        echo [OK] 数据库初始化成功 (本机 MySQL)
        goto done
    )
)

echo [X] MySQL 初始化失败
echo     请检查:
echo     1. Docker MySQL 容器是否运行: docker ps
echo     2. 或本机 MySQL 是否启动
echo     3. root 密码是否正确
pause
exit /b 1

:done
echo.
echo 下一步: 执行 05-migrate.bat
pause
