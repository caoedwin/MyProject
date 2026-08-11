@echo off
REM ============================================================
REM 数据库备份脚本
REM 备份 Docker MySQL 或本机 MySQL 数据库
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

REM 配置
set MYSQL_HOST=127.0.0.1
set MYSQL_PORT=3307
set MYSQL_USER=root
set MYSQL_PASSWORD=DCT@2019
set MYSQL_DB=myproject

REM 备份目录
set BACKUP_DIR=backups
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

REM 文件名（带时间戳）
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set YYYY=%dt:~0,4%
set MM=%dt:~4,2%
set DD=%dt:~6,2%
set HH=%dt:~8,2%
set MIN=%dt:~10,2%
set SS=%dt:~12,2%
set BACKUP_FILE=%BACKUP_DIR%\%MYSQL_DB%_%YYYY%%MM%%DD%_%HH%%MIN%%SS%.sql

echo ============================================================
echo  MySQL 数据库备份
echo ============================================================
echo.
echo 数据库: %MYSQL_DB%
echo 备份到: %BACKUP_FILE%
echo.

REM 方式1：Docker MySQL
where docker >nul 2>&1
if not errorlevel 1 (
    echo [方式1] 使用 Docker MySQL...
    docker exec myproject_mysql84 mysqldump -u%MYSQL_USER% -p%MYSQL_PASSWORD% --databases %MYSQL_DB% --single-transaction --routines --triggers --events > %BACKUP_FILE%
    if not errorlevel 1 (
        echo [OK] 备份成功
        goto done
    )
    echo [!] Docker 方式失败，尝试本机 MySQL...
)

REM 方式2：本机 MySQL 客户端
where mysqldump >nul 2>&1
if not errorlevel 1 (
    echo [方式2] 使用本机 mysqldump...
    mysqldump -h%MYSQL_HOST% -P%MYSQL_PORT% -u%MYSQL_USER% -p%MYSQL_PASSWORD% --databases %MYSQL_DB% --single-transaction --routines --triggers --events > %BACKUP_FILE%
    if not errorlevel 1 (
        echo [OK] 备份成功
        goto done
    )
)

echo [X] 备份失败
pause
exit /b 1

:done
echo.
echo 备份文件: %BACKUP_FILE%
echo 文件大小:
for %%I in (%BACKUP_FILE%) do echo   %%~zI 字节
echo.
echo 恢复命令:
echo   08-restore-database.bat %BACKUP_FILE%
pause
