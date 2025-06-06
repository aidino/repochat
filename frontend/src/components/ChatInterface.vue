<template>
  <div class="chat-container">
    <!-- Chat Header -->
    <header class="chat-header">
      <div>
        <h2 class="chat-title">{{ chatTitle }}</h2>
        <div class="chat-status">
          <div class="status-dot" :class="{ online: isOnline }"></div>
          <span class="status-text">{{ statusText }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button 
          @click="refreshChat" 
          class="btn-secondary text-sm"
          :disabled="isLoading"
        >
          <span class="mr-2">🔄</span>
          Làm mới
        </button>
      </div>
    </header>

    <!-- Messages Area -->
    <div class="messages-area" ref="messagesContainer">
      <!-- Messages List -->
      <div class="messages-list" v-if="messages.length > 0">
        <div 
          v-for="(message, index) in messages" 
          :key="message.id || index"
          :class="[
            'message', 
            message.isUser ? 'user-message' : 'bot-message',
            'animate-slide-in-up'
          ]"
        >
          <div class="message-avatar">
            <span v-if="message.isUser">👤</span>
            <span v-else>🤖</span>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessageText(message.text)"></div>
            <div class="message-time">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>
        </div>
        
        <!-- Typing Indicator -->
        <div v-if="isTyping" class="message bot-message animate-fade-in">
          <div class="message-avatar">
            <span>🤖</span>
          </div>
          <div class="message-content">
            <div class="message-text">
              <div class="typing-indicator">
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
              :disabled="isLoading"
            >
              {{ question }}
            </button>
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
          :disabled="isLoading"
        ></textarea>
        <button 
          @click="sendMessage"
          :disabled="!canSendMessage"
          class="send-btn"
        >
          <span v-if="isLoading" class="animate-pulse">⏳</span>
          <span v-else class="icon">📤</span>
          <span v-if="!isLoading">Gửi</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
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
        'Phân tích kiến trúc của dự án này',
        'Tìm các vấn đề bảo mật trong code',
        'Đề xuất cải thiện performance',
        'Review coding standards và best practices'
      ]
    },
    initialMessages: {
      type: Array,
      default: () => []
    }
  },

  emits: [
    'send-message',
    'refresh-chat'
  ],

  data() {
    return {
      messages: [...this.initialMessages],
      currentMessage: '',
      isLoading: false,
      isOnline: true,
      isTyping: false
    }
  },

  computed: {
    canSendMessage() {
      return this.currentMessage.trim() && !this.isLoading;
    },
    
    statusText() {
      if (!this.isOnline) return 'Ngoại tuyến';
      if (this.isLoading) return 'Đang xử lý...';
      if (this.isTyping) return 'Đang trả lời...';
      return 'Sẵn sàng';
    }
  },

  methods: {
    handleKeydown(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        this.sendMessage();
      }
    },

    handleInput() {
      // Auto-resize textarea
      this.$nextTick(() => {
        const textarea = this.$refs.messageInput;
        if (textarea) {
          textarea.style.height = 'auto';
          textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        }
      });
    },

    sendMessage() {
      if (!this.canSendMessage) return;

      const message = this.currentMessage.trim();
      this.currentMessage = '';
      
      // Reset textarea height
      this.$nextTick(() => {
        const textarea = this.$refs.messageInput;
        if (textarea) {
          textarea.style.height = 'auto';
        }
      });

      this.isLoading = true;
      this.isTyping = true;

      // Emit message to parent
      this.$emit('send-message', message);

      // Simulate response delay
      setTimeout(() => {
        this.isLoading = false;
        this.isTyping = false;
      }, 2000);
    },

    sendExampleQuestion(question) {
      this.currentMessage = question;
      this.sendMessage();
    },

    refreshChat() {
      this.$emit('refresh-chat');
    },

    formatMessageText(text) {
      // Format markdown-like syntax
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
    },

    formatTime(timestamp) {
      if (!timestamp) return '';
      
      const now = new Date();
      const time = new Date(timestamp);
      const diffMs = now - time;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return 'Vừa xong';
      if (diffMins < 60) return `${diffMins} phút trước`;
      if (diffHours < 24) return `${diffHours} giờ trước`;
      if (diffDays < 7) return `${diffDays} ngày trước`;
      
      return time.toLocaleDateString('vi-VN');
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    }
  },

  watch: {
    messages: {
      handler() {
        this.scrollToBottom();
      },
      deep: true
    },

    initialMessages: {
      handler(newMessages) {
        this.messages = [...newMessages];
      },
      deep: true
    }
  },

  mounted() {
    // Focus on message input
    this.$nextTick(() => {
      if (this.$refs.messageInput) {
        this.$refs.messageInput.focus();
      }
    });
    
    // Initial scroll to bottom
    this.scrollToBottom();
  }
}
</script>

<style scoped>
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
}
</style> 