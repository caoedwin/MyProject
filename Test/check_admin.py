"""验证 Django admin 可访问"""
import urllib.request
try:
    r = urllib.request.urlopen('http://127.0.0.1:8000/admin/', timeout=5)
    print(f'Status: {r.status}')
    print(f'Title check: {"admin" in r.read().decode("utf-8", errors="replace").lower()}')
except Exception as e:
    print(f'Error: {e}')
