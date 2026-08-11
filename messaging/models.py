from django.db import models
from django.conf import settings


class Message(models.Model):
    """站内消息记录 - 用于消息推送历史查询"""

    class Category(models.IntegerChoices):
        SYSTEM = 1, '系统'
        NOTIFICATION = 2, '通知'
        TASK = 3, '任务'
        AI = 4, 'AI'

    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    category = models.IntegerField('类型', choices=Category.choices, default=Category.NOTIFICATION)
    # 接收人（null 表示全员广播）
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='messages', verbose_name='接收人'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sent_messages', verbose_name='发送人'
    )
    # 仅对点对点消息有效；广播消息的已读状态见 MessageRead
    is_read = models.BooleanField('是否已读', default=False)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_message'
        verbose_name = '站内消息'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class MessageRead(models.Model):
    """广播消息的逐用户已读记录

    广播消息(recipient=null)被所有用户共享，无法在 Message 表上记录
    每个用户的已读状态，因此用本表为「用户 × 广播消息」建立独立记录。
    点对点消息不需要此表（直接用 Message.is_read）。
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='broadcast_reads', verbose_name='用户'
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE,
        related_name='read_records', verbose_name='消息'
    )
    read_at = models.DateTimeField('阅读时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_message_read'
        verbose_name = '广播已读记录'
        verbose_name_plural = verbose_name
        unique_together = [('user', 'message')]
        ordering = ['-read_at']

    def __str__(self):
        return f'{self.user_id} read {self.message_id}'

