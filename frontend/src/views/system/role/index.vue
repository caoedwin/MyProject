<template>
  <div class="role-page">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>角色管理</span>
          <el-button type="primary" @click="openDialog(null)">新增角色</el-button>
        </div>
      </template>
      <el-table :data="roleList" v-loading="loading" stripe>
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色编码" width="150" />
        <el-table-column prop="remark" label="备注" min-width="200" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'info'">{{ row.status ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑角色' : '新增角色'" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入角色编码" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" placeholder="备注信息" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" active-text="启用" inactive-text="禁用" />
        </el-form-item>
        <el-form-item label="关联菜单">
          <div class="menu-tree-box">
            <el-checkbox-group v-model="form.menu_ids">
              <div v-for="item in menuLeafList" :key="item.id" class="menu-leaf-item">
                <el-checkbox :value="item.id" :label="item.id">
                  {{ item.fullPath }}
                </el-checkbox>
              </div>
            </el-checkbox-group>
            <el-empty v-if="menuLeafList.length === 0" description="暂无菜单" :image-size="40" />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listRoles, createRole, updateRole, deleteRole, listMenus } from '@/api'

const loading = ref(false)
const roleList = ref([])
const dialogVisible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref()
const menuLeafList = ref([])

const form = reactive({
  name: '',
  code: '',
  remark: '',
  status: true,
  menu_ids: [],
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

// 获取角色列表
async function fetchList() {
  loading.value = true
  try {
    const res = await listRoles()
    roleList.value = res.data?.results || res.data || []
  } finally {
    loading.value = false
  }
}

// 获取菜单树，扁平化为叶子节点列表（带完整路径）
async function fetchMenuTree() {
  const res = await listMenus()
  const menus = res.data?.results || res.data || []
  menuLeafList.value = flattenLeafMenus(menus, '')
}

// 递归遍历菜单树，提取所有叶子菜单，生成 "父级 > 子级" 路径
function flattenLeafMenus(nodes, parentPath) {
  const result = []
  for (const node of nodes) {
    const currentPath = parentPath ? `${parentPath} > ${node.name}` : node.name
    const hasChildren = !!(node.children && node.children.length > 0)
    if (hasChildren) {
      // 目录节点：继续递归子节点
      result.push(...flattenLeafMenus(node.children, currentPath))
    } else if (node.menu_type === 1) {
      // 叶子菜单节点
      result.push({ id: node.id, fullPath: currentPath })
    }
  }
  return result
}

// 打开对话框
async function openDialog(row) {
  await fetchMenuTree()
  if (row) {
    isEdit.value = true
    editId.value = row.id
    form.name = row.name
    form.code = row.code
    form.remark = row.remark || ''
    form.status = row.status
    form.menu_ids = row.menu_ids || []
  } else {
    isEdit.value = false
    editId.value = null
    form.name = ''
    form.code = ''
    form.remark = ''
    form.status = true
    form.menu_ids = []
  }
  dialogVisible.value = true
}

// 保存
async function handleSave() {
  await formRef.value.validate()
  saving.value = true
  try {
    const data = {
      name: form.name,
      code: form.code,
      remark: form.remark,
      status: form.status,
      menu_ids: form.menu_ids,
    }
    if (isEdit.value) {
      await updateRole(editId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createRole(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchList()
  } catch {
    // 错误由拦截器处理
  } finally {
    saving.value = false
  }
}

// 删除
async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除角色「${row.name}」？`, '提示', { type: 'warning' })
  await deleteRole(row.id)
  ElMessage.success('已删除')
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped lang="scss">
.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu-tree-box {
  width: 100%;
  max-height: 350px;
  overflow-y: auto;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 12px;
}

.menu-leaf-item {
  padding: 4px 0;
  font-size: 13px;
}
</style>