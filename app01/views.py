"""认证视图 - 登录 / 注册 / 登出 / 刷新 / 用户信息 / 偏好 / 修改密码 / 记住密码免登"""
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from app01.models import User
from app01.serializers import (
    LoginSerializer, RegisterSerializer, UserInfoSerializer,
    UpdatePreferenceSerializer, ChangePasswordSerializer, RememberLoginSerializer,
)
from system.utils import ok, fail

User = get_user_model()


class LoginView(APIView):
    """用户登录（JWT + 记住密码）"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(ok(serializer.validated_data, msg='登录成功'))


class RegisterView(APIView):
    """用户注册"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(ok(
            {'id': user.id, 'username': user.username},
            msg='注册成功'
        ))


class LogoutView(APIView):
    """登出 - 将 refresh token 加入黑名单"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return Response(ok(msg='已退出登录'))


class RememberLoginView(APIView):
    """记住密码 - 凭 remember_token 免密登录换取新 JWT"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RememberLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        remember_token = serializer.validated_data['remember_token']
        signer = TimestampSigner()
        try:
            user_pk = signer.unsign(
                remember_token,
                max_age=settings.REMEMBER_ME_DAYS * 24 * 3600,
            )
        except (BadSignature, SignatureExpired):
            return Response(fail(msg='记住密码已过期，请重新登录', code=401))

        try:
            user = User.objects.get(pk=user_pk, is_active=True)
        except User.DoesNotExist:
            return Response(fail(msg='用户不存在', code=401))

        if hasattr(user, 'status') and not user.is_active_status:
            return Response(fail(msg='账号已被停用', code=401))

        refresh = RefreshToken.for_user(user)
        return Response(ok({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserInfoSerializer(user).data,
        }, msg='登录成功'))


class UserInfoView(viewsets.GenericViewSet):
    """当前用户信息 / 修改偏好 / 修改密码"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        return Response(ok(UserInfoSerializer(request.user).data))

    @action(detail=False, methods=['patch'], url_path='preferences')
    def update_preferences(self, request):
        """更新菜单布局 / 收起状态（顶部 / 左侧）"""
        serializer = UpdatePreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if 'menu_mode' in serializer.validated_data:
            user.menu_mode = serializer.validated_data['menu_mode']
        if 'menu_collapsed' in serializer.validated_data:
            user.menu_collapsed = serializer.validated_data['menu_collapsed']
        user.save(update_fields=['menu_mode', 'menu_collapsed'])
        return Response(ok(UserInfoSerializer(user).data, msg='偏好已更新'))

    @action(detail=False, methods=['post'], url_path='password')
    def change_password(self, request):
        """修改密码"""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(fail(msg='原密码错误'))
        user.set_password(serializer.validated_data['new_password'])
        # 清除记住密码 token
        user.remember_token = ''
        user.remember_token_expires = None
        user.save(update_fields=['password', 'remember_token', 'remember_token_expires'])
        return Response(ok(msg='密码修改成功，请重新登录'))
