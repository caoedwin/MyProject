from django.contrib import admin

from messaging.models import Message, MessageRead


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'recipient', 'sender', 'is_read', 'created_at')
    list_filter = ('category', 'is_read')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    list_per_page = 20


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__username', 'message__title')
    list_per_page = 20
