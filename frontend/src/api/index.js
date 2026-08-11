import request from '@/utils/request'

// 登录
export function login(data) {
  return request({ url: '/auth/login', method: 'post', data })
}

// 注册
export function register(data) {
  return request({ url: '/auth/register', method: 'post', data })
}

// 登出
export function logout(data) {
  return request({ url: '/auth/logout', method: 'post', data })
}

// 记住密码免登录
export function rememberLogin(data) {
  return request({ url: '/auth/remember-login', method: 'post', data })
}

// 刷新 token
export function refreshToken(data) {
  return request({ url: '/auth/refresh', method: 'post', data })
}

// 当前用户信息
export function getUserInfo() {
  return request({ url: '/auth/user', method: 'get' })
}

// 更新菜单偏好（顶部 / 左侧 / 收起）
export function updatePreferences(data) {
  return request({ url: '/auth/user/preferences', method: 'patch', data })
}

// 修改密码
export function changePassword(data) {
  return request({ url: '/auth/user/password', method: 'post', data })
}

// 当前用户菜单树 + 权限
export function getUserMenus() {
  return request({ url: '/system/user-menus', method: 'get' })
}

// 菜单管理
export function listMenus(params) {
  return request({ url: '/system/menus', method: 'get', params })
}
export function createMenu(data) {
  return request({ url: '/system/menus', method: 'post', data })
}
export function updateMenu(id, data) {
  return request({ url: `/system/menus/${id}`, method: 'put', data })
}
export function deleteMenu(id) {
  return request({ url: `/system/menus/${id}`, method: 'delete' })
}

// 角色管理
export function listRoles(params) {
  return request({ url: '/system/roles', method: 'get', params })
}
export function createRole(data) {
  return request({ url: '/system/roles', method: 'post', data })
}
export function updateRole(id, data) {
  return request({ url: `/system/roles/${id}`, method: 'put', data })
}
export function deleteRole(id) {
  return request({ url: `/system/roles/${id}`, method: 'delete' })
}

// 操作日志
export function listOperationLogs(params) {
  return request({ url: '/system/operation-logs', method: 'get', params })
}

// 登录日志
export function listLoginLogs(params) {
  return request({ url: '/system/login-logs', method: 'get', params })
}

// 消息
export function listMessages(params) {
  return request({ url: '/messaging/messages', method: 'get', params })
}
export function sendMessage(data) {
  return request({ url: '/messaging/messages/send', method: 'post', data })
}
export function broadcastMessage(data) {
  return request({ url: '/messaging/messages/broadcast', method: 'post', data })
}
export function markMessageRead(id) {
  return request({ url: `/messaging/messages/${id}/read`, method: 'post' })
}
export function getUnreadCount() {
  return request({ url: '/messaging/messages/unread-count', method: 'get' })
}

// AI 对话
export function aiAsk(data) {
  return request({ url: '/ai/chat/ask', method: 'post', data })
}
export function listChatSessions() {
  return request({ url: '/ai/chat', method: 'get' })
}
export function deleteChatSession(id) {
  return request({ url: `/ai/chat/${id}`, method: 'delete' })
}
