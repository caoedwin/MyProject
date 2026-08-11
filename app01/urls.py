from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app01.views import (
    LoginView, RegisterView, LogoutView, RememberLoginView, UserInfoView,
)

app_name = 'app01'

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('remember-login', RememberLoginView.as_view(), name='remember-login'),
    path('refresh', TokenRefreshView.as_view(), name='token-refresh'),
    # 用户信息 / 偏好 / 改密
    path('user', UserInfoView.as_view({'get': 'list'}), name='user-info'),
    path('user/preferences', UserInfoView.as_view({'patch': 'update_preferences'}), name='user-preferences'),
    path('user/password', UserInfoView.as_view({'post': 'change_password'}), name='user-password'),
]
