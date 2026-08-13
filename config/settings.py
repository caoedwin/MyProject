"""
Django settings for config project.
前后端分离框架 - Python 3.14 + Django 6.1 + MySQL + Vue3
"""
import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全配置
SECRET_KEY = 'django-insecure-f%mw8t9vypmb=w)g$t7n_oatz)94)avqs+y#$9j%^vu46+kziy'
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# ============================================================
# 应用注册
# ============================================================
INSTALLED_APPS = [
    'daphne',  # ASGI 服务，置于首位以使用 Channels
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 第三方
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'guardian',
    'channels',
    'django_celery_beat',
    'django_celery_results',

    # 本地应用
    'app01',          # 认证 / 用户 / 登录注册
    'system',         # RBAC：菜单 / 权限 / 角色 / 操作日志
    'tasks',          # Celery 异步 / 定时任务
    'messaging',      # Channels 消息推送
    'aihub',          # AI 能力集成
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 跨域，置于首位
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 自定义操作日志中间件
    'system.middleware.OperationLogMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ============================================================
# 数据库 - MySQL 8.4 (Docker 容器，端口 3307，与本机 MySQL 8.0 隔离)
# 启动容器: docker compose up -d
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myproject',
        'USER': 'edwin',
        'PASSWORD': 'DCT@2019',
        'HOST': '127.0.0.1',
        'PORT': '3307',  # Docker 容器映射端口，避免与本机 3306 冲突
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Guardian 对象级权限（RBAC 辅助）
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)
ANONYMOUS_USER_NAME = 'AnonymousUser'

# 自定义用户模型
AUTH_USER_MODEL = 'app01.User'

# ============================================================
# 密码校验
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# 国际化
# ============================================================
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# ============================================================
# 静态文件 / 媒体文件
# ============================================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ============================================================
# CSRF / 跨域信任（开发环境：Vite 代理访问 admin）
# ============================================================
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 默认主键字段
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# Redis 业务配置（用于库存预扣、分布式锁、幂等缓存）
# ============================================================
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = 'DCT2019'
REDIS_DB_BUSINESS = 3

# Django 缓存（使用业务库 3）
# CONNECTION_POOL_KWARGS protocol=2 兼容 Redis < 6.0
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_BUSINESS}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
            'CONNECTION_POOL_KWARGS': {'protocol': 2},
        },
    }
}

# Channels 层（消息推送，使用独立的 Redis db 4，避免与 celery/channels 冲突）
# 使用 RedisPubSubChannelLayer（Pub/Sub 机制），兼容 Redis 2.0+（无需 BZPOPMIN）
# protocol=2 强制使用 RESP2 协议，兼容 Redis < 6.0（不支持 HELLO 命令）
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.pubsub.RedisPubSubChannelLayer',
        'CONFIG': {
            'hosts': [{
                'address': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/4',
                'protocol': 2,
            }],
        },
    },
}

# ============================================================
# Celery 异步 / 定时任务
# 同一台机器启动多个 celery，BROKER_URL 必须不同
# ============================================================
CELERY_BROKER_URL = 'redis://:DCT2019@localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://:DCT2019@localhost:6379/2'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 60 * 30
CELERY_RESULT_EXTENDED = True
# 定时任务调度器
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# ============================================================
# Django REST Framework
# ============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'system.exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# ============================================================
# SimpleJWT 配置
# ============================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'app01.serializers.LoginSerializer',
}

# ============================================================
# CORS 跨域
# ============================================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
    'x-remember-me', 'x-menu-mode',
]
CORS_EXPOSE_HEADERS = ['Content-Disposition', 'X-Total-Count']

# ============================================================
# drf-spectacular API 文档
# ============================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'MyProject API',
    'DESCRIPTION': '前后端分离系统 API 文档',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# ============================================================
# 登录安全
# ============================================================
LOGIN_ATTEMPT_LIMIT = 5           # 最大尝试次数
LOGIN_ATTEMPT_WINDOW = 600        # 窗口秒数
LOGIN_LOCK_DURATION = 600         # 锁定秒数
REMEMBER_ME_DAYS = 30             # 记住密码 token 有效期

# ============================================================
# AI 集成
# ============================================================
AI_PROVIDER = 'openai'  # openai / anthropic / custom
AI_API_KEY = os.environ.get('AI_API_KEY', '')
AI_BASE_URL = os.environ.get('AI_BASE_URL', 'https://api.openai.com/v1')
AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4o-mini')
AI_TIMEOUT = float(os.environ.get('AI_TIMEOUT', '60'))  # 连接 + 读取总超时（秒）
AI_MAX_RETRIES = int(os.environ.get('AI_MAX_RETRIES', '1'))

# ============================================================
# 日志配置
# ============================================================
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
        'simple': {
            'format': '[{asctime}] {levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'},
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'django_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 7,
            'formatter': 'verbose',
        },
        'operation_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'operation.log',
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 15,
            'formatter': 'verbose',
        },
        'task_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'celery.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 7,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'django_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'system.operation': {
            'handlers': ['console', 'operation_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'task_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'app01': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'tasks': {'handlers': ['console', 'task_file'], 'level': 'INFO', 'propagate': False},
        'messaging': {'handlers': ['console', 'django_file'], 'level': 'DEBUG', 'propagate': False},
    },
}

# ============================================================
# Email（开发环境控制台）
# ============================================================
MAILERS = {
    'default': {'BACKEND': 'django.core.mail.backends.console.EmailBackend'},
}

# 会话 cookie（前端 remember-me 时使用长有效期）
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
SESSION_SAVE_EVERY_REQUEST = True
