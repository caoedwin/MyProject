<template>
  <div class="task-page">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>任务管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>新增
            </el-button>
            <el-button @click="downloadTemplate">
              <el-icon><Download /></el-icon>模板下载
            </el-button>
            <el-upload
              :show-file-list="false"
              :before-upload="handleUpload"
              accept=".xlsx,.xls"
              style="display:inline-block;margin:0 8px"
            >
              <el-button><el-icon><Upload /></el-icon>Excel上传</el-button>
            </el-upload>
            <el-button @click="handleExport">
              <el-icon><Document /></el-icon>导出
            </el-button>
            <el-button
              type="danger"
              :disabled="selectedIds.length === 0"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>批量删除
            </el-button>
            <el-button @click="handleBatchEdit" :disabled="selectedIds.length !== 1">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-popover placement="bottom" :width="300" trigger="click">
              <template #reference>
                <el-button><el-icon><Setting /></el-icon>列设定</el-button>
              </template>
              <el-checkbox-group v-model="visibleColumns">
                <div v-for="col in allColumns" :key="col.key" style="margin:4px 0">
                  <el-checkbox :label="col.key" :disabled="col.fixed">{{ col.label }}</el-checkbox>
                </div>
              </el-checkbox-group>
            </el-popover>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键字">
          <el-input v-model="searchForm.keyword" placeholder="任务标题/描述" clearable @clear="handleSearch" @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="任务种类">
          <el-select v-model="searchForm.category" placeholder="全部" clearable filterable>
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="searchForm.priority" placeholder="全部" clearable>
            <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="searchForm.difficulty" placeholder="全部" clearable>
            <el-option v-for="item in difficultyOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-autocomplete
            v-model="searchForm.ownerName"
            :fetch-suggestions="querySearchOwner"
            placeholder="请输入负责人"
            clearable
            @select="handleOwnerSelect"
            @clear="searchForm.owner = ''; handleSearch()"
            style="width:200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        @selection-change="handleSelectionChange"
        ref="tableRef"
      >
        <el-table-column type="selection" width="55" :selectable="checkSelectable" align="center" />
        <el-table-column prop="title" label="任务标题" min-width="180" show-overflow-tooltip
          v-if="visibleColumns.includes('title')" />
        <el-table-column prop="category_name" label="任务种类" width="120"
          v-if="visibleColumns.includes('category_name')" />
        <el-table-column prop="priority_display" label="优先级" width="80"
          v-if="visibleColumns.includes('priority_display')">
          <template #default="{ row }">
            <el-tag :type="priorityTagType(row.priority)" effect="dark" size="small">{{ row.priority_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty_display" label="难度" width="80"
          v-if="visibleColumns.includes('difficulty_display')">
          <template #default="{ row }">
            <el-tag :type="difficultyTagType(row.difficulty)" effect="plain" size="small">{{ row.difficulty_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="benefit" label="效益/积分" width="100"
          v-if="visibleColumns.includes('benefit')" />
        <el-table-column prop="owner_name" label="负责人" width="100"
          v-if="visibleColumns.includes('owner_name')" />
        <el-table-column prop="progress" label="进度" width="140"
          v-if="visibleColumns.includes('progress')">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :stroke-width="8"
              :status="row.progress === 100 ? 'success' : ''"
              :color="progressColor(row.progress)" />
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="100"
          v-if="visibleColumns.includes('status_display')">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" :effect="statusEffect(row.status)" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始时间" width="110"
          v-if="visibleColumns.includes('start_date')" />
        <el-table-column prop="expected_end_date" label="预计结束" width="110"
          v-if="visibleColumns.includes('expected_end_date')" />
        <el-table-column prop="actual_end_date" label="实际结束" width="110"
          v-if="visibleColumns.includes('actual_end_date')" />
        <el-table-column prop="created_by_name" label="创建人" width="100"
          v-if="visibleColumns.includes('created_by_name')" />
        <el-table-column prop="created_at" label="创建时间" width="160"
          v-if="visibleColumns.includes('created_at')" />
        <el-table-column label="操作" width="340" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">详情</el-button>
            <el-button link type="primary" :disabled="!row.can_edit" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" :disabled="!row.can_edit" @click="handleDelete(row)">删除</el-button>
            <template v-if="row.can_edit">
              <!-- 草稿/已驳回 -> 提交审核 -->
              <el-button v-if="['draft','rejected'].includes(row.status)" link type="warning" @click="showSubmitApproval(row)">提交审核</el-button>
              <!-- 待审核 -> 审批通过/驳回 -->
              <el-button v-if="row.status === 'pending'" link type="success" @click="handleApproveInline(row)">通过</el-button>
              <el-button v-if="row.status === 'pending'" link type="danger" @click="showRejectInline(row)">驳回</el-button>
              <!-- 审核通过/进行中 -> 更新进度 -->
              <el-button v-if="['approved','in_progress'].includes(row.status)" link type="primary" @click="showProgressInline(row)">进度</el-button>
              <!-- 待验证 -> 验证通过 -->
              <el-button v-if="row.status === 'pending_verify'" link type="success" @click="handleVerifyInline(row)">验证通过</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top:20px; text-align:right;"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="1000px"
      :close-on-click-modal="false"
      @closed="resetForm"
      @opened="loadAllUsers"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="110px">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="任务标题" prop="title">
              <el-input v-model="formData.title" placeholder="请输入任务标题" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="任务种类" prop="category">
              <el-select v-model="formData.category" placeholder="请选择" filterable style="width:100%">
                <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="formData.priority" placeholder="请选择" style="width:100%">
                <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="难度等级" prop="difficulty">
              <el-select v-model="formData.difficulty" placeholder="请选择" style="width:100%">
                <el-option v-for="item in difficultyOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="效益/积分" prop="benefit">
              <el-input-number v-model="formData.benefit" :min="0" :precision="2" style="width:100%" placeholder="部分任务种类需要填写" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开始时间">
              <el-date-picker v-model="formData.start_date" type="date" placeholder="选择日期" style="width:100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计结束时间">
              <el-date-picker v-model="formData.expected_end_date" type="date" placeholder="选择日期" style="width:100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="isEdit">
            <el-form-item label="任务进度">
              <el-slider v-model="formData.progress" :min="0" :max="100" show-input :show-input-controls="false" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="负责人">
              <el-transfer
                v-model="formData.owner"
                :data="allUsers"
                :titles="['可选用户', '负责人']"
                :filter-method="filterUser"
                :props="{ key: 'id', label: 'label' }"
                filterable
                filter-placeholder="输入用户名/昵称筛选"
                style="width:100%"
                @change="handleOwnerTransferChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="参与人">
              <el-transfer
                v-model="formData.participant_ids"
                :data="allUsers"
                :titles="['可选用户', '参与人']"
                :filter-method="filterUser"
                :props="{ key: 'id', label: 'label' }"
                filterable
                filter-placeholder="输入用户名/昵称筛选"
                style="width:100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="任务描述">
              <el-input v-model="formData.description" type="textarea" :rows="4" placeholder="请输入任务描述" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 提交审核对话框 -->
    <el-dialog v-model="submitDialogVisible" title="提交审核" width="700px" @opened="loadQMUsers">
      <el-form label-width="100px">
        <el-form-item label="审批人">
          <el-transfer
            v-model="approvalForm.approverId"
            :data="qmUsers"
            :titles="['可选主管', '审批人']"
            :filter-method="filterUser"
            :props="{ key: 'id', label: 'label' }"
            filterable
            filter-placeholder="输入用户名/昵称筛选"
            style="width:100%"
            @change="handleQMTransferChange"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="submitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitApproval">提交</el-button>
      </template>
    </el-dialog>

    <!-- 驳回对话框 -->
    <el-dialog v-model="rejectDialogVisible" title="驳回任务" width="500px">
      <el-form label-width="100px">
        <el-form-item label="驳回原因">
          <el-input v-model="rejectComment" type="textarea" :rows="3" placeholder="请输入驳回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="handleRejectInline">确认驳回</el-button>
      </template>
    </el-dialog>

    <!-- 进度更新对话框 -->
    <el-dialog v-model="progressDialogVisible" title="更新进度" width="500px">
      <el-form label-width="100px">
        <el-form-item label="当前进度">
          <el-slider v-model="progressFormInline.progress" :min="0" :max="100" show-input />
        </el-form-item>
        <el-form-item label="进度描述">
          <el-input v-model="progressFormInline.description" type="textarea" :rows="3" placeholder="请描述进度情况" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="progressDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateProgressInline">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Upload, Document, Delete, Edit, Setting } from '@element-plus/icons-vue'
import {
  listTasks, createTask, updateTask, deleteTask, batchDeleteTasks,
  listTaskCategories, downloadTaskTemplate, importTasksExcel, exportTasksExcel,
  searchUsers, submitApproval, approveTask, rejectTask, updateTaskProgress, verifyTask, getQMUsers,
} from '@/api'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const tableRef = ref(null)
const selectedIds = ref([])
const currentPage = ref(1)
const pageSize = ref(100)
const total = ref(0)
const categories = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增任务')
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)
const allUsers = ref([])

// 工作流对话框状态
const submitDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const progressDialogVisible = ref(false)
const currentTaskRow = ref(null)
const rejectComment = ref('')
const approvalForm = reactive({ approverId: [] })
const progressFormInline = reactive({ progress: 0, description: '' })
const qmUsers = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: '',
  status: '',
  priority: '',
  difficulty: '',
  owner: '',
  ownerName: '',
})

