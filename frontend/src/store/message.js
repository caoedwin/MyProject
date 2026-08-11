import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getUnreadCount } from '@/api'
import { useUserStore } from '@/store/user'

// 消息中心 - 全局未读消息数（菜单栏铃铛徽标）
// 提升到 store 是为了让消息页「标记已读」后能即时通知铃铛刷新，
// 而不必等待 Navbar 的 30s 轮询或刷新整页。
export const useMessageStore = defineStore('message', () => {
  const unreadCount = ref(0)

  // 拉取未读数；未登录时跳过
  async function fetchUnread() {
    const userStore = useUserStore()
    if (!userStore.token) return
    try {
      const res = await getUnreadCount()
      unreadCount.value = res.data.unread
    } catch (e) {
      // 忽略：徽标更新失败不影响主流程
    }
  }

  return { unreadCount, fetchUnread }
})
