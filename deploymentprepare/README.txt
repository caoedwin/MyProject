# ============================================================
# MyProject 生产环境部署指南
# 目标环境: Linux (CentOS 7+/Ubuntu 20.04+), 无外网
# ============================================================

# ============================================================
# 一、服务器基础环境
# ============================================================

## 1.1 安装系统依赖
# CentOS/RHEL:
#   yum install -y gcc gcc-devel python3-devel libffi-devel openssl-devel \
#                   mysql-devel redis nginx supervisor
# Ubuntu/Debian:
#   apt install -y gcc python3-dev libffi-dev libssl-dev default-libmysqlclient-dev \
#                   redis-server nginx supervisor

## 1.2 Python 3.14 安装 (如果系统没有)
# 从 python.org 下载 Python 3.14.x 源码包, 离线编译安装:
#   tar xzf Python-3.14.7.tgz
#   cd Python-3.14.7
#   ./configure --prefix=/usr/local --enable-optimizations
#   make -j$(nproc)
#   make altinstall

# ============================================================
# 二、MySQL 8.4 部署
# ============================================================

## 2.1 安装 MySQL (离线)
# 从 MySQL 官网下载对应版本的 rpm/deb 包
# CentOS:
#   rpm -ivh mysql84-community-server-8.4.0-1.el9.x86_64.rpm
# Ubuntu:
#   dpkg -i mysql-server_8.4.0-1ubuntu24.04_amd64.deb

## 2.2 配置 MySQL
# 参见 mysql_setup.sql 和 my.cnf

## 2.3 创建数据库和用户
# mysql -u root -p < mysql_setup.sql

# ============================================================
# 三、Redis 部署
# ============================================================

## 3.1 安装 Redis (离线)
# 从 redis.io 下载源码编译或使用包管理器
#   tar xzf redis-7.2.5.tar.gz
#   cd redis-7.2.5 && make && make install

## 3.2 配置
#   cp redis.conf /etc/redis/redis.conf
#   修改 requirepass 为生产密码

## 3.3 版本兼容性说明（重要！）
# 本项目使用 RedisPubSubChannelLayer（Pub/Sub 机制）+ protocol=2（RESP2 协议）
# 兼容 Redis 2.0+，无需 Redis 5.0+ 的 BZPOPMIN 或 6.0+ 的 HELLO 命令
# 推荐安装 Redis 6.0+ 以获得最佳性能和稳定性
# 如果使用 Redis < 6.0，必须保持 settings.py 中的 protocol=2 配置

# ============================================================
# 四、Python 依赖 (离线安装)
# ============================================================

## 4.1 在有网机器上下载所有依赖
# 执行 download_pip_packages.sh 或:
#   pip download -r requirements.txt -d pip_packages/ --python-version 3.14 --platform manylinux2014_x86_64

## 4.2 传输到服务器后离线安装
#   pip install --no-index --find-links=pip_packages/ -r requirements.txt

## 4.3 或者使用项目自带的虚拟环境
#   复制整个 Myprojectvenv 目录到服务器

# ============================================================
# 五、项目部署
# ============================================================

## 5.1 上传项目
#   scp -r MyProject user@server:/opt/

## 5.2 前端构建
#   cd frontend && npm install && npm run build
#   (在有网机器构建后上传 dist/ 即可)

## 5.3 配置环境变量
#   cp myproject.env /etc/myproject.env
#   修改其中的密钥和数据库密码

## 5.4 数据库迁移
#   source /etc/myproject.env
#   python manage.py migrate
#   python manage.py init_data

## 5.5 收集静态文件
#   python manage.py collectstatic --noinput

## 5.6 启动服务
#   systemctl daemon-reload
#   systemctl start myproject-gunicorn
#   systemctl start myproject-daphne
#   systemctl start myproject-celery
#   systemctl start myproject-celery-beat
#   systemctl enable myproject-gunicorn
#   systemctl enable myproject-daphne
#   systemctl enable myproject-celery
#   systemctl enable myproject-celery-beat

## 5.7 配置 Nginx
#   cp nginx.conf /etc/nginx/conf.d/myproject.conf
#   nginx -t && systemctl reload nginx

# ============================================================
# 六、目录结构 (生产环境)
# ============================================================
# /opt/MyProject/
# ├── config/          # Django 配置
# ├── app01/           # 认证模块
# ├── system/          # RBAC 模块
# ├── messaging/       # 消息推送
# ├── tasks/           # 定时/异步任务
# ├── aihub/           # AI 模块
# ├── frontend/dist/   # 前端构建产物
# ├── staticfiles/     # 收集的静态文件
# ├── media/           # 用户上传文件
# ├── logs/            # 日志
# ├── requirements.txt
# ├── manage.py
# └── gunicorn.conf.py

# ============================================================
# 七、端口规划
# ============================================================
# Nginx: 80/443 (对外)
# Gunicorn: 8000 (内网)
# Daphne: 8001 (WebSocket)
# MySQL: 3306
# Redis: 6379
# Celery 无独立端口
# Celery Beat 无独立端口