// 表单数据
const formData = reactive({
  title: '',
  category: '',
  priority: 3,
  difficulty: 3,
  benefit: null,
  owner: [],
  participant_ids: [],
  start_date: '',
  expected_end_date: '',
  actual_end_date: '',
  description: '',
  progress: 0,
  status: 'draft',
})

const rules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择任务种类', trigger: 'change' }],
}

// 列设定
const allColumns = [
  { key: 'title', label: '任务标题', fixed: true },
  { key: 'category_name', label: '任务种类', fixed: false },
  { key: 'priority_display', label: '优先级', fixed: false },
  { key: 'difficulty_display', label: '难度', fixed: false },
  { key: 'benefit', label: '效益/积分', fixed: false },
  { key: 'owner_name', label: '负责人', fixed: false },
  { key: 'progress', label: '进度', fixed: false },
  { key: 'status_display', label: '状态', fixed: false },
  { key: 'start_date', label: '开始时间', fixed: false },
  { key: 'expected_end_date', label: '预计结束', fixed: false },
  { key: 'actual_end_date', label: '实际结束', fixed: false },
  { key: 'created_by_name', label: '创建人', fixed: false },
  { key: 'created_at', label: '创建时间', fixed: false },
]
const visibleColumns = ref(allColumns.map(c => c.key))

