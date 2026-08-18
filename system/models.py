from django.db import models
from django.conf import settings


class Menu(models.Model):
    """菜单 / 权限树 - 同时承担「菜单展示」和「权限标识」职责"""

    class MenuType(models.IntegerChoices):
        DIRECTORY = 0, '目录'   # 含子菜单的父级
        MENU = 1, '菜单'        # 具体页面
        BUTTON = 2, '按钮'      # 页面内操作权限（不在菜单展示）

    name = models.CharField('名称', max_length=50)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name='父级菜单'
    )
    menu_type = models.IntegerField(
        '类型', choices=MenuType.choices, default=MenuType.MENU
    )
    # 前端路由 path（如 /system/user）与组件路径（如 system/user/index）
    path = models.CharField('路由地址', max_length=200, blank=True)
    component = models.CharField('组件路径', max_length=200, blank=True)
    redirect = models.CharField('重定向', max_length=200, blank=True)
    icon = models.CharField('图标', max_length=100, blank=True)
    # 权限标识，格式 app:action（如 system:user_list），按钮类型必填
    permission = models.CharField('权限标识', max_length=100, blank=True, db_index=True)
    sort = models.IntegerField('排序', default=0)
    is_visible = models.BooleanField('是否显示', default=True)
    # 外链
    is_external = models.BooleanField('是否外链', default=False)
    # 守卫：是否需要登录 / 是否常驻（所有登录用户可见）
    require_auth = models.BooleanField('需要登录', default=True)
    status = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_menu'
        verbose_name = '菜单权限'
        verbose_name_plural = verbose_name
        ordering = ['sort', 'id']

    def __str__(self):
        return f'{self.name} ({self.get_menu_type_display()})'

    def get_ancestor_ids(self):
        """返回所有祖先菜单 ID 列表（含自身）"""
        ids = [self.id]
        parent = self.parent
        while parent:
            ids.append(parent.id)
            parent = parent.parent
        return ids

    @staticmethod
    def expand_ancestors(menu_ids):
        """给定一组菜单 ID，自动补全所有祖先菜单 ID"""
        if not menu_ids:
            return set()
        result = set(menu_ids)
        menus = Menu.objects.filter(id__in=menu_ids).select_related('parent__parent__parent')
        for menu in menus:
            result.update(menu.get_ancestor_ids())
        return result


class Role(models.Model):
    """角色 - 对应 Django auth Group 的业务封装，挂载菜单/权限"""

    name = models.CharField('角色名称', max_length=50, unique=True)
    code = models.CharField('角色编码', max_length=50, unique=True)
    menus = models.ManyToManyField(
        Menu, blank=True, related_name='roles', verbose_name='关联菜单'
    )
    # 关联 Django 权限（细粒度按钮权限）
    permissions = models.ManyToManyField(
        'auth.Permission', blank=True, related_name='roles', verbose_name='关联权限'
    )
    remark = models.CharField('备注', max_length=200, blank=True)
    status = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_role'
        verbose_name = '角色'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """用户-角色关联"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='user_roles', verbose_name='用户'
    )
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE,
        related_name='role_users', verbose_name='角色'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_user_role'
        verbose_name = '用户角色'
        verbose_name_plural = verbose_name
        unique_together = [('user', 'role')]


class OperationLog(models.Model):
    """操作日志 - 由中间件自动记录"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='operation_logs', verbose_name='操作人'
    )
    username = models.CharField('用户名', max_length=150, blank=True)
    method = models.CharField('请求方法', max_length=10)
    path = models.CharField('请求路径', max_length=500)
    query = models.TextField('查询参数', blank=True)
    body = models.TextField('请求体', blank=True)
    status_code = models.IntegerField('响应状态码', default=0)
    ip = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.CharField('User-Agent', max_length=500, blank=True)
    duration_ms = models.IntegerField('耗时(ms)', default=0)
    response_summary = models.TextField('响应摘要', blank=True)
    error_msg = models.TextField('错误信息', blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.username} {self.method} {self.path}'


class LoginLog(models.Model):
    """登录日志"""

    class Result(models.IntegerChoices):
        SUCCESS = 1, '成功'
        FAILED = 0, '失败'

    username = models.CharField('用户名', max_length=150)
    ip = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.CharField('User-Agent', max_length=500, blank=True)
    location = models.CharField('登录位置', max_length=100, blank=True)
    browser = models.CharField('浏览器', max_length=100, blank=True)
    result = models.IntegerField('结果', choices=Result.choices, default=Result.SUCCESS)
    message = models.CharField('提示', max_length=200, blank=True)
    created_at = models.DateTimeField('登录时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_login_log'
        verbose_name = '登录日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.username} {self.get_result_display()}'
