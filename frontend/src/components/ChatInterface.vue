<template>
  <div class="chat-container">
    <!-- Chat Header -->
    <header class="chat-header">
      <div>
        <h2 class="chat-title">{{ chatTitle }}</h2>
        <div class="chat-status">
          <div class="status-dot" :class="{ online: isConnected }"></div>
          <span class="status-text">{{ statusText }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button 
          @click="refreshChat" 
          class="btn-secondary text-sm"
          :disabled="loading"
        >
          <span class="mr-2">🔄</span>
          Làm mới
        </button>
      </div>
    </header>

    <!-- Connection Status Banner -->
    <div v-if="!isConnected && !checking" class="connection-banner error">
      <span class="icon">⚠️</span>
      <span>Không thể kết nối đến server. Đang hoạt động ở chế độ ngoại tuyến.</span>
      <button @click="checkConnection" class="btn-link">Thử lại</button>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      <span class="icon">❌</span>
      <span>{{ error }}</span>
      <button @click="clearError" class="btn-link">Đóng</button>
    </div>

    <!-- Messages Area -->
    <div class="messages-area" ref="messagesContainer">
      <!-- Messages List -->
      <div class="messages-list" v-if="messages.length > 0">
        <div 
          v-for="message in messages" 
          :key="message.id"
          :class="[
            'message', 
            message.sender === 'user' ? 'user-message' : 'bot-message',
            'animate-slide-in-up'
          ]"
        >
          <div class="message-avatar">
            <span v-if="message.sender === 'user'">👤</span>
            <span v-else>🤖</span>
          </div>
          <div class="message-content">
            <div 
              class="message-text" 
              :class="{ 'error-message': message.type === 'error' }"
              v-html="formatMessageText(message.content)"
            ></div>
            <div class="message-time">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>
        </div>
        
        <!-- Enhanced Typing Indicator with Streaming Status -->
        <div v-if="loading || isStreaming" class="message bot-message animate-fade-in">
          <div class="message-avatar">
            <span>🤖</span>
          </div>
          <div class="message-content">
            <div class="message-text">
              <!-- Streaming Status Display -->
              <div v-if="isStreaming && currentStatus" class="streaming-status">
                <div class="status-header">
                  <span class="status-text">{{ currentStatus }}</span>
                  <span class="status-progress">{{ statusProgress }}%</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: statusProgress + '%' }"
                  ></div>
                </div>
              </div>
              
              <!-- Default Typing Indicator -->
              <div v-else class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Welcome Message -->
      <div class="welcome-message" v-else>
        <div class="welcome-content animate-fade-in">
          <h2>{{ welcomeTitle }}</h2>
          <p class="text-lg">{{ welcomeSubtitle }}</p>
          <p>{{ welcomeDescription }}</p>
          
          <div class="example-questions" v-if="exampleQuestions.length > 0">
            <h4>Câu hỏi mẫu:</h4>
            <button 
              v-for="(question, index) in exampleQuestions" 
              :key="index"
              @click="sendExampleQuestion(question)"
              class="example-btn"
              :disabled="loading"
            >
              {{ question }}
            </button>
          </div>

          <!-- Repository Tools -->
          <div class="repo-tools">
            <h4>Phân tích Repository:</h4>
            <div class="tool-input">
              <input
                v-model="repositoryUrl"
                @keydown.enter="scanRepository"
                placeholder="https://github.com/user/repo.git"
                class="repo-input"
                :disabled="loading"
              />
              <button 
                @click="scanRepository"
                :disabled="!repositoryUrl.trim() || loading"
                class="btn-primary"
              >
                <span v-if="loading">⏳</span>
                <span v-else>🔍</span>
                Quét Repository
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <div class="input-container">
        <textarea
          ref="messageInput"
          v-model="currentMessage"
          @keydown="handleKeydown"
          @input="handleInput"
          placeholder="Nhập câu hỏi của bạn về code..."
          class="message-input"
          rows="1"
          :disabled="loading"
        ></textarea>
        <button 
          @click="sendMessage"
          :disabled="!canSendMessage"
          class="send-btn"
        >
          <span v-if="loading" class="animate-pulse">⏳</span>
          <span v-else class="icon">📤</span>
          <span v-if="!loading">Gửi</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useChat, useConnectionStatus, useRepositoryScanning } from '@composables/useApi.js'