const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'pending', label: '待审核' },
  { value: 'approved', label: '审核通过' },
  { value: 'in_progress', label: '进行中' },
  { value: 'pending_verify', label: '待验证' },
  { value: 'completed', label: '已完成' },
  { value: 'rejected', label: '已驳回' },
  { value: 'cancelled', label: '已取消' },
]

const priorityOptions = [
  { value: 1, label: '紧急' },
  { value: 2, label: '高' },
  { value: 3, label: '中' },
  { value: 4, label: '低' },
]

const difficultyOptions = [
  { value: 1, label: '极高' },
  { value: 2, label: '高' },
  { value: 3, label: '中' },
  { value: 4, label: '低' },
]

function priorityTagType(priority) {
  const map = { 1: 'danger', 2: 'warning', 3: 'info', 4: '' }
  return map[priority] || ''
}

function statusTagType(status) {
  const map = {
    draft: 'info', pending: 'warning', approved: 'success',
    in_progress: '', pending_verify: 'warning',
    completed: 'success', rejected: 'danger', cancelled: 'info',
  }
  return map[status] || ''
}

function statusEffect(status) {
  // 进行中/待审核等活跃状态用 dark，已完成/已取消等用 plain
  const dark = ['pending', 'in_progress', 'pending_verify']
  return dark.includes(status) ? 'dark' : 'plain'
}

function difficultyTagType(difficulty) {
  const map = { 1: 'danger', 2: 'warning', 3: 'info', 4: '' }
  return map[difficulty] || ''
}

