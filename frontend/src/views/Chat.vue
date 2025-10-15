<template>
  <div class="chat-page">
    <el-header class="header">
      <div class="header-left">
        <h1>AI智能助手</h1>
      </div>
      <div class="header-right">
        <el-button @click="goToAnalysis" type="info" plain>
          <el-icon><Document /></el-icon>
          文本分析
        </el-button>
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ authStore.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container>
      <el-main class="chat-main">
        <div class="chat-container">
          <!-- 聊天消息区域 -->
          <div class="chat-messages" ref="messagesContainer">
            <!-- 欢迎消息 -->
            <div v-if="messages.length === 0" class="welcome-message">
              <div class="welcome-card">
                <el-icon class="welcome-icon" size="48"><ChatDotRound /></el-icon>
                <h2>你好！我是小宝，你的AI助手</h2>
                <p>我可以帮助你解答各种问题，提供信息和建议。有什么我可以帮助你的吗？</p>
                <div class="quick-questions">
                  <h4>你可以试试这些问题：</h4>
                  <el-button 
                    v-for="question in quickQuestions" 
                    :key="question"
                    @click="sendQuickQuestion(question)"
                    type="primary" 
                    plain 
                    size="small"
                    class="quick-question-btn"
                  >
                    {{ question }}
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 聊天消息列表 -->
            <div 
              v-for="(message, index) in messages" 
              :key="index" 
              class="message-wrapper"
              :class="{ 'user-message': message.role === 'user', 'assistant-message': message.role === 'assistant' }"
            >
              <div class="message-bubble">
                <div v-if="message.role === 'user'" class="message-header">
                  <el-icon class="user-avatar"><User /></el-icon>
                  <span class="message-sender">你</span>
                </div>
                <div v-else class="message-header">
                  <el-icon class="assistant-avatar"><Robot /></el-icon>
                  <span class="message-sender">小宝</span>
                </div>
                
                <div class="message-content">
                  <div v-if="message.role === 'assistant'" v-html="formatMessage(message.content)"></div>
                  <div v-else>{{ message.content }}</div>
                </div>
                
                <div class="message-time">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
            </div>

            <!-- 正在输入指示器 -->
            <div v-if="isTyping" class="message-wrapper assistant-message">
              <div class="message-bubble typing-indicator">
                <div class="message-header">
                  <el-icon class="assistant-avatar"><Robot /></el-icon>
                  <span class="message-sender">小宝</span>
                </div>
                <div class="message-content">
                  <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input-area">
            <div class="input-container">
              <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="1"
                :autosize="{ minRows: 1, maxRows: 4 }"
                placeholder="输入你的问题，按Enter发送，Shift+Enter换行..."
                @keydown="handleKeydown"
                :disabled="isSending"
                class="message-input"
                resize="none"
              />
              <div class="input-actions">
                <el-button
                  :loading="isSending"
                  type="primary"
                  @click="sendMessage"
                  :disabled="!inputMessage.trim()"
                  class="send-button"
                >
                  <el-icon v-if="!isSending"><Promotion /></el-icon>
                  <span v-if="isSending">发送中...</span>
                  <span v-else>发送</span>
                </el-button>
                <el-button
                  @click="clearChat"
                  :disabled="messages.length === 0"
                  type="info"
                  plain
                >
                  <el-icon><Delete /></el-icon>
                  清空
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { api } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, ArrowDown, SwitchButton, Document, ChatDotRound, 
  Robot, Promotion, Delete 
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const messages = ref([])
const inputMessage = ref('')
const isSending = ref(false)
const isTyping = ref(false)
const messagesContainer = ref(null)

// 快速问题建议
const quickQuestions = [
  '介绍一下你自己',
  '今天天气怎么样？',
  '推荐一些学习英语的方法',
  '什么是人工智能？'
]

