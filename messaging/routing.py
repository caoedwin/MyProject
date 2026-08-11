"""Channels WebSocket 路由"""
from django.urls import path
from channels.routing import URLRouter

from messaging.consumers import NotificationConsumer

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]

application = URLRouter(websocket_urlpatterns)
