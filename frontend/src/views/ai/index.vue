<template>
  <div class="ai-chat">
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="flex-between">
              <span>会话历史</span>
              <el-button type="primary" size="small" @click="newSession">新建</el-button>
            </div>
          </template>
          <el-menu :default-active="String(currentSessionId)" @select="handleSelectSession">
            <el-menu-item v-for="s in sessions" :key="s.id" :index="String(s.id)">
              <span>{{ s.title || '新对话' }}</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-card class="chat-area">
          <div class="messages" ref="messagesRef">
            <div v-for="msg in currentMessages" :key="msg.id" :class="['msg', msg.role === 1 ? 'msg-user' : 'msg-ai']">
              <div class="msg-content" v-html="renderMarkdown(msg.content)"></div>
            </div>
            <div v-if="streaming" class="msg msg-ai">
              <div class="msg-content">{{ streamContent }}<span class="cursor">|</span></div>
            </div>
          </div>
          <div class="input-area">
            <el-input
              v-model="inputText"
              type="textarea"
              :rows="3"
              placeholder="输入消息，Ctrl+Enter 发送"
              @keydown.ctrl.enter="handleSend"
            />
            <el-button type="primary" :loading="streaming" @click="handleSend">发送</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { listChatSessions, aiAsk } from '@/api'

const sessions = ref([])
const currentSessionId = ref(null)
const currentMessages = ref([])
const inputText = ref('')
const streaming = ref(false)
const streamContent = ref('')
const messagesRef = ref()

function renderMarkdown(text) {
  try {
    return marked(text || '')
  } catch {
    return text
  }
}

async function fetchSessions() {
  const res = await listChatSessions()
  sessions.value = res.data || []
  if (sessions.value.length > 0) {
    handleSelectSession(String(sessions.value[0].id))
  }
}

function handleSelectSession(id) {
  currentSessionId.value = Number(id)
  const session = sessions.value.find(s => s.id === currentSessionId.value)
  currentMessages.value = session?.messages || []
  scrollToBottom()
}

function newSession() {
  currentSessionId.value = null
  currentMessages.value = []
  streamContent.value = ''
}

async function handleSend() {
  const content = inputText.value.trim()
  if (!content || streaming.value) return

  currentMessages.value.push({ id: Date.now(), role: 1, content })
  inputText.value = ''
  streaming.value = true
  streamContent.value = ''
  scrollToBottom()

  try {
    // 流式调用
    const resp = await fetch('/api/ai/chat/ask-stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('myproject_token')}`,
      },
      body: JSON.stringify({
        content,
        session_id: currentSessionId.value,
      }),
    })

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.content) {
              streamContent.value += data.content
              scrollToBottom()
            }
            if (data.done) {
              currentSessionId.value = data.session_id
              currentMessages.value.push({
                id: Date.now(),
                role: 2,
                content: streamContent.value,
              })
              streamContent.value = ''
              fetchSessions()
            }
            if (data.error) {
              ElMessage.error(data.error)
            }
          } catch (e) {
            // ignore parse error
          }
        }
      }
    }
  } catch (e) {
    ElMessage.error('请求失败')
  } finally {
    streaming.value = false
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

onMounted(fetchSessions)
</script>

<style scoped lang="scss">
.ai-chat {
  height: calc(100vh - 82px);
}

.chat-area {
  height: 100%;
  display: flex;
  flex-direction: column;
  :deep(.el-card__body) {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 0;
  }
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.msg {
  margin-bottom: 16px;
  display: flex;
}

.msg-user {
  justify-content: flex-end;
  .msg-content {
    background: #409eff;
    color: #fff;
  }
}

.msg-ai {
  justify-content: flex-start;
  .msg-content {
    background: #f4f4f5;
    color: #303133;
  }
}

.msg-content {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 8px;
  line-height: 1.6;
  word-break: break-word;
}

.cursor {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.input-area {
  padding: 12px;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 8px;
  align-items: flex-end;
}
</style>
