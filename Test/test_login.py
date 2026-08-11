"""测试登录接口是否正常"""
import json
import urllib.request
import urllib.error

url = 'http://localhost:8000/api/auth/login'
data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode('utf-8')

try:
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = resp.read().decode('utf-8')
        with open('Test/login_result.txt', 'w', encoding='utf-8') as f:
            f.write(f'Status: {resp.status}\n')
            f.write(f'Response: {result[:2000]}\n')
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    with open('Test/login_result.txt', 'w', encoding='utf-8') as f:
        f.write(f'HTTP Error: {e.code}\n')
        f.write(f'Response: {body[:2000]}\n')
except Exception as e:
    with open('Test/login_result.txt', 'w', encoding='utf-8') as f:
        f.write(f'Exception: {e}\n')

print('Done - check Test/login_result.txt')
