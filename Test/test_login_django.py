"""通过 Django 环境直接测试登录序列化器，捕获具体异常"""
import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app01.serializers import LoginSerializer

class FakeRequest:
    META = {
        'HTTP_USER_AGENT': 'test-agent',
        'REMOTE_ADDR': '127.0.0.1',
    }
    data = {}

try:
    serializer = LoginSerializer(
        data={'username': 'admin', 'password': 'admin123'},
        context={'request': FakeRequest()}
    )
    if serializer.is_valid():
        print('LOGIN OK')
        data = serializer.validated_data
        # 不打印 token 全文，只看 key
        print('Keys:', list(data.keys()))
        print('User info keys:', list(data.get('user', {}).keys()) if isinstance(data.get('user'), dict) else 'N/A')
    else:
        print('VALIDATION ERROR:', serializer.errors)
except Exception:
    print('EXCEPTION during login:')
    traceback.print_exc()
