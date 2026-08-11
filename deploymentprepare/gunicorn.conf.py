# ============================================================
# Gunicorn 配置 - Django 生产环境
# ============================================================
import multiprocessing
import os

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 4
timeout = 30
keepalive = 5

# 项目路径
chdir = "/opt/MyProject"

# 环境变量
raw_env = [
    "DJANGO_SETTINGS_MODULE=config.settings",
]

# 日志
accesslog = "/opt/MyProject/logs/gunicorn_access.log"
errorlog = "/opt/MyProject/logs/gunicorn_error.log"
loglevel = "info"

# 进程名
proc_name = "myproject_gunicorn"

# 优雅重启
graceful_timeout = 30
preload_app = True
