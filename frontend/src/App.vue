<template>
  <div class="app-container">
    <!-- Settings Screen -->
    <SettingsScreen 
      v-if="currentView === 'settings'"
      @go-back="goBackFromSettings"
      @settings-saved="handleSettingsSaved"
    />

    <!-- Main App Layout -->
    <template v-else>
      <!-- Modern Sidebar - Always visible -->
      <ModernSidebar
        :show-on-mobile="true"
        :current-chat-id="currentChatId"
        :user-name="userSettings.name"
        @new-chat="handleNewChat"
        @select-chat="handleSelectChat"
        @delete-chat="handleDeleteChat"
        @rename-chat="handleRenameChat"
        @export-chat="handleExportChat"
        @duplicate-chat="handleDuplicateChat"
        @open-settings="openSettings"
        @close-sidebar="closeSidebar"
        @toggle-favorite="handleToggleFavorite"
        @clear-all-chats="handleClearAllChats"
      />

      <!-- Chat Interface -->
      <ChatInterface
        :chat-title="currentChatTitle"
        :welcome-title="welcomeSettings.title"
        :welcome-subtitle="welcomeSettings.subtitle"
        :welcome-description="welcomeSettings.description"
        :example-questions="exampleQuestions"
        :initial-messages="currentChatMessages"
        @send-message="handleSendMessage"
        @refresh-chat="handleRefreshChat"
        ref="chatInterface"
      />
    </template>
  </div>
</template>

<script>
import ChatInterface from './components/ChatInterface.vue'
import ModernSidebar from './components/ModernSidebar.vue'
import SettingsScreen from './components/SettingsScreen.vue'

