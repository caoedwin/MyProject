"""初始化系统数据：超级管理员 + 角色 + 菜单 + 权限"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from app01.models import User
from system.models import Menu, Role, UserRole

User = get_user_model()


class Command(BaseCommand):
    help = '初始化系统基础数据（超级管理员、角色、菜单、权限）'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('开始初始化系统数据...'))

        # 1. 超级管理员
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'nickname': '超级管理员',
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
                'status': User.Status.ACTIVE,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('[OK] 创建超级管理员 admin/admin123'))
        else:
            self.stdout.write('  超级管理员已存在，跳过')

        # 2. 角色
        admin_role, _ = Role.objects.get_or_create(
            code='admin',
            defaults={'name': '系统管理员', 'remark': '拥有所有权限', 'status': True}
        )
        user_role, _ = Role.objects.get_or_create(
            code='user',
            defaults={'name': '普通用户', 'remark': '基础查看权限', 'status': True}
        )
        self.stdout.write(self.style.SUCCESS('[OK] 角色初始化完成'))

        # 3. 菜单（目录 + 菜单 + 按钮）
        menus_data = [
            # ---- 仪表盘 ----
            {'name': '仪表盘', 'path': '/dashboard', 'component': 'dashboard/index',
             'icon': 'Odometer', 'menu_type': Menu.MenuType.MENU, 'sort': 1,
             'permission': ''},
            # ---- 系统管理 ----
            {'name': '系统管理', 'path': '/system', 'icon': 'Setting',
             'menu_type': Menu.MenuType.DIRECTORY, 'sort': 90, 'children': [
                {'name': '用户管理', 'path': '/system/user', 'component': 'system/user/index',
                 'icon': 'User', 'menu_type': Menu.MenuType.MENU,
                 'permission': 'system:user_list', 'sort': 1,
                 'buttons': [
                     {'name': '新增', 'permission': 'system:user_add'},
                     {'name': '编辑', 'permission': 'system:user_edit'},
                     {'name': '删除', 'permission': 'system:user_delete'},
                 ]},
                {'name': '角色管理', 'path': '/system/role', 'component': 'system/role/index',
                 'icon': 'UserFilled', 'menu_type': Menu.MenuType.MENU,
                 'permission': 'system:role', 'sort': 2},
                {'name': '菜单管理', 'path': '/system/menu', 'component': 'system/menu/index',
                 'icon': 'Menu', 'menu_type': Menu.MenuType.MENU,
                 'permission': 'system:menu', 'sort': 3},
                {'name': '操作日志', 'path': '/system/operation-log',
                 'component': 'system/operation_log/index', 'icon': 'Document',
                 'menu_type': Menu.MenuType.MENU, 'permission': 'system:operation_log', 'sort': 4},
                {'name': '登录日志', 'path': '/system/login-log',
                 'component': 'system/login_log/index', 'icon': 'Histogram',
                 'menu_type': Menu.MenuType.MENU, 'permission': 'system:login_log', 'sort': 5},
            ]},
            # ---- 消息中心 ----
            {'name': '消息中心', 'path': '/message', 'component': 'message/index',
             'icon': 'Bell', 'menu_type': Menu.MenuType.MENU, 'sort': 80,
             'permission': 'messaging:message'},
            # ---- AI 助手 ----
            {'name': 'AI 助手', 'path': '/ai', 'component': 'ai/index',
             'icon': 'ChatDotRound', 'menu_type': Menu.MenuType.MENU, 'sort': 85,
             'permission': 'aihub:chat'},
        ]

        created_count = 0
        for item in menus_data:
            created_count += _create_menu(item)
        self.stdout.write(self.style.SUCCESS(f'[OK] 菜单初始化完成（新增 {created_count} 条）'))

        # 4. 给 admin 角色挂载所有菜单
        admin_role.menus.set(Menu.objects.all())
        admin_role.permissions.set(Permission.objects.all())
        self.stdout.write(self.style.SUCCESS('[OK] 管理员角色权限已分配'))

        # 5. admin 用户绑定 admin 角色
        UserRole.objects.get_or_create(user=admin, role=admin_role)
        self.stdout.write(self.style.SUCCESS('[OK] admin 用户已绑定管理员角色'))

        self.stdout.write(self.style.SUCCESS('\n=== 初始化完成 ==='))
        self.stdout.write('Super admin: admin')
        self.stdout.write('Password: admin123')
        self.stdout.write('Please change password after login!')


def _create_menu(data, parent=None):
    """递归创建菜单"""
    count = 0
    children = data.pop('children', [])
    buttons = data.pop('buttons', [])
    data['parent'] = parent

    menu, created = Menu.objects.get_or_create(
        name=data['name'],
        defaults={**data, 'is_visible': True, 'status': True}
    )
    if created:
        count += 1

    for child in children:
        count += _create_menu(child, parent=menu)

    for btn in buttons:
        _, c = Menu.objects.get_or_create(
            name=btn['name'], parent=menu,
            defaults={
                'menu_type': Menu.MenuType.BUTTON,
                'permission': btn['permission'],
                'is_visible': False,
                'status': True,
                'sort': 0,
            }
        )
        if c:
            count += 1
    return count
