<template>
  <div class="task-category-page">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>任务种类管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增种类
          </el-button>
        </div>
      </template>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="code" label="编码" width="150" />
        <el-table-column prop="has_benefit" label="是否有效益" width="100">
          <template #default="{ row }">
            <el-tag :type="row.has_benefit ? 'success' : 'info'">{{ row.has_benefit ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'danger'">{{ row.status ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" @closed="resetForm">
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="种类名称" prop="name">
          <el-input v-model="formData.name" placeholder="例如：日常任务" />
        </el-form-item>
        <el-form-item label="种类编码" prop="code">
          <el-input v-model="formData.code" placeholder="例如：daily" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="是否有效益">
          <el-switch v-model="formData.has_benefit" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="formData.sort" :min="0" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="formData.status" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { listAllTaskCategories, createTaskCategory, updateTaskCategory, deleteTaskCategory } from '@/api'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增种类')
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const formData = reactive({
  name: '',
  code: '',
  description: '',
  has_benefit: false,
  sort: 0,
  status: true,
})

const rules = {
  name: [{ required: true, message: '请输入种类名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入种类编码', trigger: 'blur' }],
}

async function fetchList() {
  loading.value = true
  try {
    const res = await listAllTaskCategories()
    tableData.value = res.data || []
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  editId.value = null
  dialogTitle.value = '新增种类'
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  editId.value = row.id
  dialogTitle.value = '编辑种类'
  formData.name = row.name
  formData.code = row.code
  formData.description = row.description || ''
  formData.has_benefit = row.has_benefit
  formData.sort = row.sort
  formData.status = row.status
  dialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除该种类吗？', '确认删除', { type: 'warning' })
    await deleteTaskCategory(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {
    if (e !== 'cancel') { /* handled */ }
  }
}

async function submitForm() {
  try {
    await formRef.value.validate()
  } catch { return }
  submitting.value = true
  try {
    const data = { ...formData }
    if (isEdit.value) {
      await updateTaskCategory(editId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createTaskCategory(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
  formData.name = ''
  formData.code = ''
  formData.description = ''
  formData.has_benefit = false
  formData.sort = 0
  formData.status = true
}

onMounted(fetchList)
</script>

<style scoped>
.task-category-page {
  padding: 20px;
}
.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>