"""检查菜单配置和对应的视图文件"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from system.models import Menu

menus = Menu.objects.all().order_by('id')
print('=== 数据库中的菜单配置 ===')
for m in menus:
    print(f'id={m.id} name={m.name} path={m.path} component={m.component} type={m.menu_type} parent={m.parent_id}')

# 检查前端视图文件
print('\n=== 检查前端视图文件 ===')
views_dir = r'c:\djangoproject\MyProject\frontend\src\views'
for m in menus:
    if m.component:
        # 菜单配置的 component 格式如 'system/user/index'
        file_path = os.path.join(views_dir, m.component.replace('/', os.sep) + '.vue')
        exists = os.path.exists(file_path)
        status = '[OK]' if exists else '[MISSING]'
        print(f'{status} {m.component} -> {file_path}')
