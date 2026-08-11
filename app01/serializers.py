"""认证序列化器 - 登录 / 注册 / 用户信息 / 记住密码"""
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from app01.models import User
from system.models import LoginLog

User = get_user_model()


class LoginSerializer(TokenObtainPairSerializer):
    """登录序列化器 - 扩展 JWT，支持记住密码 + 登录日志"""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    remember_me = serializers.BooleanField(default=False, write_only=True)
    captcha = serializers.CharField(required=False, allow_blank=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 在 token 中附加额外信息
        token['username'] = user.username
        token['nickname'] = user.nickname or user.username
        token['is_superuser'] = user.is_superuser
        return token

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        remember_me = attrs.get('remember_me', False)
        request = self.context.get('request')

        # 登录失败次数限制（Redis）
        from django.core.cache import cache
        lock_key = f'login_lock:{username}'
        attempt_key = f'login_attempt:{username}'
        if cache.get(lock_key):
            raise serializers.ValidationError('账号已被锁定，请稍后再试')

        user = authenticate(request=request, username=username, password=password)
        if not user:
            # 记录失败次数
            attempts = cache.get(attempt_key, 0) + 1
            cache.set(attempt_key, attempts, settings.LOGIN_ATTEMPT_WINDOW)
            if attempts >= settings.LOGIN_ATTEMPT_LIMIT:
                cache.set(lock_key, 1, settings.LOGIN_LOCK_DURATION)
                _record_login_log(username, request, False, '账号锁定')
                raise serializers.ValidationError('密码错误次数过多，账号已被锁定')
            _record_login_log(username, request, False, f'密码错误({attempts}/{settings.LOGIN_ATTEMPT_LIMIT})')
            raise serializers.ValidationError(f'用户名或密码错误（剩余 {settings.LOGIN_ATTEMPT_LIMIT - attempts} 次）')

        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')
        if hasattr(user, 'status') and not user.is_active_status:
            raise serializers.ValidationError('账号已被停用，请联系管理员')

        # 清除失败计数
        cache.delete(attempt_key)
        cache.delete(lock_key)

        # 生成 token
        refresh = self.get_token(user)

        # 记住密码：生成独立的 remember_token（非明文密码，仅用于延长刷新有效期）
        remember_token = ''
        if remember_me:
            from django.core.signing import TimestampSigner
            signer = TimestampSigner()
            remember_token = signer.sign(user.pk)
            user.remember_token = remember_token
            user.remember_token_expires = timezone.now() + timedelta(days=settings.REMEMBER_ME_DAYS)
            # 记住密码时，刷新 token 有效期延长
            refresh.set_exp(lifetime=timedelta(days=settings.REMEMBER_ME_DAYS))

        # 更新登录信息
        ip = _get_client_ip(request)
        user.last_login = timezone.now()
        user.last_login_ip = ip
        user.save(update_fields=['last_login', 'last_login_ip', 'remember_token', 'remember_token_expires'])

        _record_login_log(username, request, True, '登录成功', user=user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'remember_token': remember_token,
            'user': UserInfoSerializer(user).data,
        }


class RegisterSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'nickname', 'email', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '两次密码不一致'})
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': '用户名已存在'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.status = User.Status.ACTIVE
        user.save()
        return user


class UserInfoSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'nickname', 'avatar', 'email', 'phone',
            'gender', 'status', 'is_superuser', 'menu_mode', 'menu_collapsed',
            'date_joined', 'last_login', 'roles', 'permissions',
        ]

    def get_roles(self, obj):
        return [{'id': ur.role.id, 'name': ur.role.name, 'code': ur.role.code}
                for ur in obj.user_roles.select_related('role')]

    def get_permissions(self, obj):
        from system.permissions import get_user_permissions
        return list(get_user_permissions(obj))


class UpdatePreferenceSerializer(serializers.Serializer):
    """用户偏好设置 - 菜单布局 / 收起状态"""
    menu_mode = serializers.ChoiceField(choices=['top', 'side'], required=False)
    menu_collapsed = serializers.BooleanField(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)


class RememberLoginSerializer(serializers.Serializer):
    """记住密码 - 免登录（用 remember_token 换取新 token）"""
    remember_token = serializers.CharField()


def _get_client_ip(request):
    if not request:
        return None
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _record_login_log(username, request, success, message, user=None):
    try:
        LoginLog.objects.create(
            username=username,
            ip=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500] if request else '',
            result=LoginLog.Result.SUCCESS if success else LoginLog.Result.FAILED,
            message=message,
        )
    except Exception:
        pass