import { config } from '@config/environment.js'
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

export default {
  name: 'ChatInterface',
  
  props: {
    chatTitle: {
      type: String,
      default: 'Trợ lý AI Code Review'
    },
    welcomeTitle: {
      type: String,
      default: 'Chào mừng đến với RepoChat!'
    },
    welcomeSubtitle: {
      type: String,
      default: 'Trợ lý AI thông minh cho việc phân tích và review code'
    },
    welcomeDescription: {
      type: String,
      default: 'Hãy bắt đầu bằng cách hỏi một câu hỏi hoặc thử một trong những ví dụ dưới đây:'
    },
    exampleQuestions: {
      type: Array,
      default: () => [
        'Định nghĩa của class User ở đâu?',
        'Phân tích kiến trúc của dự án này',
        'Tìm các vấn đề bảo mật trong code',
        'Đề xuất cải thiện performance'
      ]
    },
    initialMessages: {
      type: Array,
      default: () => []
    }
  },

  emits: [
    'send-message',
    'refresh-chat',
    'repository-scanned',
    'error'
  ],

  setup(props, { emit }) {
    // === Reactive State ===
    const currentMessage = ref('')
    const repositoryUrl = ref('')
    const repositoryContext = ref(null)
    const messagesContainer = ref(null)
    const messageInput = ref(null)

    // === Composables ===
    const { 
      loading: chatLoading, 
      error: chatError,
      messages, 
      isTyping,
      sendMessage: sendChatMessage,
      sendMessageStream,
      askQuestion,
      askQuestionStream,
      clearMessages,
      clearError: clearChatError,
      // Streaming states
      currentStatus,
      statusProgress,
      isStreaming
    } = useChat()

    const { 
      isConnected, 
      checking, 
      checkConnection,
      retryConnection
    } = useConnectionStatus()

    const {
      loading: scanLoading,
      error: scanError,
      scanResult,
      scanStatus,
      progress,
      scanRepository: performScan,
      clearError: clearScanError
    } = useRepositoryScanning()

    // === Computed Properties ===
    const loading = computed(() => chatLoading.value || scanLoading.value || isStreaming.value)
    const error = computed(() => chatError.value || scanError.value)

    const statusText = computed(() => {
      if (checking.value) return 'Đang kiểm tra kết nối...'
      if (!isConnected.value) return 'Ngoại tuyến'
      if (isStreaming.value && currentStatus.value) return currentStatus.value
      if (scanStatus.value === 'scanning') return `Đang quét repository... ${progress.value}%`
      if (loading.value) return 'Đang xử lý...'
      return 'Trực tuyến'
    })

    const canSendMessage = computed(() => {
      return currentMessage.value.trim() && !loading.value && isConnected.value && !isStreaming.value
    })

    // === Message Handling ===
    const handleSendMessage = async () => {
      if (!canSendMessage.value) return

      const message = currentMessage.value.trim()
      
      // Clear input immediately when user clicks send
      currentMessage.value = ''

      // Reset textarea height and focus back to input
      await nextTick()
      resetTextareaHeight()
      if (messageInput.value) {
        messageInput.value.focus()
      }

      try {
        // Emit to parent component for logging
        emit('send-message', message)

        // Use streaming for better UX - determine if this is a Q&A question or regular chat
        if (isQuestionMessage(message)) {
          await askQuestionStream(message, repositoryContext.value)
        } else {
          await sendMessageStream(message, repositoryContext.value)
        }

        // Auto-scroll to bottom after message
        await nextTick()
        scrollToBottom()
        
      } catch (err) {
        console.error('Error sending message:', err)
        
        // If there's an error, put the message back in the input
        currentMessage.value = message
        
        emit('error', err.message || 'Lỗi khi gửi tin nhắn')
      }
    }

    const sendExampleQuestion = async (question) => {
      if (loading.value) return
      
      // Set the question as current message
      currentMessage.value = question
      
      // Send the message (handleSendMessage will clear the input)
      await handleSendMessage()
    }

    const isQuestionMessage = (message) => {
      const questionPatterns = [
        /định nghĩa|definition|define/i,
        /ở đâu|where|location/i,
        /class|interface|function|method/i,
        /phân tích|analyze|analysis/i,
        /tìm|find|search/i
      ]
      
      return questionPatterns.some(pattern => pattern.test(message))
    }

    // === Repository Scanning ===
    const scanRepository = async () => {
      if (!repositoryUrl.value.trim() || loading.value) return

      const url = repositoryUrl.value.trim()
      
      try {
        clearScanError()
        
        const response = await performScan(url, {
          includeAnalysis: true,
          analyzeCode: true
        })

        if (response.success) {
          // Update repository context for chat
          repositoryContext.value = {
            repository_url: url,
            scan_id: response.scanId,
            scan_data: response.data
          }

          // Add success message to chat
          messages.value.push({
            id: Date.now(),
            content: `✅ Repository đã được quét thành công!\n\n📊 **Thống kê:**\n- Repository: ${url}\n- Scan ID: ${response.scanId}\n- Trạng thái: ${response.data?.status || 'Hoàn thành'}\n\nBạn có thể hỏi các câu hỏi về repository này.`,
            role: 'assistant',
            timestamp: new Date().toISOString(),
            type: 'scan_success'
          })

          // Emit repository scanned event
          emit('repository-scanned', {
            url,
            scanId: response.scanId,
            data: response.data
          })

          // Clear repository URL after successful scan
          repositoryUrl.value = ''
          
        } else {
          // Add error message to chat
          messages.value.push({
            id: Date.now(),
            content: `❌ Lỗi khi quét repository: ${response.error}`,
            role: 'assistant',
            timestamp: new Date().toISOString(),
            isError: true
          })
          
          emit('error', response.error)
        }

        await nextTick()
        scrollToBottom()

      } catch (err) {
        console.error('Repository scan error:', err)
        emit('error', err.message || 'Lỗi khi quét repository')
      }
    }

    // === UI Helpers ===
    const refreshChat = async () => {
      try {
        clearMessages()
        clearChatError()
        clearScanError()
        repositoryContext.value = null
        repositoryUrl.value = ''
        
        // Check connection
        await checkConnection()
        
        emit('refresh-chat')
        
        // Focus input after refresh
        await nextTick()
        messageInput.value?.focus()
        
      } catch (err) {
        console.error('Error refreshing chat:', err)
      }
    }

    const clearError = () => {
      clearChatError()
      clearScanError()
    }

    const formatMessageText = (text) => {
      if (!text) return ''
      
      // Convert markdown-like formatting to HTML
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>')
    }

    const formatTime = (timestamp) => {
      try {
        const date = new Date(timestamp)
        return date.toLocaleTimeString('vi-VN', {
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch {
        return ''
      }
    }

    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }

    // === Input Handling ===
    const handleKeydown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        handleSendMessage()
      }
    }

    const handleInput = () => {
      // Auto-resize textarea
      const textarea = messageInput.value
      if (textarea) {
        textarea.style.height = 'auto'
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
      }
    }

    // Helper function to reset textarea height
    const resetTextareaHeight = () => {
      const textarea = messageInput.value
      if (textarea) {
        textarea.style.height = 'auto'
        textarea.style.height = '44px' // Reset to default height
      }
    }

    // === Lifecycle ===
    onMounted(async () => {
      // Initialize connection check
      await checkConnection()
      
      // Load initial messages if provided
      if (props.initialMessages.length > 0) {
        messages.value = [...props.initialMessages]
        await nextTick()
        scrollToBottom()
      }

      // Focus input
      messageInput.value?.focus()

      // Set up auto-scroll for new messages
      watch(
        () => messages.value.length,
        async () => {
          await nextTick()
          scrollToBottom()
        }
      )
    })

    onUnmounted(() => {
      // Clean up any intervals or event listeners
      clearMessages()
    })

    // === Debug Info (Development) ===
    if (config.features.debugMode) {
      watch([isConnected, loading, error], ([connected, isLoading, currentError]) => {
        console.log('🔧 ChatInterface Debug:', {
          connected,
          loading: isLoading,
          error: currentError,
          messagesCount: messages.value.length,
          repositoryContext: repositoryContext.value
        })
      })
    }

    return {
      // State
      currentMessage,
      repositoryUrl,
      repositoryContext,
      messagesContainer,
      messageInput,
      
      // Computed
      loading,
      error,
      isConnected,
      checking,
      statusText,
      canSendMessage,
      messages,
      isTyping,
      scanStatus,
      progress,
      
      // Methods
      sendMessage: handleSendMessage,
      sendExampleQuestion,
      scanRepository,
      refreshChat,
      clearError,
      checkConnection,
      retryConnection,
      formatMessageText,
      formatTime,
      handleKeydown,
      handleInput,
      scrollToBottom,
      resetTextareaHeight
    }
  }
}
</script>

