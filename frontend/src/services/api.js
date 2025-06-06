/**
 * RepoChat API Service
 * Centralized HTTP client for all backend communications
 */

import axios from 'axios'
import { config } from '@config/environment.js'

// Create axios instance với configuration từ environment
const apiClient = axios.create({
  baseURL: config.api.baseURL,
  timeout: config.api.timeout,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Request interceptor để add authentication token và logging
apiClient.interceptors.request.use(
  (config) => {
    // Add timestamp để prevent caching
    config.metadata = { startTime: Date.now() }
    
    // Add authentication token if available
    const token = localStorage.getItem('repochat_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Development logging
    if (import.meta.env.DEV && config.features?.logging) {
      console.log('📤 API Request:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        baseURL: config.baseURL,
        data: config.data
      })
    }
    
    return config
  },
  (error) => {
    console.error('❌ Request Interceptor Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor để handle common errors và logging
apiClient.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const duration = Date.now() - response.config.metadata.startTime
    
    // Development logging
    if (import.meta.env.DEV && config.features?.logging) {
      console.log('📥 API Response:', {
        status: response.status,
        duration: `${duration}ms`,
        url: response.config.url,
        data: response.data
      })
    }
    
    return response
  },
  (error) => {
    const duration = error.config?.metadata ? 
      Date.now() - error.config.metadata.startTime : 0
    
    // Enhanced error logging
    console.error('❌ API Error:', {
      status: error.response?.status,
      message: error.message,
      duration: `${duration}ms`,
      url: error.config?.url,
      data: error.response?.data
    })
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('repochat_token')
      window.dispatchEvent(new CustomEvent('auth:logout'))
    } else if (error.response?.status === 403) {
      // Forbidden - user doesn't have permission
      console.warn('Access forbidden. Check user permissions.')
    } else if (error.response?.status >= 500) {
      // Server errors
      console.error('Server error. Please try again later.')
    }
    
    return Promise.reject(error)
  }
)

/**
 * Main API Service Object
 */
export const apiService = {
  
  // === Health & Status ===
  
  /**
   * Check backend health status
   */
  async healthCheck() {
    try {
      const response = await apiClient.get('/health')
      return {
        success: true,
        data: response.data,
        status: response.status
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error),
        status: error.response?.status || 0
      }
    }
  },

  /**
   * Get system status và statistics
   */
  async getSystemStatus() {
    try {
      const response = await apiClient.get('/api/system/status')
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      }
    }
  },

  // === Repository Operations ===

  /**
   * Scan repository for analysis
   */
  async scanRepository(repositoryUrl, options = {}) {
    try {
      const payload = {
        repository_url: repositoryUrl,
        ...options
      }
      
      const response = await apiClient.post('/api/repository/scan', payload)
      return {
        success: true,
        data: response.data,
        scanId: response.data?.scan_id
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error),
        details: error.response?.data
      }
    }
  },

  /**
   * Get scan status và results
   */
  async getScanStatus(scanId) {
    try {
      const response = await apiClient.get(`/api/repository/scan/${scanId}/status`)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      }
    }
  },

  /**
   * Get analysis results for repository
   */
  async getAnalysisResults(scanId) {
    try {
      const response = await apiClient.get(`/api/repository/scan/${scanId}/results`)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      }
    }
  },

  // === Chat Operations ===

  /**
   * Send chat message for repository analysis
   */
  async sendChatMessage(message, repositoryContext = null) {
    try {
      const payload = {
        message,
        context: repositoryContext,
        timestamp: new Date().toISOString()
      }
      
      const response = await apiClient.post('/api/chat/message', payload)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      }
    }
  },

  /**
   * Get chat history
   */
  async getChatHistory(sessionId = null) {
    try {
      const params = sessionId ? { session_id: sessionId } : {}
      const response = await apiClient.get('/api/chat/history', { params })
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      }
    }
  },

  // === Q&A Operations ===

  /**
   * Ask question about codebase
   */
  async askQuestion(question, repositoryContext = null) {
    try {
      const payload = {
        question,
        context: repositoryContext,
        timestamp: new Date().toISOString()
      }
      
      const response = await apiClient.post('/api/qa/ask', payload)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      }
    }
  },

  // === Settings Operations ===

  /**
   * Get user settings
   */
  async getSettings() {
    try {
      const response = await apiClient.get('/api/settings')
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      }
    }
  },

  /**
   * Update user settings
   */
  async updateSettings(settings) {
    try {
      const response = await apiClient.put('/api/settings', settings)
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      }
    }
  },

  // === File Operations ===

  /**
   * Get file content từ repository
   */
  async getFileContent(filePath, repositoryContext) {
    try {
      const params = {
        file_path: filePath,
        repository_url: repositoryContext?.repository_url
      }
      
      const response = await apiClient.get('/api/repository/file', { params })
      return {
        success: true,
        data: response.data
      }
    } catch (error) {
      return {
        success: false,
        error: this.getErrorMessage(error)
      }
    }
  },

  // === Utility Functions ===

  /**
   * Extract user-friendly error message
   */
  getErrorMessage(error) {
    if (error.response?.data?.message) {
      return error.response.data.message
    } else if (error.response?.data?.error) {
      return error.response.data.error
    } else if (error.message) {
      return error.message
    } else {
      return 'Đã xảy ra lỗi không xác định. Vui lòng thử lại.'
    }
  },

  /**
   * Check if backend is available
   */
  async isBackendAvailable() {
    try {
      const response = await this.healthCheck()
      return response.success
    } catch (error) {
      return false
    }
  },

  /**
   * Get API configuration info
   */
  getConfig() {
    return {
      baseURL: config.api.baseURL,
      timeout: config.api.timeout,
      wsURL: config.api.wsURL,
      retryAttempts: config.api.retryAttempts,
      features: config.features
    }
  }
}

// Export axios instance for advanced usage
export { apiClient }

// Export configuration
export { config as apiConfig }

export default apiService 