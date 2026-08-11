from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型 - 支持前后端分离 + JWT 认证"""

    # 性别 choices
    class Gender(models.IntegerChoices):
        MALE = 1, '男'
        FEMALE = 2, '女'
        UNKNOWN = 0, '未知'

    # 账号状态 choices
    class Status(models.IntegerChoices):
        ACTIVE = 1, '正常'
        DISABLED = 0, '禁用'

    nickname = models.CharField('昵称', max_length=50, blank=True)
    avatar = models.URLField('头像', max_length=500, blank=True)
    phone = models.CharField('手机号', max_length=20, blank=True)
    email = models.EmailField('邮箱', blank=True)
    gender = models.IntegerField(
        '性别', choices=Gender.choices, default=Gender.UNKNOWN
    )
    status = models.IntegerField(
        '状态', choices=Status.choices, default=Status.ACTIVE
    )
    # 记住密码：加密保存的凭据 token（非明文密码），前端 remember-me 时使用
    remember_token = models.CharField('记住密码Token', max_length=255, blank=True)
    remember_token_expires = models.DateTimeField('Token过期时间', null=True, blank=True)
    last_login_ip = models.GenericIPAddressField('最后登录IP', null=True, blank=True)

    # 用户偏好：菜单模式（top=顶部 / side=左侧），收起状态
    menu_mode = models.CharField(
        '菜单布局', max_length=10, default='side',
        help_text='top=顶部菜单 / side=左侧菜单'
    )
    menu_collapsed = models.BooleanField('菜单是否收起', default=False)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.username

    @property
    def is_active_status(self):
        """业务状态是否可用（与 Django is_active 解耦）"""
        return self.status == self.Status.ACTIVE