<style scoped>
/* Connection Banner */
.connection-banner {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: rgba(255, 165, 0, 0.1);
  border-left: 4px solid orange;
  color: var(--color-text-primary);
}

.connection-banner.error {
  background: rgba(255, 0, 0, 0.1);
  border-left-color: red;
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: rgba(255, 0, 0, 0.1);
  border-left: 4px solid red;
  color: var(--color-text-primary);
}

/* Repository Tools */
.repo-tools {
  margin-top: var(--space-6);
  padding: var(--space-4);
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--border-radius-lg);
}

.tool-input {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.repo-input {
  flex: 1;
  padding: var(--space-3);
  background: var(--color-surface);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.repo-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.repo-input::placeholder {
  color: var(--color-text-tertiary);
}

/* Error Message Styling */
.error-message {
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  padding: var(--space-2);
  border-radius: var(--border-radius-sm);
  border-left: 3px solid #ff6b6b;
}

/* Button Link */
.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  text-decoration: underline;
  cursor: pointer;
  font-size: inherit;
}

.btn-link:hover {
  color: var(--color-primary-hover);
}

/* Typing Indicator Animation */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-tertiary);
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Streaming Status Display */
.streaming-status {
  padding: var(--space-3);
  background: rgba(102, 126, 234, 0.1);
  border-radius: var(--border-radius-md);
  border-left: 3px solid var(--color-primary);
  min-width: 280px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.status-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.status-progress {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-bold);
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), #8b5cf6);
  border-radius: 3px;
  transition: width 0.3s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Streaming status icon animation */
.status-text::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  margin-right: var(--space-1);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

/* Header Actions */
.header-actions {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

/* Code formatting in messages */
.message-text :deep(code) {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.message-text :deep(strong) {
  font-weight: var(--font-weight-bold);
}

.message-text :deep(em) {
  font-style: italic;
}

.message-text :deep(a) {
  color: var(--color-primary);
  text-decoration: underline;
}

.message-text :deep(a):hover {
  color: var(--color-primary-hover);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .chat-header {
    padding: var(--space-3);
  }
  
  .chat-title {
    font-size: var(--font-size-base);
  }
  
  .header-actions {
    gap: var(--space-1);
  }
  
  .messages-list {
    padding: var(--space-3);
  }
  
  .input-area {
    padding: var(--space-3);
  }
  
  .welcome-content {
    padding: var(--space-4);
  }

  .tool-input {
    flex-direction: column;
  }

  .repo-input {
    margin-bottom: var(--space-2);
  }
}
</style> 