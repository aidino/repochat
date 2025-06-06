<template>
  <div class="app-container">
    <!-- Settings Screen -->
    <SettingsScreen 
      v-if="showSettings"
      @go-back="closeSettings"
      @settings-saved="onSettingsSaved"
    />

    <!-- Main App Layout (when not showing settings) -->
    <template v-else>
      <!-- Sidebar Component -->
      <Sidebar 
        :currentChatId="currentChatId"
        :isLoading="isLoading"
        @new-chat="startNewChat"
        @open-settings="openSettings"
        @select-chat="selectChat"
        @delete-chat="deleteChat"
        @rename-chat="renameChat"
        @duplicate-chat="duplicateChat"
        @export-chat="exportChat"
      />

      <!-- Main Chat Area -->
      <main class="chat-container">
      <!-- Chat Header -->
      <header class="chat-header">
        <h2 class="chat-title">{{ currentChatTitle }}</h2>
        <div class="chat-status">
          <span class="status-dot" :class="{ online: isOnline }"></span>
          <span class="status-text">{{ isOnline ? 'Trực tuyến' : 'Ngoại tuyến' }}</span>
        </div>
      </header>

      <!-- Messages Area -->
      <div class="messages-area" ref="messagesContainer">
        <div class="messages-list">
          <div 
            v-for="message in messages" 
            :key="message.id"
            class="message"
            :class="{ 'user-message': message.isUser, 'bot-message': !message.isUser }"
          >
            <div class="message-avatar">
              <span v-if="message.isUser">👤</span>
              <span v-else>🤖</span>
            </div>
            <div class="message-content">
              <div class="message-text">{{ message.text }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
        </div>

        <!-- Welcome Message when no messages -->
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-content">
            <h2>👋 Chào mừng đến với RepoChat!</h2>
            <p>Tôi là trợ lý AI phân tích repository thông minh.</p>
            <p>Hãy bắt đầu bằng cách nhập câu hỏi hoặc yêu cầu phân tích repository.</p>
            
            <div class="example-questions">
              <h4>Ví dụ về câu hỏi:</h4>
              <button 
                v-for="example in exampleQuestions" 
                :key="example"
                class="example-btn"
                @click="sendExampleQuestion(example)"
              >
                {{ example }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <div class="input-container">
          <input
            v-model="inputMessage"
            @keyup.enter="sendMessage"
            class="input message-input"
            placeholder="Nhập tin nhắn của bạn..."
            :disabled="isLoading"
          />
          <button 
            @click="sendMessage"
            class="btn btn-primary send-btn"
            :disabled="!inputMessage.trim() || isLoading"
          >
            <span v-if="isLoading" class="icon">⏳</span>
            <span v-else class="icon">📤</span>
            {{ isLoading ? 'Đang xử lý...' : 'Gửi' }}
          </button>
        </div>
      </div>
    </main>
    </template>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'
import SettingsScreen from './components/SettingsScreen.vue'

export default {
  name: 'App',
  components: {
    Sidebar,
    SettingsScreen
  },
  data() {
    return {
      // App state
      showSettings: false,
      
      // Chat state
      currentChatId: 1,
      inputMessage: '',
      isLoading: false,
      isOnline: true,
      
      // Messages
      messages: [],
      
      // Example questions
      exampleQuestions: [
        'Phân tích repository https://github.com/spring-projects/spring-petclinic.git',
        'Review PR #123 của repository này',
        'Định nghĩa của class User ở đâu?',
        'Tìm các circular dependencies trong code'
      ]
    }
  },
  
  computed: {
    currentChatTitle() {
      // For now, use simple title logic. In real app, this would come from chat data
      return this.currentChatId === 1 ? 'Phân tích Spring Pet Clinic' : 'Chat Mới'
    }
  },
  
  methods: {
    startNewChat() {
      this.currentChatId = Date.now()
      this.messages = []
      console.log('Started new chat with ID:', this.currentChatId)
    },
    
    openSettings() {
      console.log('Opening settings screen...')
      this.showSettings = true
    },
    
    selectChat(chatId) {
      this.currentChatId = chatId
      // In a real app, load messages for this chat from API
      this.messages = []
      console.log('Selected chat:', chatId)
    },
    
    // === New Sidebar Event Handlers ===
    deleteChat(chatId) {
      console.log('Delete chat requested:', chatId)
      // If deleting current chat, switch to new chat
      if (chatId === this.currentChatId) {
        this.startNewChat()
      }
    },
    
    renameChat(data) {
      console.log('Rename chat requested:', data)
      // In real app, update chat title in backend
    },
    
    duplicateChat(chat) {
      console.log('Duplicate chat requested:', chat)
      // In real app, create new chat based on existing one
      this.currentChatId = chat.id
      this.messages = []
    },
    
    exportChat(chat) {
      console.log('Export chat requested:', chat)
      // In real app, export chat data
    },
    
    // === Settings Management ===
    closeSettings() {
      console.log('Closing settings screen...')
      this.showSettings = false
    },
    
    onSettingsSaved(settingsData) {
      console.log('Settings saved in parent app:', settingsData)
      // Optional: show notification or handle settings update
      // For now, just close settings automatically after save
      setTimeout(() => {
        this.closeSettings()
      }, 2000)
    },
    
    sendMessage() {
      if (!this.inputMessage.trim() || this.isLoading) return
      
      // Add user message
      const userMessage = {
        id: Date.now(),
        text: this.inputMessage,
        isUser: true,
        timestamp: new Date()
      }
      
      this.messages.push(userMessage)
      
      // Store input for processing
      const messageText = this.inputMessage
      this.inputMessage = ''
      this.isLoading = true
      
      // Simulate bot response
      setTimeout(() => {
        const botMessage = {
          id: Date.now() + 1,
          text: this.generateBotResponse(messageText),
          isUser: false,
          timestamp: new Date()
        }
        
        this.messages.push(botMessage)
        this.isLoading = false
        
        // Auto-scroll to bottom
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }, 1500)
      
      // Auto-scroll to bottom for user message
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    },
    
    sendExampleQuestion(question) {
      this.inputMessage = question
      this.sendMessage()
    },
    
    generateBotResponse(userMessage) {
      // Mock bot responses based on message content
      const message = userMessage.toLowerCase()
      
      if (message.includes('repository') || message.includes('repo')) {
        return '🔍 Tôi hiểu bạn muốn phân tích repository. Hiện tại đây là giao diện demo. Trong phiên bản production, tôi sẽ kết nối với backend để thực hiện phân tích repository thực sự bằng CLI commands.'
      } else if (message.includes('pr') || message.includes('pull request')) {
        return '📝 Chức năng review Pull Request đang được phát triển. Tôi sẽ có thể phân tích các thay đổi code, tác động đến hệ thống và đưa ra các gợi ý cải thiện.'
      } else if (message.includes('class') || message.includes('định nghĩa')) {
        return '🎯 Tôi có thể giúp bạn tìm định nghĩa class trong codebase. Ví dụ: "Class User được định nghĩa tại: src/models/user.py:15"'
      } else if (message.includes('circular') || message.includes('dependency')) {
        return '🔄 Tôi có thể phát hiện circular dependencies trong code và đưa ra các giải pháp để fix chúng.'
      } else {
        return `✨ Cảm ơn bạn đã gửi: "${userMessage}". Đây là giao diện chat cơ bản cho RepoChat v1.0. Tôi hiểu được tin nhắn và sẽ phản hồi thông minh hơn khi được tích hợp với backend!`
      }
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    formatDate(date) {
      return new Intl.DateTimeFormat('vi-VN', {
        month: 'short',
        day: 'numeric'
      }).format(date)
    },
    
    formatTime(date) {
      return new Intl.DateTimeFormat('vi-VN', {
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }
  },
  
  mounted() {
    // Simulate online status
    setInterval(() => {
      this.isOnline = navigator.onLine
    }, 5000)
  }
}
</script>

<style scoped>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');

.app-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  font-family: var(--font-family-primary);
  background: var(--color-background);
  color: var(--color-text-primary);
}



/* Chat Container */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
}

.chat-header {
  padding: var(--space-4) var(--space-6);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-subtle);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(10px);
}

.chat-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  letter-spacing: -0.025em;
}

.chat-status {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-dot {
  width: var(--space-2);
  height: var(--space-2);
  border-radius: var(--radius-full);
  background: var(--color-text-tertiary);
  animation: pulse 2s infinite;
}

.status-dot.online {
  background: var(--color-success);
}

.status-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

/* Messages Area */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  background: var(--gradient-secondary);
}

.messages-list {
  max-width: 800px;
  margin: 0 auto;
}

.message {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  animation: slideIn var(--transition-normal) ease;
}

.message.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
  box-shadow: var(--shadow-md);
  flex-shrink: 0;
  border: 2px solid var(--color-border-subtle);
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.user-message .message-content {
  align-items: flex-end;
}

.message-text {
  background: var(--color-surface);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  line-height: var(--line-height-relaxed);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-subtle);
}