function progressColor(progress) {
  if (progress >= 100) return '#67c23a'
  if (progress >= 60) return '#409eff'
  if (progress >= 30) return '#e6a23c'
  return '#909399'
}

function checkSelectable(row) {
  return row.can_edit === true
}

// 获取任务列表
async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...searchForm,
    }
    // 清理空值
    Object.keys(params).forEach(k => {
      if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k]
    })
    const res = await listTasks(params)
    tableData.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (e) {
    // 错误已在拦截器处理
  } finally {
    loading.value = false
  }
}

// 获取任务种类
async function fetchCategories() {
  try {
    const res = await listTaskCategories()
    categories.value = res.data || []
  } catch (e) { /* ignore */ }
}

// 加载所有用户（穿梭框数据源）
async function loadAllUsers() {
  try {
    const res = await searchUsers({ keyword: '' })
    allUsers.value = (res.data || []).map(u => ({
      id: u.id,
      label: `${u.username} (${u.nickname || u.username})`,
    }))
  } catch (e) { /* ignore */ }
}

function filterUser(query, item) {
  return item.label.toLowerCase().includes(query.toLowerCase())
}

// 负责人穿梭框：只允许单选
function handleOwnerTransferChange(value, direction, movedKeys) {
  if (direction === 'right' && value.length > 1) {
    // 只保留最新选中的
    formData.owner = [movedKeys[0]]
  }
}

// 搜索栏：负责人 autocomplete
async function querySearchOwner(queryString, cb) {
  if (!queryString) { cb([]); return }
  try {
    const res = await searchUsers({ keyword: queryString })
    const users = (res.data || []).map(u => ({
      value: u.username,
      number: u.id,
      nickname: u.nickname,
    }))
    cb(users)
  } catch (e) { cb([]) }
}

function handleOwnerSelect(item) {
  searchForm.owner = item.number
  handleSearch()
}

function handleSearch() {
  currentPage.value = 1
  fetchList()
}

function resetSearch() {
  searchForm.keyword = ''
  searchForm.category = ''
  searchForm.status = ''
  searchForm.priority = ''
  searchForm.difficulty = ''
  searchForm.owner = ''
  searchForm.ownerName = ''
  handleSearch()
}

function handleSizeChange() {
  fetchList()
}

function handleCurrentChange() {
  fetchList()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(s => s.id)
}

function handleAdd() {
  isEdit.value = false
  editId.value = null
  dialogTitle.value = '新增任务'
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  editId.value = row.id
  dialogTitle.value = '编辑任务'
  // 填充表单数据
  formData.title = row.title
  formData.category = row.category
  formData.priority = row.priority
  formData.difficulty = row.difficulty
  formData.benefit = row.benefit
  formData.owner = row.owner ? [row.owner] : []
  formData.participant_ids = row.participants ? row.participants.map(p => p.id || p) : []
  formData.start_date = row.start_date
  formData.expected_end_date = row.expected_end_date
  formData.actual_end_date = row.actual_end_date
  formData.description = row.description || ''
  formData.progress = row.progress || 0
  formData.status = row.status
  dialogVisible.value = true
}

