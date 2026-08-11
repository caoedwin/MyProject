from rest_framework import serializers
from system.models import Menu, Role, UserRole, OperationLog, LoginLog


class MenuSerializer(serializers.ModelSerializer):
    """菜单序列化（含子菜单树）"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            'id', 'name', 'parent', 'menu_type', 'path', 'component',
            'redirect', 'icon', 'permission', 'sort', 'is_visible',
            'is_external', 'require_auth', 'status', 'children',
        ]

    def get_children(self, obj):
        children = obj.children.filter(status=True).order_by('sort', 'id')
        return MenuSerializer(children, many=True).data


class MenuTreeSerializer(serializers.ModelSerializer):
    """精简菜单树 - 供前端路由生成"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            'id', 'name', 'path', 'component', 'redirect', 'icon',
            'is_visible', 'is_external', 'menu_type', 'permission', 'sort',
            'children',
        ]

    def get_children(self, obj):
        children = obj.children.filter(status=True, is_visible=True).order_by('sort', 'id')
        return MenuTreeSerializer(children, many=True).data


class RoleSerializer(serializers.ModelSerializer):
    menu_ids = serializers.PrimaryKeyRelatedField(
        source='menus', many=True, queryset=Menu.objects.all(),
        required=False, write_only=True
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'menu_ids', 'remark', 'status', 'created_at']


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'created_at']


class OperationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationLog
        fields = [
            'id', 'username', 'method', 'path', 'query', 'status_code',
            'ip', 'duration_ms', 'created_at',
        ]


class LoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginLog
        fields = [
            'id', 'username', 'ip', 'location', 'browser',
            'result', 'message', 'created_at',
        ]
