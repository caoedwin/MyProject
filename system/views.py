"""系统管理视图 - 菜单 / 角色 / 日志 / 用户菜单"""
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from system.models import Menu, Role, OperationLog, LoginLog
from system.serializers import (
    MenuSerializer, MenuTreeSerializer, RoleSerializer,
    OperationLogSerializer, LoginLogSerializer,
)
from system.permissions import HasPermission, get_user_menus, get_user_permissions
from system.utils import ok, fail


class MenuViewSet(viewsets.ModelViewSet):
    """菜单 / 权限 管理"""
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'system:menu'

    def get_queryset(self):
        qs = Menu.objects.all()
        # 默认只返回顶级，children 通过序列化递归
        parent_id = self.request.query_params.get('parent')
        keyword = self.request.query_params.get('keyword')
        if parent_id:
            qs = qs.filter(parent_id=parent_id)
        elif not self.request.query_params.get('all'):
            qs = qs.filter(parent__isnull=True)
        if keyword:
            qs = qs.filter(Q(name__icontains=keyword) | Q(permission__icontains=keyword))
        return qs.order_by('sort', 'id')

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        return Response(ok(MenuSerializer(qs, many=True).data))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ok(serializer.data, msg='创建成功'))

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ok(serializer.data, msg='更新成功'))


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'system:role'
    filterset_fields = ['status']
    search_fields = ['name', 'code']

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        return Response(ok(RoleSerializer(qs, many=True).data))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ok(serializer.data, msg='创建成功'))


class UserMenuView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """当前登录用户的菜单树 + 权限标识（前端动态路由用）"""
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        menus = get_user_menus(user)
        # 只返回目录 + 菜单（按钮不进路由树）
        route_menus = menus.filter(
            menu_type__in=[Menu.MenuType.DIRECTORY, Menu.MenuType.MENU],
            parent__isnull=True,
        ).order_by('sort', 'id')
        perms = get_user_permissions(user)
        data = {
            'menus': MenuTreeSerializer(route_menus, many=True).data,
            'permissions': list(perms),
        }
        return Response(ok(data))


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """操作日志查询"""
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'system:operation_log'
    filterset_fields = ['username', 'method']
    search_fields = ['path', 'username']
    ordering_fields = ['created_at', 'duration_ms']

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response(ok(serializer.data))


class DashboardViewSet(viewsets.GenericViewSet):
    """首页统计数据 - 全部从数据库实时查询"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request, *args, **kwargs):
        """汇总统计：用户数、未读消息、今日操作、AI 对话"""
        from django.contrib.auth import get_user_model
        from messaging.models import Message
        from aihub.models import ChatSession

        User = get_user_model()
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # 用户总数（排除超级管理员可选，这里保留全部）
        user_count = User.objects.count()

        # 当前用户的未读消息数（recipient 为当前用户且未读）
        unread_count = Message.objects.filter(
            recipient=request.user, is_read=False
        ).count()

        # 今日操作日志数
        today_ops = OperationLog.objects.filter(created_at__gte=today_start).count()

        # AI 对话会话总数
        ai_sessions = ChatSession.objects.count()

        data = {
            'user_count': user_count,
            'unread_count': unread_count,
            'today_ops': today_ops,
            'ai_sessions': ai_sessions,
        }
        return Response(ok(data))


class LoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """登录日志查询"""
    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_required = 'system:login_log'
    filterset_fields = ['username', 'result']
    search_fields = ['username', 'ip']
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response(ok(serializer.data))