.user-message .message-text {
  background: var(--gradient-primary);
  color: var(--color-text-inverse);
  border: none;
}

.message-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  padding: 0 var(--space-2);
  font-weight: var(--font-weight-medium);
}

/* Welcome Message */
.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
}

.welcome-content {
  max-width: 500px;
  padding: var(--space-8);
  background: var(--color-surface);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--color-border-subtle);
}

.welcome-content h2 {
  font-size: var(--font-size-2xl);
  margin-bottom: var(--space-4);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-bold);
  letter-spacing: -0.025em;
}

.welcome-content p {
  color: var(--color-text-secondary);
  margin-bottom: var(--space-3);
  line-height: var(--line-height-relaxed);
}

.example-questions {
  margin-top: var(--space-8);
}

.example-questions h4 {
  margin-bottom: var(--space-4);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-semibold);
}

.example-btn {
  display: block;
  width: 100%;
  margin-bottom: var(--space-2);
  padding: var(--space-3);
  background: var(--color-background-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--color-text-primary);
  text-align: left;
  font-family: var(--font-family-primary);
  font-weight: var(--font-weight-medium);
}

.example-btn:hover {
  background: var(--gradient-primary);
  color: var(--color-text-inverse);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
  border-color: transparent;
}

/* Input Area */
.input-area {
  padding: var(--space-4) var(--space-6);
  background: rgba(255, 255, 255, 0.8);
  border-top: 1px solid var(--color-border-subtle);
  backdrop-filter: blur(20px);
  box-shadow: var(--shadow-lg);
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: var(--space-3);
  align-items: flex-end;
}

