"""统一异常处理 - DRF 异常转换为标准 JSON 响应"""
import logging

from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    AuthenticationFailed, NotAuthenticated, PermissionDenied,
    ValidationError, Throttled,
)
from rest_framework import status as http_status

from system.utils import fail

logger = logging.getLogger('system.operation')


def custom_exception_handler(exc, context):
    """将 DRF / Django 异常统一转换为 {code, msg, success} 结构"""
    response = exception_handler(exc, context)

    # DRF 已处理的异常（有 response）
    if response is not None:
        code = response.status_code
        data = response.data
        if isinstance(data, dict):
            msg = data.get('detail') or data.get('message') or next(
                (v for v in data.values() if isinstance(v, (str, list))), 'error'
            )
            if isinstance(msg, list):
                msg = '; '.join(str(m) for m in msg)
        elif isinstance(data, list):
            msg = '; '.join(str(m) for m in data)
        else:
            msg = str(data)

        # 认证类异常归一到 401
        if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            code = 401
            msg = '登录已过期或未登录，请重新登录'
        elif isinstance(exc, PermissionDenied):
            code = 403
            msg = '没有访问权限'
        elif isinstance(exc, ValidationError):
            code = 422
        elif isinstance(exc, Throttled):
            code = 429
            msg = f'请求过于频繁，请 {exc.wait} 秒后重试'

        response.data = fail(msg=str(msg), code=code)
        response.status_code = http_status.HTTP_200_OK  # 业务层用 code 区分
        return response

    # 未被 DRF 捕获的异常
    logger.exception('未处理异常: %s', exc)
    return fail(msg='服务器内部错误', code=500, err=str(exc))
