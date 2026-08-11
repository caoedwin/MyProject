import router from './index'
import NProgress from 'nprogress'
import { useUserStore } from '@/store/user'
import { usePermissionStore } from '@/store/permission'
import { createWebSocket, closeWebSocket } from '@/utils/websocket'

// 白名单（无需登录可访问）
const whiteList = ['/login', '/404', '/403']

router.beforeEach(async (to, from, next) => {
  NProgress.start()
  document.title = to.meta.title ? `${to.meta.title} - MyProject` : 'MyProject'

  const userStore = useUserStore()
  const permissionStore = usePermissionStore()

  // 已登录
  if (userStore.token) {
    if (to.path === '/login') {
      next({ path: '/' })
      NProgress.done()
      return
    }
    // 已加载过权限路由
    if (permissionStore.loaded) {
      next()
      return
    }
    try {
      // 拉取用户信息（防止刷新丢失）
      if (!userStore.userInfo) {
        await userStore.fetchUserInfo()
      }
      // 生成动态路由
      const dynamicRoutes = await permissionStore.generateRoutes()
      // 初始化 WebSocket（登录后建立连接）
      createWebSocket()
      // 动态添加路由
      dynamicRoutes.forEach(route => {
        // 包装到根布局下
        router.addRoute({
          path: '/',
          component: () => import('@/layout/index.vue'),
          children: [route],
        })
      })
      // 兜底 404
      router.addRoute({ path: '/:pathMatch(.*)*', redirect: '/404' })
      // 重新跳转，确保新路由生效
      next({ ...to, replace: true })
    } catch (e) {
      console.error('路由守卫异常:', e)
      closeWebSocket()
      userStore.resetState()
      next(`/login?redirect=${to.path}`)
      NProgress.done()
    }
    return
  }

  // 未登录
  if (whiteList.includes(to.path)) {
    next()
  } else {
    // 尝试记住密码免登录
    const remembered = await userStore.tryRememberLogin()
    if (remembered) {
      next({ ...to, replace: true })
    } else {
      next(`/login?redirect=${to.path}`)
    }
    NProgress.done()
  }
})

router.afterEach(() => {
  NProgress.done()
})