.message-input {
  flex: 1;
  min-height: 50px;
  resize: none;
  border-radius: var(--radius-xl);
  border: 2px solid var(--color-border);
  padding: var(--space-4) var(--space-5);
  font-family: var(--font-family-primary);
  font-size: var(--font-size-base);
  transition: all var(--transition-fast);
}

.message-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(182, 176, 159, 0.2);
}

.send-btn {
  min-width: 100px;
  height: 50px;
  border-radius: var(--radius-xl);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.icon {
  font-size: var(--font-size-base);
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }
  
  .input-container {
    padding: 0 var(--space-2);
  }
  
  .chat-header {
    padding: var(--space-3) var(--space-4);
  }
  
  .messages-area {
    padding: var(--space-3);
  }
  
  .input-area {
    padding: var(--space-3) var(--space-4);
  }
}

@media (max-width: 480px) {
  .welcome-content {
    padding: var(--space-6);
    margin: var(--space-4);
  }
  
  .send-btn {
    min-width: 80px;
  }
  
  .message-avatar {
    width: 32px;
    height: 32px;
    font-size: var(--font-size-base);
  }
}

/* Accessibility improvements */
.message-input:focus-visible,
.example-btn:focus-visible,
.send-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .input-area {
    background: rgba(38, 38, 38, 0.8);
  }
}
</style> 