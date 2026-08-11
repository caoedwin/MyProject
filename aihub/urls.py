from django.urls import path, include
from rest_framework.routers import DefaultRouter

from aihub.views import ChatViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'chat', ChatViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
]
