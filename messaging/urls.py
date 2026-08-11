from django.urls import path, include
from rest_framework.routers import DefaultRouter

from messaging.views import MessageViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
]
