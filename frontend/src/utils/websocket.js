/**
 * WebSocket 客户端 - 消息推送
 * 用法：
 *   const ws = createWebSocket()
 *   ws.onMessage((data) => console.log(data))
 *   ws.send({ type: 'ping' })
 */
import { useUserStore } from '@/store/user'
import { ElNotification } from 'element-plus'

let socket = null
let reconnectTimer = null
let messageHandlers = []

export function createWebSocket() {
  if (socket && socket.readyState === WebSocket.OPEN) return socket

  const userStore = useUserStore()
  if (!userStore.token) return null

  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const url = `${protocol}//${location.host}/ws/notifications/?token=${userStore.token}`

  socket = new WebSocket(url)

  socket.onopen = () => {
    console.log('[WS] 已连接')
    // 启动心跳
    startHeartbeat()
  }

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'message' || data.type === 'broadcast') {
        // 弹通知
        ElNotification({
          title: data.message.title || '新消息',
          message: data.message.content,
          type: 'info',
          duration: 5000,
        })
      }
      // 分发给业务处理器
      messageHandlers.forEach(fn => fn(data))
    } catch (e) {
      console.error('[WS] 消息解析失败', e)
    }
  }

  socket.onclose = (e) => {
    console.log('[WS] 已断开', e.code)
    stopHeartbeat()
    // 非主动关闭则重连
    if (e.code !== 1000) {
      reconnectTimer = setTimeout(() => createWebSocket(), 5000)
    }
  }

  socket.onerror = (e) => {
    console.error('[WS] 错误', e)
  }

  return socket
}

let heartbeatTimer = null
function startHeartbeat() {
  heartbeatTimer = setInterval(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }))
    }
  }, 30000)
}

function stopHeartbeat() {
  if (heartbeatTimer) clearInterval(heartbeatTimer)
}

export function closeWebSocket() {
  if (reconnectTimer) clearTimeout(reconnectTimer)
  stopHeartbeat()
  if (socket) {
    socket.close(1000)
    socket = null
  }
}

export function onMessage(handler) {
  messageHandlers.push(handler)
  return () => {
    messageHandlers = messageHandlers.filter(fn => fn !== handler)
  }
}
