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
        # RBAC 过滤：只返回用户有权访问的子菜单
        allowed_ids = self.context.get('allowed_ids')
        if allowed_ids is not None:
            children = children.filter(id__in=allowed_ids)
        return MenuTreeSerializer(children, many=True, context=self.context).data


class RoleSerializer(serializers.ModelSerializer):
    menu_ids = serializers.PrimaryKeyRelatedField(
        source='menus', many=True, queryset=Menu.objects.all(),
        required=False
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'menu_ids', 'remark', 'status', 'created_at']

    def validate(self, attrs):
        """自动补全祖先菜单：选子菜单时，父级目录自动加入"""
        if 'menus' in attrs:
            from system.models import Menu
            menu_ids = [m.id for m in attrs['menus']]
            expanded = Menu.expand_ancestors(menu_ids)
            attrs['menus'] = Menu.objects.filter(id__in=expanded)
        return attrs


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
