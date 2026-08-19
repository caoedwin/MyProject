import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import Cookies from 'js-cookie'
import {
  login as loginApi, logout as logoutApi, getUserInfo,
  rememberLogin as rememberLoginApi,
} from '@/api'
import { useAppStore } from '@/store/app'

const TOKEN_KEY = 'myproject_token'
const REFRESH_TOKEN_KEY = 'myproject_refresh'
const REMEMBER_KEY = 'myproject_remember'
const USER_KEY = 'myproject_user'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const refreshToken = ref(localStorage.getItem(REFRESH_TOKEN_KEY) || '')
  const userInfo = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))
  const permissions = ref([])
  const roles = ref([])

  const isLogin = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.is_superuser || roles.value.some(r => r.code === 'admin'))

  // 设置 token
  function setToken(access, refresh) {
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem(TOKEN_KEY, access)
    if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  }

  // 应用账户级菜单偏好（菜单位置、是否收缩）
  function applyMenuPreferences(user) {
    if (!user) return
    const appStore = useAppStore()
    if (user.menu_mode) {
      appStore.setMenuMode(user.menu_mode)
    }
    if (user.menu_collapsed !== undefined) {
      appStore.setCollapsed(user.menu_collapsed)
    }
  }

  // 登录
  async function login(loginForm) {
    const res = await loginApi(loginForm)
    setToken(res.data.access, res.data.refresh)
    userInfo.value = res.data.user
    localStorage.setItem(USER_KEY, JSON.stringify(res.data.user))
    applyMenuPreferences(res.data.user)

    // 记住密码：保存 remember_token 到 Cookie（比 localStorage 更安全，可设过期）
    if (loginForm.rememberMe && res.data.remember_token) {
      Cookies.set(REMEMBER_KEY, res.data.remember_token, { expires: 30, sameSite: 'strict' })
    } else {
      Cookies.remove(REMEMBER_KEY)
    }
    return res
  }

  // 记住密码免登录
  async function tryRememberLogin() {
    const rememberToken = Cookies.get(REMEMBER_KEY)
    if (!rememberToken) return false
    try {
      const res = await rememberLoginApi({ remember_token: rememberToken })
      setToken(res.data.access, res.data.refresh)
      userInfo.value = res.data.user
      localStorage.setItem(USER_KEY, JSON.stringify(res.data.user))
      applyMenuPreferences(res.data.user)
      return true
    } catch (e) {
      Cookies.remove(REMEMBER_KEY)
      return false
    }
  }

  // 获取用户信息
  async function fetchUserInfo() {
    const res = await getUserInfo()
    userInfo.value = res.data
    roles.value = res.data.roles || []
    localStorage.setItem(USER_KEY, JSON.stringify(res.data))
    applyMenuPreferences(res.data)
    return res.data
  }

  // 设置权限
  function setPermissions(perms) {
    permissions.value = perms || []
  }

  // 检查权限
  function hasPermission(perm) {
    if (isAdmin.value) return true
    if (!perm) return true
    return permissions.value.includes('*') || permissions.value.includes(perm)
  }

  // 登出
  async function logout() {
    try {
      if (token.value) {
        await logoutApi({ refresh: refreshToken.value })
      }
    } catch (e) {
      // 忽略登出失败
    }
    resetState()
    Cookies.remove(REMEMBER_KEY)
    // 重置权限路由，确保下个用户登录时重新生成菜单
    const { usePermissionStore } = await import('@/store/permission')
    usePermissionStore().reset()
  }

  function resetState() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    permissions.value = []
    roles.value = []
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return {
    token, refreshToken, userInfo, permissions, roles,
    isLogin, isAdmin,
    setToken, login, tryRememberLogin, fetchUserInfo,
    setPermissions, hasPermission, logout, resetState,
    applyMenuPreferences,
  }
})
