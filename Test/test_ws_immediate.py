"""测试 WebSocket - 连接后立即发送消息"""
import os, sys, asyncio, json
import websockets

sys.stdout.reconfigure(line_buffering=True)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='admin')
token = str(RefreshToken.for_user(user).access_token)
print(f'Token: {token[:50]}...', flush=True)

async def test_immediate():
    """连接后立即发送 ping"""
    print("\n=== 测试: 连接后立即发送 ping ===", flush=True)
    uri = f'ws://127.0.0.1:8000/ws/notifications/?token={token}'
    try:
        async with websockets.connect(uri, origin='http://localhost:5173') as ws:
            print('[OK] WebSocket 连接成功!', flush=True)
            # 立即发送
            await ws.send(json.dumps({"type": "ping", "timestamp": 123}))
            print('[OK] ping 已发送, 等待响应...', flush=True)
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f'[OK] 收到响应: {msg}', flush=True)
    except websockets.exceptions.InvalidStatus as e:
        print(f'[FAIL] HTTP {e.response.status_code} {e.response.reason_phrase}', flush=True)
        body = e.response.body
        if body:
            print(f'  响应体: {body.decode("utf-8", errors="replace")[:300]}', flush=True)
    except Exception as e:
        print(f'[FAIL] {type(e).__name__}: {e}', flush=True)
        import traceback
        traceback.print_exc()

async def test_wait_1s():
    """连接后等待 1 秒再发送"""
    print("\n=== 测试: 连接后等待 1 秒再发送 ping ===", flush=True)
    uri = f'ws://127.0.0.1:8000/ws/notifications/?token={token}'
    try:
        async with websockets.connect(uri, origin='http://localhost:5173') as ws:
            print('[OK] WebSocket 连接成功!', flush=True)
            await asyncio.sleep(1)
            print('[OK] 1 秒后, 尝试发送 ping...', flush=True)
            await ws.send(json.dumps({"type": "ping", "timestamp": 123}))
            print('[OK] ping 已发送, 等待响应...', flush=True)
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f'[OK] 收到响应: {msg}', flush=True)
    except websockets.exceptions.InvalidStatus as e:
        print(f'[FAIL] HTTP {e.response.status_code} {e.response.reason_phrase}', flush=True)
    except Exception as e:
        print(f'[FAIL] {type(e).__name__}: {e}', flush=True)
        import traceback
        traceback.print_exc()

async def main():
    await test_immediate()
    await test_wait_1s()

asyncio.run(main())
print('[DONE] 测试结束', flush=True)
