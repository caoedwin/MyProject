@echo off
REM ============================================================
REM MyProject Windows 离线部署 - 环境检查
REM 用途：在目标 Windows 服务器上检查前置环境
REM ============================================================
chcp 65001 >nul
echo ============================================================
echo  MyProject 环境检查
echo ============================================================
echo.

REM 检查 Python
echo [1] 检查 Python...
python --version 2>nul
if errorlevel 1 (
    echo     [X] Python 未安装或未加入 PATH
    echo     请安装 Python 3.10+ (推荐 3.11/3.12)
) else (
    echo     [OK] Python 已安装
)
echo.

REM 检查 pip
echo [2] 检查 pip...
pip --version 2>nul
if errorlevel 1 (
    echo     [X] pip 未安装
) else (
    echo     [OK] pip 已安装
)
echo.

REM 检查 MySQL
echo [3] 检查 MySQL...
where mysql 2>nul
if errorlevel 1 (
    echo     [!] MySQL 客户端未加入 PATH
    echo     如使用 Docker MySQL，可跳过此项
) else (
    echo     [OK] MySQL 客户端已安装
)
echo.

REM 检查 Redis
echo [4] 检查 Redis...
where redis-cli 2>nul
if errorlevel 1 (
    echo     [!] Redis 未安装
    echo     请安装 Redis for Windows 或使用 Docker
) else (
    redis-cli ping 2>nul | findstr PONG >nul
    if errorlevel 1 (
        echo     [!] Redis 未运行
    ) else (
        echo     [OK] Redis 正在运行
    )
)
echo.

REM 检查 Docker
echo [5] 检查 Docker...
where docker 2>nul
if errorlevel 1 (
    echo     [!] Docker 未安装
) else (
    docker version 2>nul | findstr Version >nul
    if errorlevel 1 (
        echo     [!] Docker 未运行
    ) else (
        echo     [OK] Docker 已就绪
    )
)
echo.

REM 检查 Node.js (仅构建前端时需要)
echo [6] 检查 Node.js (仅构建前端需要)...
where node 2>nul
if errorlevel 1 (
    echo     [!] Node.js 未安装
    echo     如已在其他机器构建前端 dist，可跳过
) else (
    echo     [OK] Node.js 已安装
)
echo.

echo ============================================================
echo  检查完成。请根据上面 [X] 或 [!] 项进行修复
echo ============================================================
pause
