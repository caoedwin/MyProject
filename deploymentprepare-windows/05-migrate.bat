@echo off
REM ============================================================
REM 执行 Django 数据库迁移 + 初始化数据 + 收集静态文件
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0\.."

echo ============================================================
echo  Django 数据库迁移
echo ============================================================
echo.

REM 激活虚拟环境
if exist "Myprojectvenv\Scripts\activate.bat" (
    call "Myprojectvenv\Scripts\activate.bat"
    echo [OK] 已激活虚拟环境
) else (
    echo [X] 虚拟环境不存在
    pause
    exit /b 1
)

echo.
echo [1/4] 执行数据库迁移...
python manage.py migrate
if errorlevel 1 (
    echo [X] 迁移失败
    pause
    exit /b 1
)
echo [OK] 迁移完成

echo.
echo [2/4] 初始化基础数据...
python manage.py init_data
if errorlevel 1 (
    echo [!] init_data 命令不存在或失败，跳过
) else (
    echo [OK] 基础数据初始化完成
)

echo.
echo [3/4] 收集静态文件...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo [X] 收集静态文件失败
    pause
    exit /b 1
)
echo [OK] 静态文件收集完成

echo.
echo [4/4] 创建超级用户...
echo 如果需要创建超级用户，请手动执行:
echo   python manage.py createsuperuser
echo.

echo ============================================================
echo  数据库准备完成！
echo ============================================================
echo.
echo 下一步: 执行 06-start-services.bat 启动服务
pause
