"""Channels WebSocket 鉴权中间件 - 从 query/cookie/header 读取 JWT"""
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


@database_sync_to_async
def _get_user(user_id):
    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        return None


class JwtAuthMiddleware:
    """解析 query 参数 token=xxx 或 Authorization 头中的 JWT"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        token = None

        # 1. query 参数
        qs = parse_qs(scope.get('query_string', b'').decode())
        token = qs.get('token', [None])[0]

        # 2. 子协议（可选）
        if not token and scope.get('subprotocols'):
            for proto in scope['subprotocols']:
                if proto.startswith('jwt.'):
                    token = proto[4:]
                    break

        # 3. Authorization 头
        if not token:
            for header in scope.get('headers', []):
                if header[0] == b'authorization':
                    val = header[1].decode()
                    if val.startswith('Bearer '):
                        token = val[7:]
                    break

        if token:
            try:
                access = AccessToken(token)
                user = await _get_user(access['user_id'])
                if user:
                    scope['user'] = user
            except (InvalidToken, TokenError):
                scope['user'] = None
        else:
            scope['user'] = None

        return await self.app(scope, receive, send)