function handleView(row) {
  router.push(`/task/detail/${row.id}`)
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗？', '确认删除', { type: 'warning' })
    await deleteTask(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {
    if (e !== 'cancel') { /* error handled by interceptor */ }
  }
}

// ========== 工作流操作 ==========
async function loadQMUsers() {
  try {
    const res = await getQMUsers()
    qmUsers.value = (res.data || []).map(u => ({
      id: u.id,
      label: `${u.username} (${u.nickname || u.username})`,
    }))
  } catch (e) { /* ignore */ }
}

// 审批人穿梭框：只允许单选
function handleQMTransferChange(value, direction, movedKeys) {
  if (direction === 'right' && value.length > 1) {
    approvalForm.approverId = [movedKeys[0]]
  }
}

function showSubmitApproval(row) {
  currentTaskRow.value = row
  approvalForm.approverId = []
  submitDialogVisible.value = true
}

async function handleSubmitApproval() {
  if (!approvalForm.approverId.length) {
    ElMessage.warning('请选择审批人')
    return
  }
  try {
    await submitApproval(currentTaskRow.value.id, { approver_id: approvalForm.approverId[0] })
    ElMessage.success('已提交审核')
    submitDialogVisible.value = false
    fetchList()
  } catch (e) { /* handled */ }
}

async function handleApproveInline(row) {
  try {
    await approveTask(row.id, { comment: '审批通过' })
    ElMessage.success('审批通过')
    fetchList()
  } catch (e) { /* handled */ }
}

function showRejectInline(row) {
  currentTaskRow.value = row
  rejectComment.value = ''
  rejectDialogVisible.value = true
}

async function handleRejectInline() {
  if (!rejectComment.value) {
    ElMessage.warning('请输入驳回原因')
    return
  }
  try {
    await rejectTask(currentTaskRow.value.id, { comment: rejectComment.value })
    ElMessage.success('已驳回')
    rejectDialogVisible.value = false
    fetchList()
  } catch (e) { /* handled */ }
}

function showProgressInline(row) {
  currentTaskRow.value = row
  progressFormInline.progress = row.progress || 0
  progressFormInline.description = ''
  progressDialogVisible.value = true
}

async function handleUpdateProgressInline() {
  try {
    await updateTaskProgress(currentTaskRow.value.id, {
      progress: progressFormInline.progress,
      description: progressFormInline.description,
    })
    ElMessage.success('进度更新成功')
    progressDialogVisible.value = false
    fetchList()
  } catch (e) { /* handled */ }
}

async function handleVerifyInline(row) {
  try {
    await verifyTask(row.id)
    ElMessage.success('验证通过')
    fetchList()
  } catch (e) { /* handled */ }
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要删除的任务')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条任务吗？`,
      '批量删除',
      { type: 'warning' }
    )
    await batchDeleteTasks({ ids: selectedIds.value })
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    fetchList()
  } catch (e) {
    if (e !== 'cancel') { /* error handled */ }
  }
}

function handleBatchEdit() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择一条任务')
    return
  }
  if (selectedIds.value.length > 1) {
    ElMessage.warning('编辑只能选择一条任务')
    return
  }
  const row = tableData.value.find(r => r.id === selectedIds.value[0])
  if (row) handleEdit(row)
}

async function submitForm() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    const data = {
      title: formData.title,
      description: formData.description,
      category: formData.category,
      priority: formData.priority,
      difficulty: formData.difficulty,
      benefit: formData.benefit,
      owner: formData.owner.length > 0 ? formData.owner[0] : undefined,
      participant_ids: formData.participant_ids,
      start_date: formData.start_date || undefined,
      expected_end_date: formData.expected_end_date || undefined,
      actual_end_date: formData.actual_end_date || undefined,
    }
    if (isEdit.value) {
      data.progress = formData.progress
      data.status = formData.status
      await updateTask(editId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createTask(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchList()
  } catch (e) {
    // error handled by interceptor
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
  formData.title = ''
  formData.category = ''
  formData.priority = 3
  formData.difficulty = 3
  formData.benefit = null
  formData.owner = []
  formData.participant_ids = []
  formData.start_date = ''
  formData.expected_end_date = ''
  formData.actual_end_date = ''
  formData.description = ''
  formData.progress = 0
  formData.status = 'draft'
}

async function handleUpload(file) {
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await importTasksExcel(formData)
    ElMessage.success(res.msg || '导入成功')
    fetchList()
  } catch (e) {
    // error handled
  }
  return false // 阻止默认上传行为
}

async function handleExport() {
  try {
    const params = { ...searchForm }
    Object.keys(params).forEach(k => {
      if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k]
    })
    params.page_size = 99999
    const res = await exportTasksExcel(params)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = 'tasks.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    // error handled
  }
}

async function downloadTemplate() {
  try {
    const res = await downloadTaskTemplate()
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = 'task_template.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    // error handled
  }
}

onMounted(() => {
  fetchCategories()
  fetchList()
})
</script>

<style scoped>
.task-page {
  padding: 20px;
}
.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}
.search-form {
  margin-bottom: 16px;
}
.search-form .el-form-item {
  margin-bottom: 8px;
}
</style>