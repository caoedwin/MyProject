"""任务管理子系统 - 序列化器"""
from rest_framework import serializers
from app01.models import User
from TaskManagement.models import (
    TaskCategory, Task, TaskApproval, TaskProgressRecord, TaskPerformance,
)


class UserBriefSerializer(serializers.ModelSerializer):
    """用户简要信息（用于下拉选择/穿梭框）"""
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname']


class TaskCategorySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = TaskCategory
        fields = [
            'id', 'name', 'code', 'description', 'has_benefit',
            'sort', 'status', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by']


class TaskListSerializer(serializers.ModelSerializer):
    """任务列表序列化器（精简版）"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'category', 'category_name', 'priority',
            'priority_display', 'difficulty', 'difficulty_display',
            'benefit', 'owner', 'owner_name', 'start_date',
            'expected_end_date', 'actual_end_date', 'progress',
            'status', 'status_display', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    """任务详情序列化器（完整版）"""
    category_info = TaskCategorySerializer(source='category', read_only=True)
    owner_info = UserBriefSerializer(source='owner', read_only=True)
    participants_info = UserBriefSerializer(source='participants', many=True, read_only=True)
    created_by_info = UserBriefSerializer(source='created_by', read_only=True)
    updated_by_info = UserBriefSerializer(source='updated_by', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # 审批记录
    approvals = serializers.SerializerMethodField()
    # 进度记录
    progress_records_data = serializers.SerializerMethodField()
    # 绩效信息
    performance_data = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'category', 'category_info',
            'priority', 'priority_display', 'difficulty', 'difficulty_display',
            'benefit', 'owner', 'owner_info', 'participants', 'participants_info',
            'start_date', 'expected_end_date', 'actual_end_date',
            'progress', 'status', 'status_display',
            'created_by', 'created_by_info', 'updated_by', 'updated_by_info',
            'created_at', 'updated_at',
            'approvals', 'progress_records_data', 'performance_data',
        ]
        read_only_fields = ['created_by', 'updated_by', 'status']

    def get_approvals(self, obj):
        approvals = obj.approvals.all().order_by('-created_at')
        return TaskApprovalSerializer(approvals, many=True).data

    def get_progress_records_data(self, obj):
        records = obj.progress_records.all().order_by('-created_at')
        return TaskProgressRecordSerializer(records, many=True).data

    def get_performance_data(self, obj):
        if hasattr(obj, 'performance'):
            return TaskPerformanceSerializer(obj.performance).data
        return None


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """任务创建/更新序列化器"""
    participant_ids = serializers.PrimaryKeyRelatedField(
        source='participants', many=True,
        queryset=User.objects.filter(status=1),
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'category', 'priority',
            'difficulty', 'benefit', 'owner', 'participant_ids',
            'start_date', 'expected_end_date', 'actual_end_date',
            'progress', 'status',
        ]

    def validate(self, attrs):
        """校验：如果任务种类需要效益，则效益字段必填"""
        category = attrs.get('category')
        if category:
            # 如果是创建，category 是对象；如果是更新，可能是对象或 ID
            if hasattr(category, 'has_benefit'):
                cat = category
            else:
                cat = TaskCategory.objects.get(pk=category)
            if cat.has_benefit and not attrs.get('benefit'):
                raise serializers.ValidationError(
                    {'benefit': f'任务种类"{cat.name}"需要填写效益/积分'}
                )
        return attrs


class TaskApprovalSerializer(serializers.ModelSerializer):
    approver_name = serializers.CharField(source='approver.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TaskApproval
        fields = [
            'id', 'task', 'approver', 'approver_name',
            'status', 'status_display', 'comment',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['approver']


class TaskProgressRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TaskProgressRecord
        fields = [
            'id', 'task', 'user', 'user_name',
            'progress', 'description', 'created_at',
        ]
        read_only_fields = ['user']


class TaskPerformanceSerializer(serializers.ModelSerializer):
    evaluated_by_name = serializers.CharField(source='evaluated_by.username', read_only=True)

    class Meta:
        model = TaskPerformance
        fields = [
            'id', 'task', 'base_score', 'priority_bonus',
            'time_bonus', 'quality_score', 'total_score',
            'comment', 'evaluated_by', 'evaluated_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['evaluated_by']


class TaskStatsSerializer(serializers.Serializer):
    """任务统计序列化器"""
    total = serializers.IntegerField()
    by_status = serializers.DictField()
    by_priority = serializers.DictField()
    by_category = serializers.DictField()
    by_owner = serializers.ListField()
    by_difficulty = serializers.DictField()