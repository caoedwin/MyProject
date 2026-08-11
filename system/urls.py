from django.urls import path, include
from rest_framework.routers import DefaultRouter

from system.views import (
    MenuViewSet, RoleViewSet, UserMenuView,
    OperationLogViewSet, LoginLogViewSet, DashboardViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r'menus', MenuViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'operation-logs', OperationLogViewSet)
router.register(r'login-logs', LoginLogViewSet)
# 当前用户菜单树（不进 admin，单独注册）
router.register(r'user-menus', UserMenuView, basename='user-menus')
# 首页统计数据
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
