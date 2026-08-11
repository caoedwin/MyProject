"""操作日志中间件 - 自动记录请求/响应到数据库"""
import json
import time
import logging

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('system.operation')

# 不记录日志的路径前缀
EXCLUDE_PATHS = ('/admin/', '/static/', '/media/', '/favicon.ico', '/api/docs')
# 请求体最大记录长度
MAX_BODY_LENGTH = 5000


class OperationLogMiddleware(MiddlewareMixin):
    """记录接口调用日志（method/path/耗时/状态码/响应摘要）"""

    def process_request(self, request):
        request._start_time = time.time()
        # 缓存请求体（仅 JSON）
        request._log_body = ''
        if request.content_type and 'application/json' in request.content_type:
            try:
                raw = request.body
                if raw and len(raw) <= MAX_BODY_LENGTH:
                    request._log_body = raw.decode('utf-8', errors='ignore')
            except Exception:
                pass

    def process_response(self, request, response):
        try:
            path = request.path
            if any(path.startswith(p) for p in EXCLUDE_PATHS):
                return response

            duration_ms = int((time.time() - getattr(request, '_start_time', time.time())) * 1000)
            user = getattr(request, 'user', None)
            username = user.username if user and user.is_authenticated else ''

            # 响应摘要
            summary = ''
            if hasattr(response, 'content') and response.get('Content-Type', '').startswith('application/json'):
                try:
                    content = response.content.decode('utf-8', errors='ignore')
                    summary = content[:MAX_BODY_LENGTH]
                except Exception:
                    pass

            # 延迟导入避免循环引用
            from system.models import OperationLog
            OperationLog.objects.create(
                user=user if user and user.is_authenticated else None,
                username=username,
                method=request.method,
                path=path,
                query=request.META.get('QUERY_STRING', '')[:2000],
                body=getattr(request, '_log_body', ''),
                status_code=response.status_code,
                ip=_get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                duration_ms=duration_ms,
                response_summary=summary,
            )
        except Exception as e:
            logger.warning('记录操作日志失败: %s', e)
        return response


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
