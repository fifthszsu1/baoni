import { defineStore } from 'pinia'
import { api } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || null,
    isLoading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    async login(credentials) {
      try {
        this.isLoading = true
        const response = await api.auth.login(credentials)
        
        if (response.success) {
          this.token = response.token
          this.username = response.username
          
          // 保存到本地存储
          localStorage.setItem('token', response.token)
          localStorage.setItem('username', response.username)
          
          // 设置API默认认证头
          api.setAuthToken(response.token)
          
          return { success: true, message: response.message }
        } else {
          return { success: false, error: response.error }
        }
      } catch (error) {
        console.error('登录失败:', error)
        return { 
          success: false, 
          error: error.response?.data?.error || '登录失败，请检查网络连接' 
        }
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      this.token = null
      this.username = null
      
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      
      // 清除API认证头
      api.setAuthToken(null)
    },

    async verifyToken() {
      if (!this.token) return false
      
      try {
        const response = await api.auth.verifyToken()
        return response.success
      } catch (error) {
        console.error('Token验证失败:', error)
        this.logout()
        return false
      }
    },

    // 初始化时恢复认证状态
    initializeAuth() {
      if (this.token) {
        api.setAuthToken(this.token)
      }
    }
  }
}) 