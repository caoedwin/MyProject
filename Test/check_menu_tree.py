"""测试 user-menus 接口返回的完整菜单树"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

import urllib.request
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='admin')
token = str(RefreshToken.for_user(user).access_token)

req = urllib.request.Request('http://127.0.0.1:8000/api/system/user-menus')
req.add_header('Authorization', f'Bearer {token}')

with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))

# 打印菜单树结构
print("=== 用户菜单树 ===")
for menu in data['data']['menus']:
    print(f"\n[顶级] id={menu['id']} name={menu['name']} path={menu['path']} component={menu['component']} menu_type={menu['menu_type']}")
    if menu.get('children'):
        for child in menu['children']:
            print(f"  └─[子级] id={child['id']} name={child['name']} path={child['path']} component={child['component']} menu_type={child['menu_type']}")
            if child.get('children'):
                for grandchild in child['children']:
                    print(f"      └─[孙级] id={grandchild['id']} name={grandchild['name']} path={grandchild['path']} component={grandchild['component']} menu_type={grandchild['menu_type']}")
