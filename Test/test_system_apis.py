"""测试系统管理接口 - 不带斜杠"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

import urllib.request, urllib.error, json
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='admin')
token = str(RefreshToken.for_user(user).access_token)

def test_api(url):
    req = urllib.request.Request(url, method='GET')
    req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            print(f'  [OK] {resp.status}: {body[:200]}')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        # 提取关键信息
        if 'Page not found' in body:
            # 提取 URL pattern 信息
            import re
            patterns = re.findall(r'"([^"]*system[^"]*)"', body)
            print(f'  [FAIL] HTTP {e.code} - 404')
            if patterns:
                print(f'  可用 patterns: {patterns[:5]}')
        else:
            print(f'  [FAIL] HTTP {e.code}: {body[:200]}')
    except Exception as e:
        print(f'  [FAIL] {type(e).__name__}: {e}')

print('=== 测试系统管理接口（不带斜杠）===')
test_api('http://127.0.0.1:8000/api/system/menus')
test_api('http://127.0.0.1:8000/api/system/roles')
test_api('http://127.0.0.1:8000/api/system/operation-logs')
test_api('http://127.0.0.1:8000/api/system/login-logs')
test_api('http://127.0.0.1:8000/api/system/user-menus')

print('\n=== 测试 AI 接口（不带斜杠）===')
test_api('http://127.0.0.1:8000/api/ai/chat')
