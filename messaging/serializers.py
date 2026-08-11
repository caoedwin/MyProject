from rest_framework import serializers
from messaging.models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'title', 'content', 'category', 'category_display',
            'recipient', 'sender', 'sender_name',
            'is_read', 'read_at', 'created_at',
        ]
        read_only_fields = ['sender', 'read_at', 'created_at']

    def get_is_read(self, obj):
        """对当前用户的已读状态

        - 点对点消息：直接读 Message.is_read
        - 广播消息：查 MessageRead 是否存在当前用户的记录
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        if obj.recipient_id is None:
            # 广播：查 MessageRead
            return obj.read_records.filter(user=request.user).exists()
        # 点对点
        return obj.is_read
