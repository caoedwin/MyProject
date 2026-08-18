<template>
  <div class="navbar">
    <div class="navbar-left">
      <!-- 折叠按钮（仅左侧菜单模式显示） -->
      <el-icon class="trigger" v-if="appStore.menuMode === 'side'" @click="appStore.toggleCollapse()">
        <Fold v-if="!appStore.menuCollapsed" />
        <Expand v-else />
      </el-icon>

      <!-- 顶部菜单模式：显示顶级菜单 -->
      <el-menu
        v-if="appStore.menuMode === 'top'"
        :default-active="activeTopMenu"
        mode="horizontal"
        @select="handleTopMenuSelect"
        background-color="transparent"
        :text-color="appStore.isDark ? '#e5eaf3' : '#303133'"
        active-text-color="#409EFF"
      >
        <template v-for="item in topMenus" :key="item.path">
          <!-- 有子菜单：使用 el-sub-menu -->
          <el-sub-menu
            v-if="item.children && item.children.length"
            :index="item.path || String(item.id)"
            :teleported="false"
          >
            <template #title>
              <el-icon v-if="item.icon"><component :is="item.icon" /></el-icon>
              <span>{{ item.name }}</span>
            </template>
            <el-menu-item
              v-for="child in item.children"
              :key="child.path"
              :index="child.path"
            >
              <span>{{ child.name }}</span>
            </el-menu-item>
          </el-sub-menu>
          <!-- 无子菜单：直接跳转 -->
          <el-menu-item v-else :index="item.path">
            <el-icon v-if="item.icon"><component :is="item.icon" /></el-icon>
            <span>{{ item.name }}</span>
          </el-menu-item>
        </template>
      </el-menu>

      <!-- 面包屑 -->
      <el-breadcrumb v-else separator="/" class="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-for="item in breadcrumbItems" :key="item.path">
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="navbar-right">
      <!-- 菜单布局切换 -->
      <el-tooltip :content="appStore.menuMode === 'side' ? '切换到顶部菜单' : '切换到左侧菜单'" placement="bottom">
        <el-icon class="action-item" @click="toggleMenuMode">
          <Operation />
        </el-icon>
      </el-tooltip>

      <!-- 消息通知 -->
      <el-badge :value="messageStore.unreadCount" :hidden="messageStore.unreadCount === 0" class="action-item">
        <el-icon @click="router.push('/message')"><Bell /></el-icon>
      </el-badge>

      <!-- 全屏 -->
      <el-tooltip content="全屏" placement="bottom">
        <el-icon class="action-item" @click="toggleFullscreen"><FullScreen /></el-icon>
      </el-tooltip>

      <!-- 日夜切换 -->
      <el-tooltip :content="appStore.isDark ? '切换日间模式' : '切换夜间模式'" placement="bottom">
        <el-icon class="action-item" @click="appStore.toggleTheme()">
          <Sunny v-if="appStore.isDark" />
          <Moon v-else />
        </el-icon>
      </el-tooltip>

      <!-- 用户菜单 -->
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="30" :src="userStore.userInfo?.avatar">
            {{ userStore.userInfo?.nickname?.charAt(0) || 'U' }}
          </el-avatar>
          <span class="username">{{ userStore.userInfo?.nickname || userStore.userInfo?.username }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile" :icon="User">个人中心</el-dropdown-item>
            <el-dropdown-item command="password" :icon="Lock">修改密码</el-dropdown-item>
            <el-dropdown-item divided command="logout" :icon="SwitchButton">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="420px">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwdLoading" @click="submitPassword">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Fold, Expand, Operation, Bell, FullScreen, ArrowDown,
  User, Lock, SwitchButton, Sunny, Moon,
} from '@element-plus/icons-vue'
import { useAppStore } from '@/store/app'
import { useUserStore } from '@/store/user'
import { usePermissionStore } from '@/store/permission'
import { useMessageStore } from '@/store/message'
import { changePassword } from '@/api'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()
const permissionStore = usePermissionStore()
const messageStore = useMessageStore()

const topMenus = computed(() => permissionStore.menus)
const activeTopMenu = ref('')

// 面包屑
const breadcrumbItems = computed(() => {
  return route.matched
    .filter(r => r.meta && r.meta.title && !r.meta.hidden)
    .map(r => ({ path: r.path, title: r.meta.title }))
})

// 顶部菜单选中
function handleTopMenuSelect(path) {
  const menu = topMenus.value.find(m => m.path === path)
  if (menu && menu.is_external) {
    window.open(path, '_blank', 'noopener')
  } else {
    router.push(path)
  }
}

// 切换菜单布局
async function toggleMenuMode() {
  const newMode = appStore.menuMode === 'side' ? 'top' : 'side'
  appStore.setMenuMode(newMode)
  // 持久化到后端
  try {
    await import('@/api').then(m => m.updatePreferences({ menu_mode: newMode }))
  } catch (e) {
    // 持久化失败不影响使用
  }
}

// 全屏
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

// 用户菜单
async function handleCommand(command) {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'password') {
    pwdDialogVisible.value = true
  } else if (command === 'logout') {
    await ElMessageBox.confirm('确认退出登录？', '提示', { type: 'warning' })
    await userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}

// 修改密码
const pwdDialogVisible = ref(false)
const pwdLoading = ref(false)
const pwdFormRef = ref()
const pwdForm = reactive({ old_password: '', new_password: '' })
const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
}

async function submitPassword() {
  await pwdFormRef.value.validate()
  pwdLoading.value = true
  try {
    await changePassword(pwdForm)
    ElMessage.success('密码修改成功，请重新登录')
    await userStore.logout()
    router.push('/login')
  } catch (e) {
    // ignore
  } finally {
    pwdLoading.value = false
  }
}

// 未读消息数：状态放在 messageStore，方便消息页「标记已读」后即时刷新铃铛
// Navbar 只负责启动轮询定时器
let pollTimer = null

onMounted(() => {
  messageStore.fetchUnread()
  pollTimer = setInterval(() => messageStore.fetchUnread(), 30000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped lang="scss">
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
  overflow: visible;
}

.trigger {
  font-size: 20px;
  cursor: pointer;
  color: var(--el-text-color-primary);
}

.breadcrumb {
  line-height: 50px;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
  overflow: visible;
}

.action-item {
  font-size: 18px;
  cursor: pointer;
  color: var(--el-text-color-primary);
  &:hover {
    color: #409eff;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  .username {
    font-size: 14px;
    color: var(--el-text-color-primary);
  }
}

:deep(.el-menu--horizontal) {
  border-bottom: none;
}

:deep(.el-badge) {
  display: inline-flex;
  align-items: center;
  overflow: visible;
}

:deep(.el-badge__content) {
  top: auto;
  bottom: -2px;
  transform: translate(50%, 0);
  pointer-events: none;
}
</style>
