"""系统管理后台注册 - RBAC + 用户 + 日志"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from app01.models import User
from system.models import Menu, Role, UserRole, OperationLog, LoginLog
from aihub.models import ChatSession, ChatMessage


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'nickname', 'phone', 'status', 'menu_mode', 'menu_collapsed', 'is_superuser', 'last_login']
    list_filter = ['status', 'is_superuser', 'menu_mode', 'gender']
    search_fields = ['username', 'nickname', 'phone', 'email']
    list_editable = ['status', 'menu_mode', 'menu_collapsed']
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('nickname', 'avatar', 'phone', 'gender', 'status',
                                'remember_token', 'remember_token_expires', 'last_login_ip',
                                'menu_mode', 'menu_collapsed')}),
    )
    filter_horizontal = UserAdmin.filter_horizontal


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'menu_type', 'path', 'permission', 'sort', 'is_visible', 'status']
    list_filter = ['menu_type', 'status', 'is_visible']
    search_fields = ['name', 'path', 'permission']
    list_editable = ['sort', 'is_visible', 'status']
    raw_id_fields = ['parent']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'code']
    filter_horizontal = ['menus', 'permissions']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']
    raw_id_fields = ['user', 'role']


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
