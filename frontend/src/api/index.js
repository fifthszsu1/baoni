import axios from 'axios'

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || (process.env.NODE_ENV === 'development' ? 'http://localhost:5001' : ''),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    // 添加认证头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效，清除本地存储并跳转登录
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API封装
export const api = {
  // 设置认证Token
  setAuthToken(token) {
    if (token) {
      axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete axiosInstance.defaults.headers.common['Authorization']
    }
  },

  // 认证相关接口
  auth: {
    // 用户登录
    login(credentials) {
      return axiosInstance.post('/api/auth/login', credentials)
    },
    
    // 验证Token
    verifyToken() {
      return axiosInstance.get('/api/auth/verify')
    }
  },

  // 文本分析相关接口
  analysis: {
    // 分析文本
    analyzeText(text) {
      return axiosInstance.post('/api/analyze/text', { text })
    },
    
    // 图片文字识别
    extractTextFromImage(imageFile) {
      const formData = new FormData()
      formData.append('image', imageFile)
      
      return axiosInstance.post('/api/analyze/ocr', formData, {
        headers: {
          'Content-Type': undefined // 删除默认的Content-Type，让浏览器自动设置multipart/form-data
        },
        timeout: 60000 // OCR可能需要更长时间
      })
    },
    
    // 测试连接
    testConnection() {
      return axiosInstance.get('/api/analyze/test')
    }
  },

  // 聊天相关接口
  chat: {
    // 发送消息（普通模式）
    sendMessage(message, conversationHistory = []) {
      return axiosInstance.post('/api/chat/message', {
        message,
        conversation_history: conversationHistory
      })
    },

    // 发送消息（流式模式）
    async sendStreamMessage(message, conversationHistory = []) {
      const token = localStorage.getItem('token')
      const baseURL = process.env.VUE_APP_API_BASE_URL || (process.env.NODE_ENV === 'development' ? 'http://localhost:5001' : '')
      
      const response = await fetch(`${baseURL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message,
          conversation_history: conversationHistory
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return response
    },

    // 测试聊天连接
    testChatConnection() {
      return axiosInstance.get('/api/chat/test')
    }
  }
}

export default axiosInstance 