const sendQuickQuestion = (question) => {
  inputMessage.value = question
  sendMessage()
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isSending.value) return

  const userMessage = {
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date()
  }

  // 添加用户消息到聊天记录
  messages.value.push(userMessage)
  
  // 清空输入框
  const messageToSend = inputMessage.value.trim()
  inputMessage.value = ''
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    isSending.value = true
    isTyping.value = true

    // 准备对话历史（只包含role和content）
    const conversationHistory = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    console.log('发送流式聊天请求:', { messageToSend, conversationHistory: conversationHistory.slice(0, -1) })

    // 调用流式API
    const response = await api.chat.sendStreamMessage(messageToSend, conversationHistory.slice(0, -1))
    
    console.log('收到响应:', response)
    
    // 创建AI回复消息
    const assistantMessage = {
      role: 'assistant',
      content: '',
      timestamp: new Date()
    }
    
    messages.value.push(assistantMessage)
    isTyping.value = false

    // 处理流式响应
    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    console.log('开始读取流式数据...')

    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        console.log('流式数据读取完成')
        break
      }

      const chunk = decoder.decode(value)
      console.log('收到数据块:', chunk)
      
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6).trim()
            if (jsonStr) {
              console.log('解析JSON:', jsonStr)
              const data = JSON.parse(jsonStr)
              
              if (data.error) {
                throw new Error(data.error)
              }
              
              if (data.content) {
                // 更新最后一条AI消息的内容
                const lastMessage = messages.value[messages.value.length - 1]
                lastMessage.content += data.content
                
                // 滚动到底部
                await nextTick()
                scrollToBottom()
              }
              
              if (data.done) {
                console.log('收到完成标志')
                break
              }
            }
          } catch (e) {
            console.error('解析流式数据失败:', e, '原始行:', line)
          }
        }
      }
    }

  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败，请稍后重试')
    
    // 移除可能添加的空AI消息
    if (messages.value.length > 0 && messages.value[messages.value.length - 1].role === 'assistant' && !messages.value[messages.value.length - 1].content) {
      messages.value.pop()
    }
  } finally {
    isSending.value = false
    isTyping.value = false
  }
}

const clearChat = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有聊天记录吗？', '确认', {
      type: 'warning'
    })
    
    messages.value = []
    ElMessage.success('聊天记录已清空')
  } catch (error) {
    // 用户取消
  }
}

const handleKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatMessage = (content) => {
  if (!content) return ''
  
  // 简单的markdown格式化
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const now = new Date()
  const diff = now - timestamp
  
  if (diff < 60000) { // 1分钟内
    return '刚刚'
  } else if (diff < 3600000) { // 1小时内
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) { // 24小时内
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return timestamp.toLocaleString()
  }
}

const goToAnalysis = () => {
  router.push('/dashboard')
}

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '确认', {
        type: 'warning'
      })
      
      await authStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (error) {
      // 用户取消
    }
  }
}

onMounted(() => {
  // 验证token有效性
  authStore.verifyToken()
})
</script>

<style scoped>
.chat-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-left h1 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-right .user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
}

.header-right .user-info:hover {
  color: #409eff;
}

.header-right .user-info .el-icon {
  margin: 0 5px;
}

.chat-main {
  padding: 0;
  height: calc(100vh - 60px);
}

.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.welcome-card {
  text-align: center;
  padding: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px;
  max-width: 500px;
}

.welcome-icon {
  margin-bottom: 20px;
  color: rgba(255, 255, 255, 0.9);
}

.welcome-card h2 {
  margin: 0 0 16px 0;
  font-size: 24px;
  font-weight: 600;
}

.welcome-card p {
  margin: 0 0 30px 0;
  font-size: 16px;
  opacity: 0.9;
  line-height: 1.6;
}

.quick-questions h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  opacity: 0.9;
}

.quick-question-btn {
  margin: 4px;
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.quick-question-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.message-wrapper {
  display: flex;
}

.user-message {
  justify-content: flex-end;
}

.assistant-message {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #f0f0f0;
}

.user-message .message-bubble {
  background: linear-gradient(135deg, #409eff 0%, #36a3f7 100%);
  color: white;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}

.user-avatar {
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  padding: 4px;
}

.assistant-avatar {
  width: 24px;
  height: 24px;
  background: #f0f9ff;
  color: #409eff;
  border-radius: 50%;
  padding: 4px;
}

.message-sender {
  font-size: 12px;
  font-weight: 600;
  opacity: 0.8;
}

.message-content {
  margin: 8px 0;
  line-height: 1.6;
  word-wrap: break-word;
}

.message-content :deep(strong) {
  font-weight: 600;
}

.message-content :deep(em) {
  font-style: italic;
}

.message-content :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.user-message .message-content :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

.message-time {
  font-size: 11px;
  opacity: 0.6;
  text-align: right;
}

.typing-indicator .message-content {
  display: flex;
  align-items: center;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: #409eff;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input-area {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
}

.input-actions {
  display: flex;
  gap: 8px;
}

.send-button {
  height: 40px;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    margin: 0;
    border-radius: 0;
    height: 100%;
  }
  
  .message-bubble {
    max-width: 85%;
  }
  
  .welcome-card {
    padding: 30px 20px;
  }
  
  .input-container {
    flex-direction: column;
    gap: 12px;
  }
  
  .input-actions {
    justify-content: stretch;
  }
  
  .input-actions .el-button {
    flex: 1;
  }
}
</style>
