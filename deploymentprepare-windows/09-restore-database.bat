@echo off
REM ============================================================
REM 数据库恢复脚本
REM 用法: 09-restore-database.bat <backup_file.sql>
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

REM 配置
set MYSQL_HOST=127.0.0.1
set MYSQL_PORT=3307
set MYSQL_USER=root
set MYSQL_PASSWORD=DCT@2019
set MYSQL_DB=myproject

REM 参数检查
if "%~1"=="" (
    echo 用法: %~nx0 ^<backup_file.sql^>
    echo.
    echo 可用备份文件:
    if exist backups dir backups\*.sql /b
    pause
    exit /b 1
)

set RESTORE_FILE=%~1
if not exist "%RESTORE_FILE%" (
    echo [X] 备份文件不存在: %RESTORE_FILE%
    pause
    exit /b 1
)

echo ============================================================
echo  MySQL 数据库恢复
echo ============================================================
echo.
echo 备份文件: %RESTORE_FILE%
echo 目标数据库: %MYSQL_DB%
echo.
echo 警告: 此操作将覆盖现有数据！
echo 确认继续请按任意键，或按 Ctrl+C 取消...
pause >nul

REM 方式1：Docker MySQL
where docker >nul 2>&1
if not errorlevel 1 (
    echo [方式1] 使用 Docker MySQL...
    docker exec -i myproject_mysql84 mysql -u%MYSQL_USER% -p%MYSQL_PASSWORD% < "%RESTORE_FILE%"
    if not errorlevel 1 (
        echo [OK] 恢复成功
        pause
        exit /b 0
    )
    echo [!] Docker 方式失败，尝试本机 MySQL...
)

REM 方式2：本机 MySQL 客户端
where mysql >nul 2>&1
if not errorlevel 1 (
    echo [方式2] 使用本机 mysql...
    mysql -h%MYSQL_HOST% -P%MYSQL_PORT% -u%MYSQL_USER% -p%MYSQL_PASSWORD% < "%RESTORE_FILE%"
    if not errorlevel 1 (
        echo [OK] 恢复成功
        pause
        exit /b 0
    )
)

echo [X] 恢复失败
pause
exit /b 1
