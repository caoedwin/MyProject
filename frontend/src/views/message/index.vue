<template>
  <div class="message-page">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>消息中心</span>
          <el-button v-if="userStore.isAdmin" type="primary" @click="broadcastDialog = true">发广播</el-button>
        </div>
      </template>
      <el-table :data="messageList" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="category_display" label="类型" width="100" />
        <el-table-column prop="sender_name" label="发送人" width="120" />
        <el-table-column prop="is_read" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_read ? 'info' : 'danger'">{{ row.is_read ? '已读' : '未读' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button v-if="!row.is_read" link type="primary" @click="handleRead(row)">标记已读</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="broadcastDialog" title="发送广播" width="500px">
      <el-form :model="broadcastForm" label-width="80px">
        <el-form-item label="标题"><el-input v-model="broadcastForm.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="broadcastForm.content" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="broadcastDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBroadcast">发送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listMessages, markMessageRead, broadcastMessage } from '@/api'
import { useUserStore } from '@/store/user'
import { useMessageStore } from '@/store/message'

const userStore = useUserStore()
const messageStore = useMessageStore()
const loading = ref(false)
const messageList = ref([])
const broadcastDialog = ref(false)
const broadcastForm = reactive({ title: '', content: '' })

async function fetchList() {
  loading.value = true
  try {
    const res = await listMessages()
    messageList.value = res.data?.results || res.data || []
  } finally {
    loading.value = false
  }
}

async function handleRead(row) {
  await markMessageRead(row.id)
  ElMessage.success('已标记已读')
  fetchList()
  // 即时刷新菜单栏铃铛未读数，避免只能等 30s 轮询或刷新整页
  messageStore.fetchUnread()
}

async function handleBroadcast() {
  if (!broadcastForm.title || !broadcastForm.content) {
    ElMessage.warning('请填写完整')
    return
  }
  await broadcastMessage(broadcastForm)
  ElMessage.success('广播已发送')
  broadcastDialog.value = false
  broadcastForm.title = ''
  broadcastForm.content = ''
  fetchList()
}

onMounted(fetchList)
</script>
