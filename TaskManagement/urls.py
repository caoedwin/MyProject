"""任务管理子系统 - URL 路由"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from TaskManagement.views import (
    TaskCategoryViewSet, TaskViewSet, TaskApprovalViewSet,
    TaskPerformanceViewSet, TaskStatsViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r'categories', TaskCategoryViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'approvals', TaskApprovalViewSet)
router.register(r'performances', TaskPerformanceViewSet)
router.register(r'stats', TaskStatsViewSet, basename='task-stats')

urlpatterns = [
    path('', include(router.urls)),
]