#!/bin/bash
# ============================================================
# MyProject 一键部署脚本 (离线环境)
# 使用方法: sudo bash deploy.sh
# ============================================================

set -e

PROJECT_DIR="/opt/MyProject"
VENV_DIR="/opt/MyProject/venv"
LOG_DIR="/opt/MyProject/logs"
ENV_FILE="/etc/myproject.env"

echo "================================================"
echo "  MyProject 生产环境部署"
echo "================================================"

# ---------- 1. 创建必要目录 ----------
echo "[1/7] 创建目录..."
mkdir -p "$PROJECT_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$PROJECT_DIR/media"
mkdir -p "$PROJECT_DIR/staticfiles"

# ---------- 2. 创建 Python 虚拟环境 ----------
echo "[2/7] 创建 Python 虚拟环境..."
if [ ! -d "$VENV_DIR" ]; then
    python3.14 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel

# ---------- 3. 安装 Python 依赖 ----------
echo "[3/7] 安装 Python 依赖..."
if [ -f "$PROJECT_DIR/pip_packages" ]; then
    pip install --no-index --find-links="$PROJECT_DIR/pip_packages/" -r "$PROJECT_DIR/requirements.txt"
else
    pip install -r "$PROJECT_DIR/requirements.txt"
fi

# ---------- 4. 检查环境变量 ----------
echo "[4/7] 检查环境变量..."
if [ ! -f "$ENV_FILE" ]; then
    echo "错误: 环境变量文件 $ENV_FILE 不存在!"
    echo "请先复制 myproject.env 到 $ENV_FILE 并配置好密码"
    exit 1
fi
source "$ENV_FILE"
export $(grep -v '^#' "$ENV_FILE" | xargs)

# ---------- 5. 数据库迁移 ----------
echo "[5/7] 执行数据库迁移..."
cd "$PROJECT_DIR"
python manage.py migrate --noinput
python manage.py init_data

# ---------- 6. 收集静态文件 ----------
echo "[6/7] 收集静态文件..."
python manage.py collectstatic --noinput

# ---------- 7. 设置权限 ----------
echo "[7/7] 设置目录权限..."
chown -R www-data:www-data "$PROJECT_DIR/media"
chown -R www-data:www-data "$PROJECT_DIR/staticfiles"
chown -R www-data:www-data "$LOG_DIR"

echo ""
echo "================================================"
echo "  部署完成!"
echo "  下一步: 配置 Systemd 服务和 Nginx"
echo "================================================"
echo ""
echo "  # 注册服务:"
echo "  cp deploymentprepare/myproject-*.service /etc/systemd/system/"
echo "  systemctl daemon-reload"
echo "  systemctl start myproject-gunicorn"
echo "  systemctl start myproject-daphne"
echo "  systemctl start myproject-celery"
echo "  systemctl start myproject-celery-beat"
echo ""
echo "  # 配置 Nginx:"
echo "  cp deploymentprepare/nginx.conf /etc/nginx/conf.d/myproject.conf"
echo "  nginx -t && systemctl reload nginx"