export default {
  name: 'App',
  
  components: {
    ChatInterface,
    ModernSidebar,
    SettingsScreen
  },

  data() {
    return {
      // App State
      currentView: 'chat', // 'chat' | 'settings'
      sidebarVisible: true, // Always visible - removed responsive logic
      
      // Chat State
      currentChatId: null,
      chats: new Map(), // Store chat data by ID
      
      // User Settings
      userSettings: {
        name: 'Developer',
        theme: 'dark',
        language: 'vi'
      },

      // Welcome Screen Settings
      welcomeSettings: {
        title: 'Chào mừng đến với RepoChat!',
        subtitle: 'Trợ lý AI thông minh cho việc phân tích và review code',
        description: 'Hãy bắt đầu bằng cách hỏi một câu hỏi hoặc thử một trong những ví dụ dưới đây:'
      },

      // Example Questions
      exampleQuestions: [
        'Phân tích kiến trúc của dự án này',
        'Tìm các vấn đề bảo mật trong code',
        'Đề xuất cải thiện performance',
        'Review coding standards và best practices',
        'Giải thích luồng xử lý chính của ứng dụng',
        'Tìm các anti-patterns trong codebase'
      ],

      // API Configuration
      apiConfig: {
        baseUrl: 'http://localhost:8000',
        timeout: 30000,
        maxRetries: 3
      }
    }
  },

  computed: {
    currentChatTitle() {
      if (!this.currentChatId) return 'Trợ lý AI Code Review';
      
      const chat = this.chats.get(this.currentChatId);
      return chat?.title || 'Cuộc trò chuyện mới';
    },

    currentChatMessages() {
      if (!this.currentChatId) return [];
      
      const chat = this.chats.get(this.currentChatId);
      return chat?.messages || [];
    }
  },

  methods: {
    // === Navigation Methods ===
    
    openSettings() {
      console.log('Opening settings...');
      this.currentView = 'settings';
    },

    goBackFromSettings() {
      console.log('Returning from settings...');
      this.currentView = 'chat';
    },

    handleSettingsSaved(settingsData) {
      console.log('Settings saved:', settingsData);
      // TODO: Apply settings to app state
      
      // Auto-close settings after a delay
      setTimeout(() => {
        this.goBackFromSettings();
      }, 2000);
    },

    // === Sidebar Methods (Simplified - no toggle behavior) ===
    
    closeSidebar() {
      // No-op: sidebar always visible now
      console.log('Sidebar close requested but ignored - sidebar always visible');
    },

    // === Chat Management Methods ===
    
    handleNewChat(chatData = null) {
      const newChatId = Date.now();
      const newChat = {
        id: newChatId,
        title: chatData?.title || 'Cuộc trò chuyện mới',
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date(),
        isFavorite: false
      };

      this.chats.set(newChatId, newChat);
      this.currentChatId = newChatId;

      console.log('Created new chat:', newChat);
    },

    handleSelectChat(chat) {
      this.currentChatId = chat.id;
      
      console.log('Selected chat:', chat.id, chat.title);
    },

    handleDeleteChat(chat) {
      this.chats.delete(chat.id);
      
      // If deleted chat was current, switch to new chat
      if (this.currentChatId === chat.id) {
        this.handleNewChat();
      }
      
      console.log('Deleted chat:', chat.id);
    },

    handleRenameChat(data) {
      const chat = this.chats.get(data.id);
      if (chat) {
        chat.title = data.newTitle;
        chat.updatedAt = new Date();
        console.log('Renamed chat:', data.id, 'to:', data.newTitle);
      }
    },

    handleExportChat(chat) {
      // Create export data
      const exportData = {
        title: chat.title,
        messages: chat.messages,
        createdAt: chat.createdAt,
        exportedAt: new Date()
      };

      // Create downloadable file
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `repochat-${chat.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
      a.click();
      URL.revokeObjectURL(url);

      console.log('Exported chat:', chat.id);
    },

    handleDuplicateChat(chat) {
      const newChatId = Date.now();
      const duplicatedChat = {
        id: newChatId,
        title: `${chat.title} (Copy)`,
                 messages: [...chat.messages],
         createdAt: new Date(),
         updatedAt: new Date(),
         isFavorite: false
      };

      this.chats.set(newChatId, duplicatedChat);
      this.currentChatId = newChatId;

      console.log('Duplicated chat:', chat.id, 'to:', newChatId);
    },

    handleToggleFavorite(chat) {
      const existingChat = this.chats.get(chat.id);
      if (existingChat) {
        existingChat.isFavorite = !existingChat.isFavorite;
        existingChat.updatedAt = new Date();
        console.log('Toggled favorite for chat:', chat.id, existingChat.isFavorite);
      }
    },

    handleClearAllChats() {
      if (confirm('Bạn có chắc chắn muốn xóa tất cả cuộc trò chuyện? Hành động này không thể hoàn tác.')) {
        this.chats.clear();
        this.handleNewChat();
        console.log('Cleared all chats');
      }
    },

    // === Message Handling ===
    
    async handleSendMessage(message) {
      if (!this.currentChatId) {
        this.handleNewChat();
      }

      const chat = this.chats.get(this.currentChatId);
      if (!chat) return;

      // Add user message
      const userMessage = {
        id: Date.now(),
        text: message,
        isUser: true,
        timestamp: new Date()
      };

             chat.messages.push(userMessage);
       chat.updatedAt = new Date();

      // Generate title from first message
      if (chat.messages.length === 1) {
        chat.title = this.generateChatTitle(message);
      }

      // Simulate AI response with delay
      setTimeout(() => {
        const botMessage = {
          id: Date.now() + 1,
          text: this.generateAIResponse(message),
          isUser: false,
          timestamp: new Date()
        };

        chat.messages.push(botMessage);
        chat.updatedAt = new Date();

        console.log('Added bot response to chat:', this.currentChatId);
      }, 1000 + Math.random() * 2000); // 1-3 second delay
    },

    handleRefreshChat() {
      if (this.currentChatId) {
        const chat = this.chats.get(this.currentChatId);
        if (chat && chat.messages.length > 0) {
          // Get the last user message and regenerate response
          const lastUserMessage = [...chat.messages].reverse().find(m => m.isUser);
          if (lastUserMessage) {
            // Remove last bot message if exists
            const lastBotIndex = chat.messages.findLastIndex(m => !m.isUser);
            if (lastBotIndex > -1) {
              chat.messages.splice(lastBotIndex, 1);
            }

            // Generate new response
            setTimeout(() => {
              const botMessage = {
                id: Date.now(),
                text: this.generateAIResponse(lastUserMessage.text),
                isUser: false,
                timestamp: new Date()
              };

              chat.messages.push(botMessage);
              chat.updatedAt = new Date();

              console.log('Refreshed chat response:', this.currentChatId);
            }, 1000);
          }
        }
      }
    },

    generateAIResponse(message) {
      // Mock AI responses với nội dung thực tế hữu ích
      const responses = {
        'kiến trúc': `🏗️ **Phân tích Kiến trúc Dự án**

Dựa trên codebase đã scan, đây là phân tích kiến trúc tổng quan:

**📋 Cấu trúc Dự án:**
- **Frontend**: Vue.js 3 với Composition API
- **Backend**: Python FastAPI với multi-agent architecture  
- **Database**: Neo4j cho Code Knowledge Graph
- **Containerization**: Docker với multi-stage builds

**✅ Điểm Mạnh:**
- Clean separation of concerns với TEAM-based architecture
- Comprehensive logging và monitoring
- Production-ready Docker setup
- Modern frontend với responsive design

**⚠️ Cần Cải thiện:**
- API documentation có thể detailed hơn
- Error handling ở một số endpoints
- Test coverage cho integration scenarios

**🚀 Khuyến nghị:**
1. Implement comprehensive API docs với OpenAPI/Swagger
2. Add more integration tests cho multi-agent workflows  
3. Consider implementing caching layer cho better performance`,

        'bảo mật': `🔒 **Security Audit Report**

Sau khi scan codebase, tôi tìm thấy các vấn đề bảo mật:

**🔴 Critical:**
- API endpoints thiếu input validation
- Chưa implement CSRF protection
- Missing rate limiting cho API calls

**🟡 Medium:**
- XSS prevention cần được strengthen
- JWT tokens không có proper expiration handling
- File upload validation chưa đầy đủ

**🔧 Khuyến nghị:**
1. Implement \`express-validator\` cho API validation
2. Add \`csurf\` middleware cho CSRF protection  
3. Use \`express-rate-limit\` cho API rate limiting
4. Sanitize user inputs với \`DOMPurify\``,

        'performance': `⚡ **Performance Analysis**

Dựa trên phân tích, đây là các tối ưu được đề xuất:

**📦 Bundle Optimization:**
- Hiện tại bundle size: ~2.3MB
- Có thể giảm xuống ~800KB với các tối ưu sau:

**🎯 Immediate Actions:**
1. **Code Splitting**: Implement dynamic imports cho routes
   \`\`\`javascript
   const Settings = () => import('./views/Settings.vue')
   \`\`\`

2. **Tree Shaking**: Remove unused CSS và JS code
3. **Image Optimization**: Convert to WebP format (30-50% size reduction)
4. **Lazy Loading**: Components và images off-screen

**📊 Expected Results:**
- Load time: 2.1s → 0.8s  
- Bundle size: 2.3MB → 800KB
- Core Web Vitals: All green scores`,

        'standards': `📋 **Code Standards Review**

**✅ Following Best Practices:**
- Consistent naming conventions (camelCase, PascalCase)
- Proper component structure với single responsibility
- ESLint rules được tuân thủ tốt
- Git commit messages theo conventional format

**⚠️ Areas for Improvement:**

**TypeScript Integration:**
\`\`\`typescript
// Current: Plain JavaScript
export default {
  name: 'Component'
}

// Recommended: TypeScript
export default defineComponent({
  name: 'Component'
}) as DefineComponent
\`\`\`

**Documentation:**
- JSDoc comments cho functions
- Component props documentation
- API endpoint documentation

**Testing Coverage:**
- Current: ~45% coverage
- Target: 80%+ coverage
- Missing: Edge cases và error scenarios`
      };

      // Find matching response based on keywords
      for (const [keyword, response] of Object.entries(responses)) {
        if (message.toLowerCase().includes(keyword)) {
          return response;
        }
      }

      // Default intelligent response
      return `Tôi đã nhận được câu hỏi: "${message}"

Để có thể trả lời chính xác và hữu ích hơn, bạn có thể cung cấp thêm thông tin về:

🔹 **Ngôn ngữ/Framework**: JavaScript, Python, Vue.js, React, etc.
🔹 **Loại phân tích**: Security audit, performance review, code quality
🔹 **Scope**: Specific files, components, hoặc toàn bộ project
🔹 **Repository URL**: Để tôi có thể clone và phân tích chi tiết

**Ví dụ câu hỏi tốt:**
- "Phân tích security cho Vue.js project tại https://github.com/user/repo"
- "Review performance của React components trong folder /src/components"
- "Tìm code smells trong Python backend API"

Hãy thử lại với thông tin cụ thể hơn! 🚀`;
    },

    // === Helper Methods ===
    
    generateChatTitle(message) {
      // Generate meaningful chat title from first message
      const cleanMessage = message.trim().toLowerCase();
      
      if (cleanMessage.includes('phân tích')) return 'Phân tích dự án';
      if (cleanMessage.includes('bảo mật') || cleanMessage.includes('security')) return 'Security audit';
      if (cleanMessage.includes('performance')) return 'Performance review';
      if (cleanMessage.includes('review') || cleanMessage.includes('code')) return 'Code review';
      if (cleanMessage.includes('bug') || cleanMessage.includes('lỗi')) return 'Bug investigation';
      
      // Fallback: use first few words
      const words = message.split(' ').slice(0, 4).join(' ');
      return words.length > 30 ? words.substring(0, 30) + '...' : words;
    },

    // === Lifecycle Methods ===
    
    loadUserSettings() {
      // Load user settings from localStorage
      const saved = localStorage.getItem('repochat-settings');
      if (saved) {
        try {
          const settings = JSON.parse(saved);
          this.userSettings = { ...this.userSettings, ...settings };
        } catch (error) {
          console.warn('Failed to load user settings:', error);
        }
      }
    },

    saveUserSettings() {
      // Save user settings to localStorage
      localStorage.setItem('repochat-settings', JSON.stringify(this.userSettings));
    }
  },

  mounted() {
    // Load user settings
    this.loadUserSettings();
    
    // Create initial chat
    this.handleNewChat();
    
    // No more responsive sidebar logic - always visible
    
    // Check online status periodically
    setInterval(() => {
      // This could be used to check backend connectivity
    }, 30000);

    console.log('RepoChat App initialized with fixed sidebar layout');
  },

  beforeUnmount() {
    // Save user settings before leaving
    this.saveUserSettings();
  }
}
</script>

<style>
/* Global styles are already in main.css */
/* App-specific styles can be added here if needed */
.app-container {
  display: flex;
  height: 100vh;
}
</style> 