"""测试登录逻辑 - 结果写入文件"""
import traceback
import sys

output = []
def log(msg):
    output.append(str(msg))

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
        log('LOGIN OK')
        data = serializer.validated_data
        log(f'Keys: {list(data.keys())}')
        user = data.get('user', {})
        log(f'User info keys: {list(user.keys()) if isinstance(user, dict) else "N/A"}')
    else:
        log(f'VALIDATION ERROR: {serializer.errors}')
except Exception:
    log('EXCEPTION during login:')
    log(traceback.format_exc())

with open('Test/login_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
