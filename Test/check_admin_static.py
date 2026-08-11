"""验证 admin 页面静态资源"""
import urllib.request

# 1. admin 登录页
try:
    r = urllib.request.urlopen('http://127.0.0.1:8000/admin/login/', timeout=5)
    body = r.read().decode('utf-8', errors='replace')
    print(f'[admin/login] Status: {r.status}, Length: {len(body)}')
    print(f'  Has CSS link: {"stylesheet" in body.lower()}')
except Exception as e:
    print(f'[admin/login] Error: {e}')

# 2. 通过 Vite 代理访问
try:
    r = urllib.request.urlopen('http://localhost:5173/admin/login/', timeout=5)
    body = r.read().decode('utf-8', errors='replace')
    print(f'[vite/admin/login] Status: {r.status}, Length: {len(body)}')
except Exception as e:
    print(f'[vite/admin/login] Error: {e}')

# 3. 测试静态文件
try:
    r = urllib.request.urlopen('http://localhost:5173/static/admin/css/base.css', timeout=5)
    print(f'[static/admin/css/base.css] Status: {r.status}, Length: {len(r.read())}')
except Exception as e:
    print(f'[static/admin/css/base.css] Error: {e}')
