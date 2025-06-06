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
      <!-- Modern Sidebar -->
      <ModernSidebar
        :show-on-mobile="sidebarVisible"
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
        @toggle-sidebar="toggleSidebar"
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
      sidebarVisible: window.innerWidth >= 1024, // Show on desktop, hide on mobile by default
      
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
      this.sidebarVisible = false;
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

    // === Sidebar Methods ===
    
    toggleSidebar() {
      // Only toggle on mobile/tablet
      if (window.innerWidth < 1024) {
        this.sidebarVisible = !this.sidebarVisible;
      }
    },

    closeSidebar() {
      // Only close on mobile/tablet
      if (window.innerWidth < 1024) {
        this.sidebarVisible = false;
      }
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
        isFavorite: false,
        messageCount: 0
      };

      this.chats.set(newChatId, newChat);
      this.currentChatId = newChatId;
      this.sidebarVisible = false;

      console.log('Created new chat:', newChat);
    },

    handleSelectChat(chat) {
      this.currentChatId = chat.id;
      this.sidebarVisible = false;
      
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
        chat.title = data.title;
        chat.updatedAt = new Date();
      }
      
      console.log('Renamed chat:', data);
    },

    handleExportChat(chat) {
      const chatData = this.chats.get(chat.id);
      if (chatData) {
        const exportData = {
          ...chatData,
          exportedAt: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
          type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `repochat-${chat.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
      
      console.log('Exported chat:', chat.id);
    },

    handleDuplicateChat(chat) {
      const originalChat = this.chats.get(chat.id);
      if (originalChat) {
        const duplicatedChat = {
          ...originalChat,
          id: Date.now(),
          title: originalChat.title + ' (Bản sao)',
          createdAt: new Date(),
          updatedAt: new Date()
        };
        
        this.chats.set(duplicatedChat.id, duplicatedChat);
        this.currentChatId = duplicatedChat.id;
      }
      
      console.log('Duplicated chat:', chat.id);
    },

    handleToggleFavorite(chat) {
      const chatData = this.chats.get(chat.id);
      if (chatData) {
        chatData.isFavorite = chat.isFavorite;
        chatData.updatedAt = new Date();
      }
      
      console.log('Toggled favorite for chat:', chat.id, chat.isFavorite);
    },

    handleClearAllChats() {
      this.chats.clear();
      this.handleNewChat();
      
      console.log('Cleared all chats');
    },

    handleRefreshChat() {
      // Clear current chat messages
      if (this.currentChatId) {
        const chat = this.chats.get(this.currentChatId);
        if (chat) {
          chat.messages = [];
          chat.messageCount = 0;
          chat.updatedAt = new Date();
        }
      }
      
      console.log('Refreshed chat:', this.currentChatId);
    },

    // === Message Handling ===
    
    async handleSendMessage(data) {
      console.log('Sending message:', data.message);
      
      if (!this.currentChatId) {
        this.handleNewChat();
      }

      const chat = this.chats.get(this.currentChatId);
      if (!chat) return;

      // Update chat metadata
      chat.messageCount = (chat.messageCount || 0) + 1;
      chat.updatedAt = new Date();
      
      // Generate appropriate title for new chats
      if (chat.title === 'Cuộc trò chuyện mới' && data.message.length > 0) {
        chat.title = this.generateChatTitle(data.message);
      }

      try {
        // TODO: Replace with actual API call
        const response = await this.mockApiCall(data.message);
        
        // Handle successful response
        data.onResponse(response);
        
        // Update chat with bot response
        chat.messageCount += 1;
        chat.updatedAt = new Date();
        
      } catch (error) {
        console.error('Error sending message:', error);
        data.onError(error);
      }
    },

    // === Mock API Call (Replace with real backend integration) ===
    
    async mockApiCall(message) {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock intelligent responses
      const responses = {
        'phân tích': `🔍 **Phân tích dự án hoàn tất**

Tôi đã phân tích dự án của bạn và phát hiện:

**✅ Điểm mạnh:**
- Cấu trúc thư mục rõ ràng và có tổ chức
- Component architecture tốt với separation of concerns
- Modern CSS với CSS variables và utility classes

**⚠️ Cần cải thiện:**
- Thiếu unit tests cho một số components quan trọng
- Component state management có thể tối ưu hơn
- Accessibility features cần được bổ sung thêm

**🚀 Đề xuất:**
1. Implement Vue Testing Library cho unit tests
2. Consider Pinia cho centralized state management
3. Add ARIA labels và keyboard navigation support`,

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
    
    // Handle window resize for responsive sidebar
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        this.sidebarVisible = true; // Always show on desktop
      } else {
        this.sidebarVisible = false; // Hide on mobile by default
      }
    };
    
    window.addEventListener('resize', handleResize);
    
    // Store resize handler for cleanup
    this.resizeHandler = handleResize;
    
    // Check online status periodically
    setInterval(() => {
      // This could be used to check backend connectivity
    }, 30000);

    console.log('RepoChat App initialized with modern theme');
    },

  beforeUnmount() {
    // Cleanup event listeners
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
    }
    // Save user settings before leaving
    this.saveUserSettings();
  }
}
</script>

<style>
/* Global styles are already in main.css */
/* App-specific styles can be added here if needed */

/* Ensure proper mobile behavior */
@media (max-width: 768px) {
  .app-container {
    overflow: hidden;
  }
}
</style> 