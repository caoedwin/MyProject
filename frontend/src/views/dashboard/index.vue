<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in statCards" :key="card.title">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" :style="{ background: card.color }">
              <component :is="card.icon" />
            </el-icon>
            <div class="stat-content">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-title">{{ card.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <span>欢迎，{{ userStore.userInfo?.nickname || userStore.userInfo?.username }}</span>
          </template>
          <div class="welcome">
            <p>这是 MyProject 管理系统首页。</p>
            <p>当前菜单布局：<el-tag>{{ appStore.menuMode === 'side' ? '左侧菜单' : '顶部菜单' }}</el-tag></p>
            <p>您的角色：<el-tag v-for="r in userStore.roles" :key="r.id" type="success">{{ r.name }}</el-tag></p>
            <p>权限数量：<el-tag type="info">{{ userStore.permissions.length }}</el-tag></p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>系统信息</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="后端">Django 6.1</el-descriptions-item>
            <el-descriptions-item label="前端">Vue 3 + Element Plus</el-descriptions-item>
            <el-descriptions-item label="数据库">MySQL</el-descriptions-item>
            <el-descriptions-item label="缓存">Redis</el-descriptions-item>
            <el-descriptions-item label="任务队列">Celery</el-descriptions-item>
            <el-descriptions-item label="WebSocket">Channels</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, watch, markRaw } from 'vue'
import { useUserStore } from '@/store/user'
import { useAppStore } from '@/store/app'
import request from '@/utils/request'
import { User, Bell, Document, ChatDotRound } from '@element-plus/icons-vue'

const userStore = useUserStore()
const appStore = useAppStore()

const statCards = ref([
  { title: '用户数', value: '-', icon: markRaw(User), color: '#409eff', key: 'user_count' },
  { title: '未读消息', value: '-', icon: markRaw(Bell), color: '#67c23a', key: 'unread_count' },
  { title: '今日操作', value: '-', icon: markRaw(Document), color: '#e6a23c', key: 'today_ops' },
  { title: 'AI 对话', value: '-', icon: markRaw(ChatDotRound), color: '#f56c6c', key: 'ai_sessions' },
])

const fetchStats = async () => {
  try {
    const res = await request.get('/system/dashboard/stats')
    const data = res.data || {}
    statCards.value.forEach(card => {
      const val = data[card.key]
      card.value = (val === undefined || val === null) ? 0 : val
    })
  } catch (e) {
    console.error('获取统计数据失败', e)
  }
}

onMounted(fetchStats)
// keep-alive 缓存后重新激活时刷新数据
onActivated(fetchStats)
// 切换用户后重新拉取数据（仅当仍处于登录状态时）
watch(() => userStore.userInfo?.username, (newVal) => {
  if (newVal) fetchStats()
})
</script>

<style scoped lang="scss">
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  color: #fff;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stat-title {
  font-size: 13px;
  color: var(--el-text-color-regular);
  margin-top: 4px;
}

.welcome p {
  margin-bottom: 10px;
  line-height: 1.8;
  color: var(--el-text-color-primary);
}
</style>
