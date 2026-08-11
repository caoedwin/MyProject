"""示例异步任务 - 演示 Celery 用法，业务任务可在本 app 内扩展"""
import logging
from celery import shared_task

logger = logging.getLogger('tasks')


@shared_task(bind=True, name='tasks.debug_echo')
def debug_echo(self, message: str = ''):
    """调试任务：回显消息"""
    logger.info('debug_echo 收到消息: %s', message)
    return {'echo': message, 'task_id': self.request.id}


@shared_task(name='tasks.send_notification')
def send_notification(user_id: int, title: str, content: str):
    """发送站内消息推送（通过 Channels layer 广播）"""
    import asyncio
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'notify_message',
            'message': {
                'title': title,
                'content': content,
                'category': 'notification',
            },
        },
    )
    logger.info('通知已推送 user=%s title=%s', user_id, title)
    return {'user_id': user_id, 'title': title, 'sent': True}


@shared_task(name='tasks.cleanup_logs')
def cleanup_logs(retain_days: int = 30):
    """定时清理过期日志（配合 django-celery-beat 调度）"""
    from datetime import timedelta
    from django.utils import timezone
    from system.models import OperationLog, LoginLog

    cutoff = timezone.now() - timedelta(days=retain_days)
    op_deleted, _ = OperationLog.objects.filter(created_at__lt=cutoff).delete()
    login_deleted, _ = LoginLog.objects.filter(created_at__lt=cutoff).delete()
    logger.info('日志清理完成: 操作日志 %d 条, 登录日志 %d 条', op_deleted, login_deleted)
    return {'operation_logs': op_deleted, 'login_logs': login_deleted}
