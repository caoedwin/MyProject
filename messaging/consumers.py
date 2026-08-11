"""Channels WebSocket 消费者 - 实时消息推送"""
import logging
import traceback
from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger('messaging')


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """消息推送消费者 - 每个用户独立分组 user_{id}"""

    async def connect(self):
        try:
            user = self.scope.get('user')
            logger.info('WebSocket connect 尝试, user=%s, authenticated=%s', user, getattr(user, 'is_authenticated', False))
            if not user or not user.is_authenticated:
                await self.close(code=4001)
                return
            self.user_group = f'user_{user.id}'
            self.broadcast_group = 'broadcast'
            await self.channel_layer.group_add(self.user_group, self.channel_name)
            await self.channel_layer.group_add(self.broadcast_group, self.channel_name)
            await self.accept()
            logger.info('WebSocket 已连接 user=%s', user.username)
        except Exception as e:
            logger.error('WebSocket connect 异常: %s\n%s', e, traceback.format_exc())
            raise

    async def disconnect(self, code):
        try:
            if hasattr(self, 'user_group'):
                await self.channel_layer.group_discard(self.user_group, self.channel_name)
                await self.channel_layer.group_discard(self.broadcast_group, self.channel_name)
            logger.info('WebSocket 已断开 code=%s', code)
        except Exception as e:
            logger.error('WebSocket disconnect 异常: %s\n%s', e, traceback.format_exc())

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        """覆盖 receive 方法，添加调试日志"""
        try:
            logger.info('WebSocket receive 原始数据: text_data=%r, bytes_data=%r', text_data, bytes_data)
            await super().receive(text_data=text_data, bytes_data=bytes_data, **kwargs)
            logger.info('WebSocket receive 处理完成')
        except Exception as e:
            logger.error('WebSocket receive 异常: %s\n%s', e, traceback.format_exc())
            raise

    async def receive_json(self, content, **kwargs):
        """接收客户端消息（心跳 / ACK）"""
        try:
            logger.info('WebSocket 收到消息: %s', content)
            msg_type = content.get('type', 'ping')
            if msg_type == 'ping':
                await self.send_json({'type': 'pong', 'timestamp': content.get('timestamp')})
                logger.info('WebSocket 已发送 pong')
        except Exception as e:
            logger.error('WebSocket receive_json 异常: %s\n%s', e, traceback.format_exc())
            raise

    # ---------- 分组事件处理器（type 映射）----------

    async def notify_message(self, event):
        """推送业务消息（type=notify_message -> notify_message）"""
        await self.send_json({
            'type': 'message',
            'message': event['message'],
        })

    async def broadcast(self, event):
        """广播消息"""
        await self.send_json({
            'type': 'broadcast',
            'message': event['message'],
        })
