"""系统管理后台注册 - RBAC + 用户 + 日志"""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.utils.html import format_html

from app01.models import User
from system.models import Menu, Role, UserRole, OperationLog, LoginLog
from aihub.models import ChatSession, ChatMessage
from TaskManagement.models import TaskCategory, Task, TaskApproval, TaskProgressRecord, TaskPerformance


class RoleAdminForm(forms.ModelForm):
    """角色管理表单：菜单选择只显示叶子节点，标签显示完整路径"""
    menus = forms.ModelMultipleChoiceField(
        queryset=Menu.objects.none(),
        required=False,
        label='关联菜单',
        widget=admin.widgets.FilteredSelectMultiple('菜单', False),
    )
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(), required=False,
        label='关联权限',
        widget=admin.widgets.FilteredSelectMultiple('权限', False),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 叶子菜单：menu_type=1(MENU) 且无子菜单，按完整路径排序
        leaf_menus = Menu.objects.filter(
            menu_type=Menu.MenuType.MENU, status=True,
        ).exclude(children__isnull=False).select_related('parent__parent__parent')
        # 构建带路径的菜单列表，重写 label 为完整路径
        self.fields['menus'].choices = self._build_choices(leaf_menus)
        self.fields['menus'].queryset = leaf_menus

    def _build_choices(self, menus):
        """为每个叶子菜单生成 "父级 > 子级" 格式的标签"""
        choices = []
        for menu in menus:
            path_parts = self._get_path(menu)
            label = ' > '.join(path_parts)
            choices.append((menu.pk, label))
        # 按路径排序
        choices.sort(key=lambda x: x[1])
        return choices

    def _get_path(self, menu):
        """递归获取菜单的完整路径（从根到叶）"""
        parts = []
        current = menu
        while current:
            parts.insert(0, current.name)
            current = current.parent
        return parts

    class Meta:
        model = Role
        fields = '__all__'


class UserChangeForm(forms.ModelForm):
    """用户编辑表单 - 角色多选（直观替代多条 UserRoleInline）"""
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.filter(status=True).order_by('name'),
        required=False,
        label='角色',
        widget=admin.widgets.FilteredSelectMultiple('角色', False),
        help_text='一个用户可拥有多个角色',
    )

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # 预填充当前用户已有的角色
            self.initial['roles'] = UserRole.objects.filter(
                user=self.instance
            ).values_list('role_id', flat=True)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'nickname', 'role_list', 'phone', 'status', 'menu_mode', 'menu_collapsed', 'is_superuser', 'last_login']
    list_filter = ['status', 'is_superuser', 'menu_mode', 'gender']
    search_fields = ['username', 'nickname', 'phone', 'email']
    list_editable = ['status', 'menu_mode', 'menu_collapsed']
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('nickname', 'avatar', 'phone', 'gender', 'status',
                                'remember_token', 'remember_token_expires', 'last_login_ip',
                                'menu_mode', 'menu_collapsed', 'roles')}),
    )
    filter_horizontal = UserAdmin.filter_horizontal

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('user_roles__role')

    @admin.display(description='角色')
    def role_list(self, obj):
        roles = [ur.role.name for ur in obj.user_roles.all()]
        return format_html(
            '<span style="font-size:12px">{}</span>',
            ' | '.join(roles) if roles else '-'
        )

    def get_form(self, request, obj=None, **kwargs):
        """使用自定义表单，支持角色多选"""
        kwargs['form'] = UserChangeForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 同步角色关联
        if 'roles' in form.cleaned_data:
            selected_roles = form.cleaned_data['roles']
            current_role_ids = set(UserRole.objects.filter(user=obj).values_list('role_id', flat=True))
            new_role_ids = {r.id for r in selected_roles}
            # 删除取消的角色
            to_remove = current_role_ids - new_role_ids
            if to_remove:
                UserRole.objects.filter(user=obj, role_id__in=to_remove).delete()
            # 添加新角色
            to_add = new_role_ids - current_role_ids
            for role_id in to_add:
                UserRole.objects.create(user=obj, role_id=role_id)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'menu_type', 'path', 'permission', 'sort', 'is_visible', 'status']
    list_filter = ['menu_type', 'status', 'is_visible']
    search_fields = ['name', 'path', 'permission']
    list_editable = ['sort', 'is_visible', 'status']
    raw_id_fields = ['parent']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    form = RoleAdminForm
    list_display = ['name', 'code', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'code']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']
    raw_id_fields = ['user', 'role']
    readonly_fields = ['user', 'role', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True  # 允许删除，但不能新增/编辑


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['username', 'method', 'path', 'status_code', 'ip', 'duration_ms', 'created_at']
    list_filter = ['method', 'status_code']
    search_fields = ['username', 'path', 'ip']
    readonly_fields = [f.name for f in OperationLog._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['username', 'result', 'ip', 'browser', 'message', 'created_at']
    list_filter = ['result']
    search_fields = ['username', 'ip']
    readonly_fields = [f.name for f in LoginLog._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'model', 'created_at', 'updated_at']
    search_fields = ['title', 'user__username']
    raw_id_fields = ['user']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'content_short', 'tokens', 'created_at']
    list_filter = ['role']
    search_fields = ['content']
    raw_id_fields = ['session']

    def content_short(self, obj):
        text = obj.content[:60] + ('...' if len(obj.content) > 60 else '')
        return format_html('<span title="{}">{}</span>', obj.content[:200], text)
    content_short.short_description = '内容'
