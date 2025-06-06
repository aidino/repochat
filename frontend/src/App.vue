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
        @repository-scanned="handleRepositoryScanned"
        @error="handleApiError"
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

    // === Chat Message Methods (Updated for API Integration) ===
    
    handleSendMessage(message) {
      if (!this.currentChatId) {
        this.handleNewChat();
      }

      const chat = this.chats.get(this.currentChatId);
      if (!chat) {
        console.error('Current chat not found');
        return;
      }

      // Message handling is now done in ChatInterface component
      // This method is kept for backward compatibility
      console.log('Message sent via ChatInterface:', message);
    },

    handleRefreshChat() {
      if (!this.currentChatId) return;

      const chat = this.chats.get(this.currentChatId);
      if (chat) {
        chat.messages = [];
        chat.updatedAt = new Date();
        console.log('Refreshed chat:', this.currentChatId);
      }
    },

    // === API Error Handling ===
    
    handleApiError(error) {
      console.error('API Error occurred:', error);
      
      // Show user-friendly error notification
      this.showErrorNotification(
        'Đã xảy ra lỗi kết nối. Vui lòng kiểm tra kết nối mạng và thử lại.'
      );
    },

    handleRepositoryScanned(result) {
      console.log('Repository scan completed:', result);
      
      // Update current chat title to reflect repository
      if (this.currentChatId && result.repository_url) {
        const chat = this.chats.get(this.currentChatId);
        if (chat) {
          // Extract repo name from URL for better title
          const repoName = this.extractRepoName(result.repository_url);
          chat.title = `Phân tích: ${repoName}`;
          chat.updatedAt = new Date();
          
          console.log('Updated chat title:', chat.title);
        }
      }

      // Show success notification
      this.showSuccessNotification(
        'Repository đã được quét thành công! Bạn có thể bắt đầu hỏi câu hỏi về code.'
      );
    },

    // === Utility Methods ===
    
    extractRepoName(repositoryUrl) {
      try {
        // Extract repo name from GitHub/GitLab URL
        const match = repositoryUrl.match(/[\/:]([^\/]+)\/([^\/]+)(?:\.git)?$/);
        if (match) {
          return `${match[1]}/${match[2].replace(/\.git$/, '')}`;
        }
        return 'Repository';
      } catch (error) {
        return 'Repository';
      }
    },

    showErrorNotification(message) {
      // Simple notification system - can be enhanced later
      console.error('ERROR:', message);
      
      // You can integrate with a toast notification library here
      // For now, we'll use browser alert as fallback
      if (window.confirm) {
        alert(`❌ ${message}`);
      }
    },

    showSuccessNotification(message) {
      // Simple notification system - can be enhanced later
      console.log('SUCCESS:', message);
      
      // You can integrate with a toast notification library here
      // For now, we'll use browser alert as fallback
      if (window.confirm) {
        alert(`✅ ${message}`);
      }
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