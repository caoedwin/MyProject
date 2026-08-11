"""消息推送视图 - 发送 / 广播 / 我的消息 / 标记已读"""
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from messaging.models import Message, MessageRead
from messaging.serializers import MessageSerializer
from system.utils import ok, fail


class MessageViewSet(viewsets.ModelViewSet):
    """站内消息管理"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'is_read']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        # 我收到的（点对点） + 全员广播
        qs = Message.objects.filter(recipient=user) | Message.objects.filter(recipient__isnull=True)
        return qs.distinct().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response(ok(serializer.data))

    @action(detail=False, methods=['post'], url_path='send')
    def send(self, request):
        """发送消息给指定用户（异步推送 + 落库）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(sender=request.user)

        # 触发异步推送
        from tasks.tasks import send_notification
        send_notification.delay(
            user_id=message.recipient_id,
            title=message.title,
            content=message.content,
        )
        return Response(ok(MessageSerializer(message).data, msg='消息已发送'))

    @action(detail=False, methods=['post'], url_path='broadcast')
    def broadcast(self, request):
        """全员广播（仅超级管理员，异步推送）"""
        # 权限校验：仅超级管理员
        if not request.user.is_superuser:
            return Response(fail(msg='仅超级管理员可发送广播', code=403), status=403)

        title = request.data.get('title', '')
        content = request.data.get('content', '')
        if not title or not content:
            return Response(fail(msg='标题和内容不能为空'))
        message = Message.objects.create(
            title=title, content=content,
            category=Message.Category.SYSTEM,
            sender=request.user,
        )
        # 广播给所有在线用户分组
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        layer = get_channel_layer()
        try:
            async_to_sync(layer.group_send)('broadcast', {
                'type': 'broadcast',
                'message': {'title': title, 'content': content},
            })
        except Exception:
            pass
        return Response(ok({'id': message.id}, msg='广播已发送'))

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        """标记已读

        - 点对点消息：更新 Message.is_read
        - 广播消息：在 MessageRead 表为当前用户创建记录
        """
        message = self.get_object()

        if message.recipient_id is None:
            # 广播消息：upsert MessageRead 记录
            MessageRead.objects.get_or_create(
                user=request.user, message=message,
            )
            return Response(ok(msg='已标记已读'))

        # 点对点消息：校验接收人
        if message.recipient_id != request.user.id:
            return Response(fail(msg='无权操作', code=403), status=403)
        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save(update_fields=['is_read', 'read_at'])
        return Response(ok(msg='已标记已读'))

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """未读消息数 = 未读点对点 + 未读广播"""
        user = request.user
        # 未读点对点消息
        unread_direct = Message.objects.filter(recipient=user, is_read=False).count()
        # 未读广播 = 全部广播 - 我已读的广播
        all_broadcasts = Message.objects.filter(recipient__isnull=True)
        read_broadcast_ids = MessageRead.objects.filter(user=user).values_list('message_id', flat=True)
        unread_broadcast = all_broadcasts.exclude(id__in=read_broadcast_ids).count()

        return Response(ok({'unread': unread_direct + unread_broadcast}))
