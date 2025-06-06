<template>
  <div class="app-container">
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
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'

export default {
  name: 'App',
  components: {
    Sidebar
  },
  data() {
    return {
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
      alert('Chức năng cài đặt sẽ được triển khai trong Task 5.3!')
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
.app-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  font-family: Inter, sans-serif;
}



/* Chat Container */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--background-color);
}

.chat-header {
  padding: 1rem 1.5rem;
  background: var(--surface-color);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.chat-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--secondary-color);
}

.status-dot.online {
  background: var(--success-color);
}

.status-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* Messages Area */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.messages-list {
  max-width: 800px;
  margin: 0 auto;
}

.message {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  animation: slideIn 0.3s ease;
}

.message.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: var(--shadow-sm);
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-message .message-content {
  align-items: flex-end;
}

.message-text {
  background: var(--surface-color);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  line-height: 1.5;
}

.user-message .message-text {
  background: var(--primary-color);
  color: white;
}

.message-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
  padding: 0 0.5rem;
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
  padding: 2rem;
}

.welcome-content h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.welcome-content p {
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.example-questions {
  margin-top: 2rem;
}

.example-questions h4 {
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.example-btn {
  display: block;
  width: 100%;
  margin-bottom: 0.5rem;
  padding: 0.75rem;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s ease;
  color: var(--text-primary);
  text-align: left;
}

.example-btn:hover {
  background: var(--primary-color);
  color: white;
  transform: translateY(-1px);
}

/* Input Area */
.input-area {
  padding: 1rem 1.5rem;
  background: var(--surface-color);
  border-top: 1px solid var(--border-color);
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  min-height: 50px;
  resize: none;
}

.send-btn {
  min-width: 100px;
  height: 50px;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.icon {
  font-size: 1rem;
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

/* Responsive */
@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }
  
  .input-container {
    padding: 0 0.5rem;
  }
}
</style> 