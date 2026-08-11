"""验证 Vite 能否编译 SidebarItem.vue"""
import urllib.request
try:
    r = urllib.request.urlopen('http://localhost:5173/src/layout/components/SidebarItem.vue', timeout=5)
    body = r.read().decode('utf-8', errors='replace')
    print(f'Status: {r.status}')
    print(f'Length: {len(body)}')
    print(f'First 200 chars: {body[:200]}')
except Exception as e:
    print(f'Error: {e}')
