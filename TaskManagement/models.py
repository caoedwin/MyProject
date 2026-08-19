"""任务管理子系统 - 数据模型"""
from django.conf import settings
from django.db import models


class TaskCategory(models.Model):
    """任务种类"""

    name = models.CharField('种类名称', max_length=50, unique=True)
    code = models.CharField('种类编码', max_length=50, unique=True)
    description = models.TextField('描述', blank=True)
    has_benefit = models.BooleanField('是否有效益', default=False,
        help_text='该种类任务是否需要填写效益/积分')
    sort = models.IntegerField('排序', default=0)
    status = models.BooleanField('启用', default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_categories',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'task_category'
        verbose_name = '任务种类'
        verbose_name_plural = verbose_name
        ordering = ['sort', 'id']

    def __str__(self):
        return self.name


class Task(models.Model):
    """任务主表"""

    class Priority(models.IntegerChoices):
        URGENT = 1, '紧急'
        HIGH = 2, '高'
        MEDIUM = 3, '中'
        LOW = 4, '低'

    class Difficulty(models.IntegerChoices):
        EXTREME = 1, '极高'
        HIGH = 2, '高'
        MEDIUM = 3, '中'
        LOW = 4, '低'

    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待审核'
        APPROVED = 'approved', '审核通过'
        IN_PROGRESS = 'in_progress', '进行中'
        PENDING_VERIFY = 'pending_verify', '待验证'
        COMPLETED = 'completed', '已完成'
        REJECTED = 'rejected', '已驳回'
        CANCELLED = 'cancelled', '已取消'

    title = models.CharField('任务标题', max_length=200)
    description = models.TextField('任务描述', blank=True)
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.PROTECT,
        related_name='tasks',
        verbose_name='任务种类'
    )
    priority = models.IntegerField(
        '优先级',
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    difficulty = models.IntegerField(
        '难度等级',
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM
    )
    benefit = models.DecimalField(
        '效益/积分',
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text='仅部分任务种类需要填写'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='owned_tasks',
        verbose_name='负责人'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participated_tasks',
        verbose_name='参与人'
    )
    start_date = models.DateTimeField('开始时间', null=True, blank=True)
    expected_end_date = models.DateTimeField('预计结束时间', null=True, blank=True)
    actual_end_date = models.DateTimeField('实际结束时间', null=True, blank=True)
    progress = models.IntegerField('任务进度', default=0,
        help_text='0-100 百分比')
    status = models.CharField(
        '任务状态',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_tasks',
        verbose_name='创建者'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='updated_tasks',
        verbose_name='更新人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'task_task'
        verbose_name = '任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['owner']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return self.title


class TaskApproval(models.Model):
    """任务审批记录"""

    class ApprovalStatus(models.TextChoices):
        PENDING = 'pending', '待审批'
        APPROVED = 'approved', '已通过'
        REJECTED = 'rejected', '已驳回'

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='approvals',
        verbose_name='关联任务'
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='task_approvals',
        verbose_name='审批人'
    )
    status = models.CharField(
        '审批状态',
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING
    )
    comment = models.TextField('审批意见', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'task_approval'
        verbose_name = '审批记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task.title} - {self.get_status_display()}'


class TaskProgressRecord(models.Model):
    """任务进度记录（用于追溯进度变更历史）"""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name='关联任务'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='progress_records',
        verbose_name='操作人'
    )
    progress = models.IntegerField('进度', default=0,
        help_text='0-100 百分比')
    description = models.TextField('进度描述', blank=True)
    created_at = models.DateTimeField('记录时间', auto_now_add=True)

    class Meta:
        db_table = 'task_progress_record'
        verbose_name = '进度记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task.title} - {self.progress}%'


class TaskPerformance(models.Model):
    """任务绩效积分（用于绩效考察）"""

    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name='performance',
        verbose_name='关联任务'
    )
    base_score = models.DecimalField(
        '基础积分', max_digits=10, decimal_places=2, default=0,
        help_text='基于难度的基础积分'
    )
    priority_bonus = models.DecimalField(
        '优先级加成', max_digits=10, decimal_places=2, default=0
    )
    time_bonus = models.DecimalField(
        '时效加成', max_digits=10, decimal_places=2, default=0,
        help_text='按时/提前完成加分，延期扣分'
    )
    quality_score = models.DecimalField(
        '质量评分', max_digits=10, decimal_places=2, default=0,
        help_text='主管对任务完成质量的评分'
    )
    total_score = models.DecimalField(
        '总积分', max_digits=10, decimal_places=2, default=0
    )
    comment = models.TextField('评分说明', blank=True)
    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='evaluated_performances',
        verbose_name='评分人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'task_performance'
        verbose_name = '绩效积分'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.task.title} - {self.total_score}分'

    def calculate_total(self):
        """计算总积分"""
        self.total_score = (
            self.base_score + self.priority_bonus +
            self.time_bonus + self.quality_score
        )
        return self.total_score