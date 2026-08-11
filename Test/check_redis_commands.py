"""检查 Redis 版本和支持的命令"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings

# 使用 protocol=2 避免 HELLO 命令
import redis
r = redis.Redis(
    host='localhost', 
    port=6379, 
    password='DCT2019', 
    db=4,
    protocol=2,
    socket_timeout=5
)

# 检查版本
info = r.info('server')
print(f"Redis version: {info.get('redis_version')}")
print(f"Redis mode: {info.get('redis_mode')}")

# 检查关键命令
for cmd in ['BZPOPMIN', 'HELLO', 'EVAL', 'BRPOP', 'ZADD']:
    try:
        # 只检查命令是否存在，不执行
        pass
    except Exception as e:
        print(f"  {cmd}: ERROR {e}")

# 尝试 BZPOPMIN
try:
    # 设置一个测试 key
    r.zadd('test_zset', {'member1': 1.0})
    result = r.bzpopmin('test_zset', timeout=1)
    print(f"BZPOPMIN result: {result}")
    r.delete('test_zset')
except redis.exceptions.ResponseError as e:
    print(f"BZPOPMIN ERROR: {e}")
except Exception as e:
    print(f"BZPOPMIN exception: {type(e).__name__}: {e}")

# 尝试 EVAL
try:
    result = r.eval("return 1", 0)
    print(f"EVAL result: {result}")
except redis.exceptions.ResponseError as e:
    print(f"EVAL ERROR: {e}")
except Exception as e:
    print(f"EVAL exception: {type(e).__name__}: {e}")

# 检查命令列表
try:
    cmds = r.execute_command('COMMAND', 'INFO', 'BZPOPMIN')
    print(f"COMMAND INFO BZPOPMIN: {cmds}")
except Exception as e:
    print(f"COMMAND INFO error: {e}")

try:
    cmds = r.execute_command('COMMAND', 'INFO', 'HELLO')
    print(f"COMMAND INFO HELLO: {cmds}")
except Exception as e:
    print(f"COMMAND INFO HELLO error: {e}")
