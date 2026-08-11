"""删除系统管理菜单，添加 Django Admin 外链"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from system.models import Menu

# 删除系统管理及其所有子菜单
system_menu = Menu.objects.filter(id=2).first()
if system_menu:
    # 删除所有子菜单
    Menu.objects.filter(parent=system_menu).delete()
    # 删除父菜单
    system_menu.delete()
    print('[OK] 已删除系统管理菜单及其所有子菜单')
else:
    print('[SKIP] 系统管理菜单不存在')

# 检查是否已存在 Django Admin 菜单
admin_menu = Menu.objects.filter(name='后台管理').first()
if not admin_menu:
    Menu.objects.create(
        name='后台管理',
        menu_type=Menu.MenuType.MENU,
        path='/admin/',
        component='',
        icon='Setting',
        permission='',
        sort=100,
        is_visible=True,
        is_external=True,  # 外链
        require_auth=False,
        status=True,
    )
    print('[OK] 已创建 Django Admin 外链菜单')
else:
    print('[SKIP] Django Admin 菜单已存在')

# 显示剩余菜单
print('\n=== 当前菜单列表 ===')
for m in Menu.objects.all().order_by('sort', 'id'):
    print(f'id={m.id} name={m.name} path={m.path} type={m.menu_type} external={m.is_external}')
