/**
 * Vue Composables for API Integration
 * Provides reactive state management cho API calls
 */

import { ref, reactive, computed, readonly } from 'vue'
import { apiService } from '@services/api.js'
import { config } from '@config/environment.js'

/**
 * General purpose API call composable
 */
export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const clearError = () => {
    error.value = null
  }

  const handleError = (err) => {
    error.value = apiService.getErrorMessage(err)
    console.error('API Error:', err)
  }

  return {
    loading,
    error,
    clearError,
    handleError
  }
}

/**
 * Health check composable
 */
export function useHealthCheck() {
  const { loading, error, clearError, handleError } = useApi()
  const isHealthy = ref(false)
  const stats = ref(null)
  const lastChecked = ref(null)

  const checkHealth = async () => {
    if (loading.value) return

    loading.value = true
    clearError()

    try {
      const response = await apiService.healthCheck()
      
      if (response.success) {
        isHealthy.value = true
        stats.value = response.data
        lastChecked.value = new Date()
      } else {
        isHealthy.value = false
        error.value = response.error
      }
      
      return response
    } catch (err) {
      isHealthy.value = false
      handleError(err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const getSystemStatus = async () => {
    if (loading.value) return

    loading.value = true
    clearError()

    try {
      const response = await apiService.getSystemStatus()
      
      if (response.success) {
        stats.value = response.data
      } else {
        error.value = response.error
      }
      
      return response
    } catch (err) {
      handleError(err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    isHealthy,
    stats,
    lastChecked,
    checkHealth,
    getSystemStatus,
    clearError
  }
}

/**
 * Repository scanning composable
 */
export function useRepositoryScanning() {
  const { loading, error, clearError, handleError } = useApi()
  const scanResult = ref(null)
  const scanId = ref(null)
  const scanStatus = ref('idle') // idle, scanning, completed, failed
  const progress = ref(0)

  const scanRepository = async (repositoryUrl, options = {}) => {
    if (loading.value) return

    loading.value = true
    scanStatus.value = 'scanning'
    progress.value = 0
    clearError()
    scanResult.value = null

    try {
      const response = await apiService.scanRepository(repositoryUrl, options)
      
      if (response.success) {
        scanId.value = response.scanId
        scanResult.value = response.data
        
        // Start polling for status if scan is in progress
        if (response.data?.status === 'in_progress') {
          pollScanStatus()
        } else {
          scanStatus.value = 'completed'
          progress.value = 100
        }
      } else {
        scanStatus.value = 'failed'
        error.value = response.error
      }
      
      return response
    } catch (err) {
      scanStatus.value = 'failed'
      handleError(err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const getScanStatus = async (scanIdParam = null) => {
    const id = scanIdParam || scanId.value
    if (!id) return

    try {
      const response = await apiService.getScanStatus(id)
      
      if (response.success) {
        const status = response.data.status
        scanStatus.value = status
        progress.value = response.data.progress || 0
        
        if (status === 'completed' || status === 'failed') {
          return response
        }
      }
      
      return response
    } catch (err) {
      console.error('Error getting scan status:', err)
      return { success: false, error: apiService.getErrorMessage(err) }
    }
  }

  const getAnalysisResults = async (scanIdParam = null) => {
    const id = scanIdParam || scanId.value
    if (!id) return

    loading.value = true
    clearError()

    try {
      const response = await apiService.getAnalysisResults(id)
      
      if (response.success) {
        scanResult.value = response.data
      } else {
        error.value = response.error
      }
      
      return response
    } catch (err) {
      handleError(err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  // Polling function for scan status
  let pollInterval = null
  
  const pollScanStatus = () => {
    if (pollInterval) {
      clearInterval(pollInterval)
    }
    
    pollInterval = setInterval(async () => {
      const response = await getScanStatus()
      
      if (response?.success) {
        const status = response.data.status
        
        if (status === 'completed') {
          clearInterval(pollInterval)
          scanStatus.value = 'completed'
          progress.value = 100
          
          // Get final results
          await getAnalysisResults()
        } else if (status === 'failed') {
          clearInterval(pollInterval)
          scanStatus.value = 'failed'
          error.value = response.data.error || 'Scan failed'
        }
      }
    }, 2000) // Poll every 2 seconds
  }

  const stopPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  return {
    loading,
    error,
    scanResult,
    scanId,
    scanStatus,
    progress,
    scanRepository,
    getScanStatus,
    getAnalysisResults,
    stopPolling,
    clearError
  }
}

/**
 * Chat composable cho Q&A functionality (Updated for unified chat system)
 */
export function useChat() {
  const { loading, error, clearError, handleError } = useApi()
  const messages = ref([])
  const chatHistory = ref([])
  const isTyping = ref(false)
  const sessionId = ref(null)
  const conversationState = ref('greeting')
  
  // Real-time status states
  const currentStatus = ref('')
  const statusProgress = ref(0)
  const isStreaming = ref(false)

  const sendMessage = async (message, repositoryContext = null) => {
    if (loading.value || !message.trim()) return

    loading.value = true
    isTyping.value = true
    clearError()

    try {
      const response = await apiService.sendChatMessage(message, sessionId.value, repositoryContext)
      
      if (response.success) {
        // Update session info
        sessionId.value = response.data.session_id
        conversationState.value = response.data.conversation_state
        
        // Update messages from response (includes both user and bot messages)
        messages.value = response.data.messages || []
        
        return response
      } else {
        error.value = response.error
        return response
      }
      
    } catch (err) {
      handleError(err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
      isTyping.value = false
    }
  }

  const sendMessageStream = async (message, repositoryContext = null) => {
    if (isStreaming.value || !message.trim()) return

    isStreaming.value = true
    isTyping.value = true
    currentStatus.value = 'Đang bắt đầu...'
    statusProgress.value = 0
    clearError()

    try {
      const response = await apiService.streamChatMessage(
        message,
        sessionId.value,
        repositoryContext,
        // onStatusUpdate callback
        (statusData) => {
          currentStatus.value = statusData.status
          statusProgress.value = statusData.progress
        },
        // onComplete callback
        (completeData) => {
          // Update session info
          sessionId.value = completeData.session_id
          conversationState.value = completeData.conversation_state
          
          // Add bot response to messages
          const botMessage = {
            id: completeData.bot_response.id,
            content: completeData.bot_response.content,
            role: completeData.bot_response.role,
            timestamp: completeData.bot_response.timestamp,
            message_type: completeData.bot_response.message_type,
            context: completeData.bot_response.context
          }
          
          // Find user message and add bot response
          const userMessage = {
            id: Date.now() - 1000, // Approximate user message ID
            content: message,
            role: 'user',
            timestamp: new Date().toISOString(),
            message_type: 'user_input'
          }
          
          // Update messages array
          messages.value = [...messages.value, userMessage, botMessage]
          
          // Clear status
          currentStatus.value = ''
          statusProgress.value = 100
          isTyping.value = false
          isStreaming.value = false
        },
        // onError callback
        (errorData) => {
          error.value = errorData.error || 'Đã xảy ra lỗi khi streaming'
          currentStatus.value = 'Lỗi'
          statusProgress.value = 0
          isTyping.value = false
          isStreaming.value = false
        }
      )
      
      return response
      
    } catch (err) {
      handleError(err)
      currentStatus.value = 'Lỗi'
      statusProgress.value = 0
      isTyping.value = false
      isStreaming.value = false
      return { success: false, error: error.value }
    }
  }

  const askQuestion = async (question, repositoryContext = null) => {
    // Q&A now uses the unified chat system
    return sendMessage(question, repositoryContext)
  }

  const askQuestionStream = async (question, repositoryContext = null) => {
    // Q&A streaming version
    return sendMessageStream(question, repositoryContext)
  }

  const loadChatHistory = async (sessionIdParam = null) => {
    const targetSessionId = sessionIdParam || sessionId.value
    if (!targetSessionId) return { success: false, error: 'No session ID provided' }

    loading.value = true
    clearError()

    try {
      const response = await apiService.getChatHistory(targetSessionId)
      
      if (response.success) {
        messages.value = response.data.messages || []
        conversationState.value = response.data.state || 'greeting'
        sessionId.value = targetSessionId
      } else {
        error.value = response.error
      }
      
      return response
    } catch (err) {
      handleError(err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const executeTaskFromChat = async () => {
    if (!sessionId.value) return { success: false, error: 'No active session' }

    loading.value = true
    clearError()

    try {
      const response = await apiService.executeTaskFromChat(sessionId.value)
      
      if (response.success) {
        // Reload chat to get system message about task execution
        await loadChatHistory(sessionId.value)
      } else {
        error.value = response.error
      }
      
      return response
    } catch (err) {
      handleError(err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const clearMessages = () => {
    messages.value = []
    sessionId.value = null
    conversationState.value = 'greeting'
    clearError()
  }

  const startNewSession = () => {
    clearMessages()
    // New session will be created on first message
  }

  return {
    loading,
    error,
    messages,
    chatHistory,
    isTyping,
    sessionId: readonly(sessionId),
    conversationState: readonly(conversationState),
    sendMessage,
    sendMessageStream,
    askQuestion,
    askQuestionStream,
    loadChatHistory,
    executeTaskFromChat,
    clearMessages,
    startNewSession,
    clearError,
    // Streaming states
    currentStatus: readonly(currentStatus),
    statusProgress: readonly(statusProgress),
    isStreaming: readonly(isStreaming)
  }
}

/**
 * Settings management composable
 */
export function useSettings() {
  const { loading, error, clearError, handleError } = useApi()
  const settings = ref({})
  const isDirty = ref(false)

  const loadSettings = async (userId = 'user123') => {
    loading.value = true
    clearError()

    try {
      const response = await apiService.getSettings(userId)
      
      if (response.success) {
        settings.value = response.data
        isDirty.value = false
      } else {
        error.value = response.error
        // Load default settings if API fails
        settings.value = getDefaultSettings()
      }
      
      return response
    } catch (err) {
      handleError(err)
      settings.value = getDefaultSettings()
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const saveSettings = async (newSettings = null, userId = 'user123') => {
    const settingsToSave = newSettings || settings.value
    
    loading.value = true
    clearError()

    try {
      const response = await apiService.updateSettings(settingsToSave, userId)
      
      if (response.success) {
        settings.value = response.data
        isDirty.value = false
      } else {
        error.value = response.error
      }
      
      return response
    } catch (err) {
      handleError(err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const updateSetting = (key, value) => {
    settings.value[key] = value
    isDirty.value = true
  }

  const resetSettings = () => {
    settings.value = getDefaultSettings()
    isDirty.value = true
  }

  const getDefaultSettings = () => ({
    llmModels: {
      nlu: 'gpt-3.5-turbo',
      codeAnalysis: 'gpt-4',
      reportGeneration: 'gpt-3.5-turbo'
    },
    ui: {
      theme: 'dark',
      language: 'vi',
      autoScroll: true
    },
    features: {
      autoRetry: true,
      debugMode: config.features.debugMode,
      logging: config.features.logging
    }
  })

  return {
    loading,
    error,
    settings,
    isDirty,
    loadSettings,
    saveSettings,
    updateSetting,
    resetSettings,
    clearError
  }
}

/**
 * Connection status composable
 */
export function useConnectionStatus() {
  const isConnected = ref(false)
  const checking = ref(false)
  const lastCheck = ref(null)
  const retryCount = ref(0)
  const maxRetries = config.api.retryAttempts

  const checkConnection = async () => {
    if (checking.value) return isConnected.value

    checking.value = true
    
    try {
      const available = await apiService.isBackendAvailable()
      isConnected.value = available
      lastCheck.value = new Date()
      
      if (available) {
        retryCount.value = 0
      }
      
      return available
    } catch (error) {
      isConnected.value = false
      console.error('Connection check failed:', error)
      return false
    } finally {
      checking.value = false
    }
  }

  const retryConnection = async () => {
    if (retryCount.value >= maxRetries) {
      console.warn('Max retry attempts reached')
      return false
    }
    
    retryCount.value++
    await new Promise(resolve => setTimeout(resolve, config.api.retryDelay))
    
    return await checkConnection()
  }

  // Auto-check on initialization
  checkConnection()

  return {
    isConnected,
    checking,
    lastCheck,
    retryCount,
    maxRetries,
    checkConnection,
    retryConnection
  }
}

/**
 * Repository utilities composable
 */
export function useRepositoryUtils() {
  const validateRepositoryUrl = (url) => {
    if (!url || typeof url !== 'string') {
      return { valid: false, error: 'URL không được để trống' }
    }
    
    const trimmedUrl = url.trim()
    
    // Basic GitHub/GitLab URL patterns
    const gitPatterns = [
      /^https:\/\/github\.com\/[\w-]+\/[\w.-]+(?:\.git)?$/i,
      /^https:\/\/gitlab\.com\/[\w-]+\/[\w.-]+(?:\.git)?$/i,
      /^git@github\.com:[\w-]+\/[\w.-]+\.git$/i,
      /^git@gitlab\.com:[\w-]+\/[\w.-]+\.git$/i
    ]
    
    const isValidGitUrl = gitPatterns.some(pattern => pattern.test(trimmedUrl))
    
    if (!isValidGitUrl) {
      return { 
        valid: false, 
        error: 'URL không hợp lệ. Vui lòng nhập URL GitHub hoặc GitLab hợp lệ.' 
      }
    }
    
    return { valid: true, url: trimmedUrl }
  }

  const extractRepoInfo = (url) => {
    const patterns = [
      /https:\/\/github\.com\/([\w-]+)\/([\w.-]+)(?:\.git)?/i,
      /https:\/\/gitlab\.com\/([\w-]+)\/([\w.-]+)(?:\.git)?/i,
      /git@github\.com:([\w-]+)\/([\w.-]+)\.git/i,
      /git@gitlab\.com:([\w-]+)\/([\w.-]+)\.git/i
    ]
    
    for (const pattern of patterns) {
      const match = url.match(pattern)
      if (match) {
        return {
          owner: match[1],
          repo: match[2].replace(/\.git$/, ''),
          platform: url.includes('github.com') ? 'github' : 'gitlab'
        }
      }
    }
    
    return null
  }

  return {
    validateRepositoryUrl,
    extractRepoInfo
  }
}