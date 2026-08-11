"""测试 AI 接口和系统管理接口"""
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
print(f'Token: {token[:50]}...')

def test_api(url, method='GET', data=None):
    """测试 API 接口"""
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    if data:
        req.data = json.dumps(data).encode('utf-8')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            body = resp.read().decode('utf-8')
            print(f'  [OK] {status}: {body[:300]}')
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f'  [FAIL] HTTP {e.code}: {body[:300]}')
        return False
    except Exception as e:
        print(f'  [FAIL] {type(e).__name__}: {e}')
        return False

print('\n=== 测试 AI 接口 ===')
test_api('http://127.0.0.1:8000/api/ai/chat')

print('\n=== 测试系统管理接口 ===')
# 测试系统管理的各个子接口
test_api('http://127.0.0.1:8000/api/system/menus/')
test_api('http://127.0.0.1:8000/api/system/roles/')
test_api('http://127.0.0.1:8000/api/system/users/')
test_api('http://127.0.0.1:8000/api/system/permissions/')
test_api('http://127.0.0.1:8000/api/system/logs/')

print('\n=== 测试消息接口 ===')
test_api('http://127.0.0.1:8000/api/messaging/messages/unread-count')
