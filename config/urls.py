"""全局 URL 路由"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 认证 / 用户
    path('api/auth/', include('app01.urls')),
    # 系统管理（菜单 / 角色 / 日志）
    path('api/system/', include('system.urls')),
    # 消息推送
    path('api/messaging/', include('messaging.urls')),
    # AI 对话
    path('api/ai/', include('aihub.urls')),
    # 任务管理
    path('api/task/', include('TaskManagement.urls')),

    # API 文档
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
