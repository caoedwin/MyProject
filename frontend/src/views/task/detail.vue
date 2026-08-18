<template>
  <div class="task-detail-page">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>
            <el-button @click="$router.back()" link><el-icon><ArrowLeft /></el-icon>返回</el-button>
            任务详情
          </span>
          <div>
            <el-button v-if="canSubmit" type="warning" @click="showSubmitDialog = true">提交审核</el-button>
            <el-button v-if="canApprove" type="success" @click="handleApprove">审批通过</el-button>
            <el-button v-if="canApprove" type="danger" @click="showRejectDialog = true">驳回</el-button>
            <el-button v-if="canUpdateProgress" type="primary" @click="showProgressDialog = true">更新进度</el-button>
            <el-button v-if="canVerify" type="success" @click="handleVerify">验证通过</el-button>
            <el-button v-if="canEdit" type="primary" @click="goEdit">编辑</el-button>
          </div>
        </div>
      </template>

      <el-descriptions v-loading="loading" :column="2" border>
        <el-descriptions-item label="任务标题" :span="2">{{ task.title }}</el-descriptions-item>
        <el-descriptions-item label="任务种类">{{ task.category_info?.name }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="priorityTagType(task.priority)">{{ task.priority_display }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="难度等级">{{ task.difficulty_display }}</el-descriptions-item>
        <el-descriptions-item label="效益/积分">{{ task.benefit || '-' }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ task.owner_info?.username }} ({{ task.owner_info?.nickname }})</el-descriptions-item>
        <el-descriptions-item label="参与人">
          <template v-if="task.participants_info?.length">
            <el-tag v-for="p in task.participants_info" :key="p.id" style="margin:2px">{{ p.username }}</el-tag>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="任务状态">
          <el-tag :type="statusTagType(task.status)">{{ task.status_display }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="进度">
          <el-progress :percentage="task.progress" :stroke-width="12" :status="task.progress === 100 ? 'success' : ''" />
        </el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ task.start_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="预计结束时间">{{ task.expected_end_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="实际结束时间">{{ task.actual_end_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ task.created_by_info?.username }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ task.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ task.updated_at }}</el-descriptions-item>
        <el-descriptions-item label="任务描述" :span="2">
          <div style="white-space:pre-wrap">{{ task.description || '-' }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 审批记录 -->
    <el-card style="margin-top:16px">
      <template #header><span>审批记录</span></template>
      <el-timeline v-if="task.approvals?.length">
        <el-timeline-item
          v-for="approval in task.approvals"
          :key="approval.id"
          :timestamp="approval.created_at"
          :type="approvalType(approval.status)"
        >
          <p><strong>{{ approval.approver_name }}</strong> - {{ approval.status_display }}</p>
          <p v-if="approval.comment" style="color:#909399">{{ approval.comment }}</p>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无审批记录" />
    </el-card>

    <!-- 进度记录 -->
    <el-card style="margin-top:16px">
      <template #header><span>进度记录</span></template>
      <el-timeline v-if="task.progress_records_data?.length">
        <el-timeline-item
          v-for="record in task.progress_records_data"
          :key="record.id"
          :timestamp="record.created_at"
        >
          <p><strong>{{ record.user_name }}</strong> 更新进度至 {{ record.progress }}%</p>
          <p v-if="record.description" style="color:#909399">{{ record.description }}</p>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无进度记录" />
    </el-card>

    <!-- 绩效信息 -->
    <el-card v-if="task.performance_data" style="margin-top:16px">
      <template #header><span>绩效评分</span></template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="基础积分">{{ task.performance_data.base_score }}</el-descriptions-item>
        <el-descriptions-item label="优先级加成">{{ task.performance_data.priority_bonus }}</el-descriptions-item>
        <el-descriptions-item label="时效加成">{{ task.performance_data.time_bonus }}</el-descriptions-item>
        <el-descriptions-item label="质量评分">{{ task.performance_data.quality_score }}</el-descriptions-item>
        <el-descriptions-item label="总积分">
          <strong style="font-size:18px;color:#409eff">{{ task.performance_data.total_score }}</strong>
        </el-descriptions-item>
        <el-descriptions-item label="评分人">{{ task.performance_data.evaluated_by_name }}</el-descriptions-item>
        <el-descriptions-item label="评分说明" :span="3">{{ task.performance_data.comment || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 提交审核对话框 -->
    <el-dialog v-model="showSubmitDialog" title="提交审核" width="500px">
      <el-form label-width="100px">
        <el-form-item label="审批人">
          <el-autocomplete
            v-model="approvalForm.approverName"
            :fetch-suggestions="querySearchApprover"
            placeholder="请选择主管"
            clearable
            @select="handleApproverSelect"
            style="width:100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSubmitDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitApproval">提交</el-button>
      </template>
    </el-dialog>

    <!-- 驳回对话框 -->
    <el-dialog v-model="showRejectDialog" title="驳回任务" width="500px">
      <el-form label-width="100px">
        <el-form-item label="驳回原因">
          <el-input v-model="rejectComment" type="textarea" :rows="3" placeholder="请输入驳回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRejectDialog = false">取消</el-button>
        <el-button type="danger" @click="handleReject">确认驳回</el-button>
      </template>
    </el-dialog>

    <!-- 进度更新对话框 -->
    <el-dialog v-model="showProgressDialog" title="更新进度" width="500px">
      <el-form label-width="100px">
        <el-form-item label="当前进度">
          <el-slider v-model="progressForm.progress" :min="0" :max="100" show-input />
        </el-form-item>
        <el-form-item label="进度描述">
          <el-input v-model="progressForm.description" type="textarea" :rows="3" placeholder="请描述进度情况" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProgressDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateProgress">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import {
  getTaskDetail, submitApproval, approveTask, rejectTask,
  updateTaskProgress, verifyTask, searchUsers,
} from '@/api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const task = ref({})
const taskId = route.params.id

// 审批
const showSubmitDialog = ref(false)
const showRejectDialog = ref(false)
const showProgressDialog = ref(false)
const rejectComment = ref('')
const approvalForm = reactive({ approverId: '', approverName: '' })
const progressForm = reactive({ progress: 0, description: '' })

const canEdit = computed(() => task.value.can_edit === true)
const canSubmit = computed(() => {
  return canEdit.value && ['draft', 'rejected'].includes(task.value.status)
})
const canApprove = computed(() => {
  return canEdit.value && task.value.status === 'pending'
})
const canUpdateProgress = computed(() => {
  return canEdit.value && ['approved', 'in_progress'].includes(task.value.status)
})
const canVerify = computed(() => {
  return canEdit.value && task.value.status === 'pending_verify'
})

function priorityTagType(p) {
  const map = { 1: 'danger', 2: 'warning', 3: 'info', 4: '' }
  return map[p] || ''
}

function statusTagType(s) {
  const map = {
    draft: 'info', pending: 'warning', approved: 'success',
    in_progress: '', pending_verify: 'warning',
    completed: 'success', rejected: 'danger', cancelled: 'info',
  }
  return map[s] || ''
}

function approvalType(status) {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

async function fetchDetail() {
  loading.value = true
  try {
    const res = await getTaskDetail(taskId)
    task.value = res.data || {}
    progressForm.progress = task.value.progress || 0
  } finally {
    loading.value = false
  }
}

async function querySearchApprover(queryString, cb) {
  if (!queryString) { cb([]); return }
  try {
    const res = await searchUsers({ keyword: queryString })
    const users = (res.data || []).map(u => ({
      value: u.username,
      number: u.id,
    }))
    cb(users)
  } catch (e) { cb([]) }
}

function handleApproverSelect(item) {
  approvalForm.approverId = item.number
}

async function handleSubmitApproval() {
  if (!approvalForm.approverId) {
    ElMessage.warning('请选择审批人')
    return
  }
  try {
    await submitApproval(taskId, { approver_id: approvalForm.approverId })
    ElMessage.success('已提交审核')
    showSubmitDialog.value = false
    fetchDetail()
  } catch (e) { /* handled */ }
}

async function handleApprove() {
  try {
    await approveTask(taskId, { comment: '审批通过' })
    ElMessage.success('审批通过')
    fetchDetail()
  } catch (e) { /* handled */ }
}

async function handleReject() {
  if (!rejectComment.value) {
    ElMessage.warning('请输入驳回原因')
    return
  }
  try {
    await rejectTask(taskId, { comment: rejectComment.value })
    ElMessage.success('已驳回')
    showRejectDialog.value = false
    rejectComment.value = ''
    fetchDetail()
  } catch (e) { /* handled */ }
}

async function handleUpdateProgress() {
  try {
    await updateTaskProgress(taskId, {
      progress: progressForm.progress,
      description: progressForm.description,
    })
    ElMessage.success('进度更新成功')
    showProgressDialog.value = false
    fetchDetail()
  } catch (e) { /* handled */ }
}

async function handleVerify() {
  try {
    await verifyTask(taskId)
    ElMessage.success('验证通过')
    fetchDetail()
  } catch (e) { /* handled */ }
}

function goEdit() {
  router.push(`/task?edit=${taskId}`)
}

onMounted(fetchDetail)
</script>

<style scoped>
.task-detail-page {
  padding: 20px;
}
.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>