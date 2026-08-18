"""自定义权限类 - 基于 RBAC 菜单权限标识校验"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasPermission(BasePermission):
    """
    按权限标识校验，使用方式：
        permission_classes = [HasPermission]
        required_permission = 'system:user_list'
    或在 view 中设置 permission_required = 'system:user_list'
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # 超级管理员放行
        if request.user.is_superuser:
            return True
        # 视图未声明 required_permission / permission_required 则仅校验登录
        required = getattr(view, 'permission_required', None) or getattr(view, 'required_permission', None)
        if not required:
            return True
        return _user_has_permission(request.user, required)


class IsAdminOrReadOnly(BasePermission):
    """管理员可写，其余只读"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser


def _user_has_permission(user, perm):
    """校验用户是否拥有某权限标识（system:action）"""
    if ':' in perm:
        app_label, codename = perm.split(':', 1)
        full_codename = f'{app_label}.{codename}'
    else:
        full_codename = perm
    return user.has_perm(full_codename)


def get_user_menus(user):
    """获取用户可见的菜单列表（含目录/菜单/按钮权限标识）"""
    from system.models import Menu
    if user.is_superuser:
        qs = Menu.objects.filter(status=True)
    else:
        # 通过角色关联菜单
        role_ids = user.user_roles.values_list('role_id', flat=True)
        qs = Menu.objects.filter(status=True, roles__id__in=role_ids).distinct()
        # 自动补全祖先菜单：选了子菜单，父级自动可见
        menu_ids = set(qs.values_list('id', flat=True))
        expanded_ids = Menu.expand_ancestors(menu_ids)
        if expanded_ids != menu_ids:
            qs = Menu.objects.filter(status=True, id__in=expanded_ids)
    return qs


def get_user_permissions(user):
    """获取用户所有权限标识集合"""
    if user.is_superuser:
        return {'*'}
    perms = set()
    # Django auth 权限
    for perm in user.get_all_permissions():
        app_label, codename = perm.split('.', 1)
        perms.add(f'{app_label}:{codename}')
    # 菜单中定义的按钮权限标识
    from system.models import Menu
    role_ids = user.user_roles.values_list('role_id', flat=True)
    button_perms = Menu.objects.filter(
        menu_type=Menu.MenuType.BUTTON, status=True,
        roles__id__in=role_ids
    ).exclude(permission='').values_list('permission', flat=True)
    perms.update(button_perms)
    return perms
