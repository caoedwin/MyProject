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

// ============================================================
// 任务管理 TaskManagement
// ============================================================
// 任务种类
export function listTaskCategories(params) {
  return request({ url: '/task/categories/choices', method: 'get', params })
}
export function listAllTaskCategories(params) {
  return request({ url: '/task/categories', method: 'get', params })
}
export function createTaskCategory(data) {
  return request({ url: '/task/categories', method: 'post', data })
}
export function updateTaskCategory(id, data) {
  return request({ url: `/task/categories/${id}`, method: 'put', data })
}
export function deleteTaskCategory(id) {
  return request({ url: `/task/categories/${id}`, method: 'delete' })
}

// 任务
export function listTasks(params) {
  return request({ url: '/task/tasks', method: 'get', params })
}
export function getTaskDetail(id) {
  return request({ url: `/task/tasks/${id}`, method: 'get' })
}
export function createTask(data) {
  return request({ url: '/task/tasks', method: 'post', data })
}
export function updateTask(id, data) {
  return request({ url: `/task/tasks/${id}`, method: 'put', data })
}
export function deleteTask(id) {
  return request({ url: `/task/tasks/${id}`, method: 'delete' })
}
export function batchDeleteTasks(data) {
  return request({ url: '/task/tasks/batch_delete', method: 'post', data })
}

// 审批
export function submitApproval(id, data) {
  return request({ url: `/task/tasks/${id}/submit_approval`, method: 'post', data })
}
export function approveTask(id, data) {
  return request({ url: `/task/tasks/${id}/approve`, method: 'post', data })
}
export function rejectTask(id, data) {
  return request({ url: `/task/tasks/${id}/reject`, method: 'post', data })
}

// 进度
export function updateTaskProgress(id, data) {
  return request({ url: `/task/tasks/${id}/update_progress`, method: 'post', data })
}

// 验证
export function verifyTask(id) {
  return request({ url: `/task/tasks/${id}/verify`, method: 'post' })
}

// 导入导出
export function importTasksExcel(formData) {
  return request({ url: '/task/tasks/import_excel', method: 'post', data: formData, headers: { 'Content-Type': 'multipart/form-data' } })
}
export function exportTasksExcel(params) {
  return request({ url: '/task/tasks/export_excel', method: 'get', params, responseType: 'blob' })
}
export function downloadTaskTemplate() {
  return request({ url: '/task/tasks/template_download', method: 'get', responseType: 'blob' })
}

// 审批记录
export function listApprovals(params) {
  return request({ url: '/task/approvals', method: 'get', params })
}

// 绩效
export function listPerformances(params) {
  return request({ url: '/task/performances', method: 'get', params })
}
export function createPerformance(data) {
  return request({ url: '/task/performances', method: 'post', data })
}
export function updatePerformance(id, data) {
  return request({ url: `/task/performances/${id}`, method: 'put', data })
}

// 统计
export function getTaskStatsSummary() {
  return request({ url: '/task/stats/summary', method: 'get' })
}
export function getTaskStatsByPerson() {
  return request({ url: '/task/stats/by_person', method: 'get' })
}
export function getPerformanceSummary() {
  return request({ url: '/task/stats/performance_summary', method: 'get' })
}
export function searchUsers(params) {
  return request({ url: '/task/stats/users', method: 'get', params })
}

export function getQMUsers() {
  return request({ url: '/task/stats/qm_users', method: 'get' })
}

export function getTaskOwners() {
  return request({ url: '/task/stats/owners', method: 'get' })
}
