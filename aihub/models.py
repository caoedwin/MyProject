"""AI 对话历史记录 - 持久化用户会话"""
from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """对话会话"""
    title = models.CharField('会话标题', max_length=200, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='chat_sessions', verbose_name='用户'
    )
    model = models.CharField('模型', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'ai_chat_session'
        verbose_name = 'AI会话'
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    """对话消息"""

    class Role(models.IntegerChoices):
        SYSTEM = 0, 'system'
        USER = 1, 'user'
        ASSISTANT = 2, 'assistant'

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE,
        related_name='messages', verbose_name='会话'
    )
    role = models.IntegerField('角色', choices=Role.choices)
    content = models.TextField('内容')
    tokens = models.IntegerField('Token数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'ai_chat_message'
        verbose_name = 'AI消息'
        verbose_name_plural = verbose_name
        ordering = ['created_at']
