"""测试 Redis channel layer 是否正常工作"""
import os, sys, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from channels.layers import get_channel_layer

async def test():
    layer = get_channel_layer()
    print(f'Channel layer type: {type(layer).__name__}')
    print(f'Channel layer config: {layer}')

    try:
        # 测试 group_add
        print('\n测试 group_add...')
        await layer.group_add('test_group', 'test_channel')
        print('[OK] group_add 成功')

        # 测试 group_send
        print('测试 group_send...')
        await layer.group_send('test_group', {
            'type': 'test.message',
            'message': 'hello'
        })
        print('[OK] group_send 成功')

        # 测试 group_discard
        print('测试 group_discard...')
        await layer.group_discard('test_group', 'test_channel')
        print('[OK] group_discard 成功')

        print('\n所有 channel layer 测试通过!')

    except Exception as e:
        print(f'\n[FAIL] {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())
