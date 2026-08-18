"""任务管理子系统 - Django Admin 注册"""
from django import forms
from django.contrib import admin
from django.db.models import Q

from TaskManagement.models import (
    TaskCategory, Task, TaskApproval, TaskProgressRecord, TaskPerformance,
)


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'has_benefit', 'sort', 'status', 'created_at']
    list_filter = ['status', 'has_benefit']
    search_fields = ['name', 'code']
    list_editable = ['sort', 'status']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'priority', 'difficulty',
                    'owner', 'progress', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'priority', 'difficulty', 'category']
    search_fields = ['title', 'description', 'owner__username', 'created_by__username']
    raw_id_fields = ['owner', 'created_by', 'updated_by']
    filter_horizontal = ['participants']
    readonly_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TaskApproval)
class TaskApprovalAdmin(admin.ModelAdmin):
    list_display = ['task', 'approver', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['task__title', 'approver__username']
    raw_id_fields = ['task', 'approver']


@admin.register(TaskProgressRecord)
class TaskProgressRecordAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'progress', 'created_at']
    search_fields = ['task__title', 'user__username']
    raw_id_fields = ['task', 'user']


@admin.register(TaskPerformance)
class TaskPerformanceAdmin(admin.ModelAdmin):
    list_display = ['task', 'base_score', 'priority_bonus', 'time_bonus',
                    'quality_score', 'total_score', 'evaluated_by', 'created_at']
    search_fields = ['task__title', 'evaluated_by__username']
    raw_id_fields = ['task', 'evaluated_by']