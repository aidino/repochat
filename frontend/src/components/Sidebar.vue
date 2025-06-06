<template>
  <aside class="sidebar">
    <!-- Sidebar Header -->
    <div class="sidebar-header">
      <h1 class="app-title">
        <span class="app-icon">🤖</span>
        RepoChat
      </h1>
      <span class="app-version">v1.0</span>
    </div>
    
    <!-- Sidebar Actions -->
    <div class="sidebar-actions">
      <button 
        class="btn btn-primary w-full mb-4" 
        @click="handleNewChat"
        :disabled="isLoading"
      >
        <span class="icon">➕</span>
        Chat Mới
      </button>
      
      <button 
        class="btn btn-secondary w-full mb-4" 
        @click="handleSettings"
        :disabled="isLoading"
      >
        <span class="icon">⚙️</span>
        Cài Đặt
      </button>
    </div>
    
    <!-- Chat History Section -->
    <div class="chat-history">
      <div class="history-header">
        <h3 class="history-title">Lịch Sử Chat</h3>
        <button 
          class="btn btn-icon"
          @click="refreshHistory"
          :disabled="isRefreshing"
          title="Làm mới lịch sử"
        >
          <span class="icon" :class="{ 'spinning': isRefreshing }">🔄</span>
        </button>
      </div>
      
      <!-- Search Chat History -->
      <div class="history-search" v-if="showSearch">
        <input
          v-model="searchQuery"
          class="input search-input"
          placeholder="Tìm kiếm chat..."
          @input="filterHistory"
        />
      </div>
      
      <!-- History List -->
      <div class="history-list">
        <div 
          v-for="chat in filteredChatHistory" 
          :key="chat.id"
          class="history-item"
          :class="{ 
            active: chat.id === currentChatId,
            recent: isRecentChat(chat.date)
          }"
          @click="handleSelectChat(chat.id)"
          @contextmenu.prevent="showContextMenu($event, chat)"
        >
          <div class="history-content">
            <div class="history-title" :title="chat.title">
              {{ truncateTitle(chat.title) }}
            </div>
            <div class="history-meta">
              <span class="history-date">{{ formatDate(chat.date) }}</span>
              <span class="history-message-count" v-if="chat.messageCount">
                {{ chat.messageCount }} tin nhắn
              </span>
            </div>
            <div class="history-preview" v-if="chat.lastMessage">
              {{ truncateMessage(chat.lastMessage) }}
            </div>
          </div>
          
          <!-- Chat actions -->
          <div class="history-actions">
            <button 
              class="btn btn-icon history-action"
              @click.stop="toggleChatFavorite(chat.id)"
              :title="chat.isFavorite ? 'Bỏ yêu thích' : 'Yêu thích'"
            >
              <span class="icon">{{ chat.isFavorite ? '⭐' : '☆' }}</span>
            </button>
            <button 
              class="btn btn-icon history-action"
              @click.stop="deleteChat(chat.id)"
              title="Xóa chat"
            >
              <span class="icon">🗑️</span>
            </button>
          </div>
        </div>
        
        <!-- Empty state -->
        <div v-if="filteredChatHistory.length === 0" class="history-empty">
          <span class="icon">💬</span>
          <p v-if="searchQuery">Không tìm thấy chat nào phù hợp</p>
          <p v-else>Chưa có lịch sử chat</p>
        </div>
      </div>
      
      <!-- Load more button -->
      <button 
        v-if="hasMoreHistory"
        class="btn btn-text w-full mt-2"
        @click="loadMoreHistory"
        :disabled="isLoadingMore"
      >
        {{ isLoadingMore ? 'Đang tải...' : 'Xem thêm' }}
      </button>
    </div>

    <!-- Context Menu -->
    <div 
      v-if="contextMenu.show"
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <button class="context-menu-item" @click="renameChat(contextMenu.chat)">
        <span class="icon">✏️</span>
        Đổi tên
      </button>
      <button class="context-menu-item" @click="duplicateChat(contextMenu.chat)">
        <span class="icon">📋</span>
        Sao chép
      </button>
      <button class="context-menu-item" @click="exportChat(contextMenu.chat)">
        <span class="icon">📤</span>
        Xuất chat
      </button>
      <hr class="context-menu-divider">
      <button 
        class="context-menu-item danger" 
        @click="deleteChat(contextMenu.chat.id)"
      >
        <span class="icon">🗑️</span>
        Xóa
      </button>
    </div>

    <!-- Sidebar Footer -->
    <div class="sidebar-footer">
      <div class="footer-stats">
        <span class="stat-item">{{ chatHistory.length }} chats</span>
        <span class="stat-item">{{ getTotalMessages() }} tin nhắn</span>
      </div>
      
      <button 
        class="btn btn-icon"
        @click="toggleSearch"
        :class="{ active: showSearch }"
        title="Tìm kiếm"
      >
        <span class="icon">🔍</span>
      </button>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'Sidebar',
  
  props: {
    currentChatId: {
      type: [Number, String],
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  
  emits: [
    'new-chat',
    'open-settings', 
    'select-chat',
    'delete-chat',
    'rename-chat',
    'duplicate-chat',
    'export-chat'
  ],
  
  data() {
    return {
      // Search functionality
      showSearch: false,
      searchQuery: '',
      filteredChatHistory: [],
      
      // Loading states
      isRefreshing: false,
      isLoadingMore: false,
      
      // Pagination
      hasMoreHistory: false,
      historyPage: 1,
      
      // Context menu
      contextMenu: {
        show: false,
        x: 0,
        y: 0,
        chat: null
      },
      
      // Mock chat history data (enhanced)
      chatHistory: [
        {
          id: 1,
          title: 'Phân tích Spring Pet Clinic',
          date: new Date(Date.now() - 3600000), // 1 hour ago
          messageCount: 15,
          lastMessage: 'Cảm ơn bạn đã phân tích repository này rất chi tiết!',
          isFavorite: true,
          tags: ['spring', 'java', 'analysis']
        },
        {
          id: 2,
          title: 'Review PR #123 - User Authentication',
          date: new Date(Date.now() - 86400000), // 1 day ago
          messageCount: 8,
          lastMessage: 'Pull request này trông khá tốt, chỉ có một vài lưu ý nhỏ.',
          isFavorite: false,
          tags: ['pr-review', 'auth', 'security']
        },
        {
          id: 3,
          title: 'Tìm class User trong codebase',
          date: new Date(Date.now() - 172800000), // 2 days ago
          messageCount: 5,
          lastMessage: 'Class User được định nghĩa trong file src/main/java/User.java',
          isFavorite: false,
          tags: ['search', 'class', 'java']
        },
        {
          id: 4,
          title: 'Circular Dependencies Analysis',
          date: new Date(Date.now() - 259200000), // 3 days ago
          messageCount: 12,
          lastMessage: 'Đã tìm thấy 2 circular dependencies cần được xử lý.',
          isFavorite: true,
          tags: ['dependencies', 'analysis', 'architecture']
        },
        {
          id: 5,
          title: 'Code Quality Report cho Project X',
          date: new Date(Date.now() - 345600000), // 4 days ago
          messageCount: 20,
          lastMessage: 'Overall code quality score: 8.5/10. Rất tốt!',
          isFavorite: false,
          tags: ['quality', 'report', 'metrics']
        },
        {
          id: 6,
          title: 'Database Schema Review',
          date: new Date(Date.now() - 432000000), // 5 days ago
          messageCount: 7,
          lastMessage: 'Schema có vẻ chuẩn, nhưng nên thêm indexes cho performance.',
          isFavorite: false,
          tags: ['database', 'schema', 'performance']
        }
      ]
    }
  },
  
  computed: {
    // Get total message count across all chats
    getTotalMessages() {
      return () => this.chatHistory.reduce((total, chat) => total + (chat.messageCount || 0), 0)
    }
  },
  
  watch: {
    // Update filtered history when chat history changes
    chatHistory: {
      handler() {
        this.filterHistory()
      },
      immediate: true
    }
  },
  
  mounted() {
    // Close context menu when clicking outside
    document.addEventListener('click', this.closeContextMenu)
    
    // Initialize filtered history
    this.filterHistory()
    
    // Simulate having more history for pagination
    this.hasMoreHistory = this.chatHistory.length >= 5
  },
  
  beforeUnmount() {
    document.removeEventListener('click', this.closeContextMenu)
  },
  
  methods: {
    // === Core Actions ===
    handleNewChat() {
      this.$emit('new-chat')
    },
    
    handleSettings() {
      this.$emit('open-settings')
    },
    
    handleSelectChat(chatId) {
      this.$emit('select-chat', chatId)
    },
    
    // === History Management ===
    refreshHistory() {
      this.isRefreshing = true
      // Simulate API call
      setTimeout(() => {
        this.isRefreshing = false
        // In real app, reload from API
        console.log('Chat history refreshed')
      }, 1000)
    },
    
    filterHistory() {
      if (!this.searchQuery.trim()) {
        this.filteredChatHistory = [...this.chatHistory]
      } else {
        const query = this.searchQuery.toLowerCase()
        this.filteredChatHistory = this.chatHistory.filter(chat =>
          chat.title.toLowerCase().includes(query) ||
          (chat.lastMessage && chat.lastMessage.toLowerCase().includes(query)) ||
          (chat.tags && chat.tags.some(tag => tag.toLowerCase().includes(query)))
        )
      }
    },
    
    loadMoreHistory() {
      this.isLoadingMore = true
      // Simulate loading more history
      setTimeout(() => {
        // In real app, load next page from API
        this.historyPage++
        this.isLoadingMore = false
        this.hasMoreHistory = false // For demo, disable after first load
        console.log('Loaded more history')
      }, 1500)
    },
    
    // === Chat Actions ===
    toggleChatFavorite(chatId) {
      const chat = this.chatHistory.find(c => c.id === chatId)
      if (chat) {
        chat.isFavorite = !chat.isFavorite
        console.log(`Chat ${chatId} ${chat.isFavorite ? 'added to' : 'removed from'} favorites`)
      }
    },
    
    deleteChat(chatId) {
      if (confirm('Bạn có chắc chắn muốn xóa chat này?')) {
        this.chatHistory = this.chatHistory.filter(chat => chat.id !== chatId)
        this.closeContextMenu()
        this.$emit('delete-chat', chatId)
        console.log(`Chat ${chatId} deleted`)
      }
    },
    
    renameChat(chat) {
      const newTitle = prompt('Nhập tên mới cho chat:', chat.title)
      if (newTitle && newTitle.trim()) {
        chat.title = newTitle.trim()
        this.closeContextMenu()
        this.$emit('rename-chat', { id: chat.id, title: newTitle.trim() })
        console.log(`Chat ${chat.id} renamed to: ${newTitle}`)
      }
    },
    
    duplicateChat(chat) {
      const newChat = {
        ...chat,
        id: Date.now(),
        title: `${chat.title} (Copy)`,
        date: new Date(),
        messageCount: 0,
        lastMessage: '',
        isFavorite: false
      }
      this.chatHistory.unshift(newChat)
      this.closeContextMenu()
      this.$emit('duplicate-chat', newChat)
      console.log(`Chat duplicated: ${newChat.title}`)
    },
    
    exportChat(chat) {
      // Simulate export functionality
      const exportData = {
        title: chat.title,
        date: chat.date,
        messageCount: chat.messageCount,
        tags: chat.tags
      }
      
      console.log('Exporting chat:', exportData)
      alert(`Xuất chat "${chat.title}" thành công! (Mock feature)`)
      this.closeContextMenu()
      this.$emit('export-chat', chat)
    },
    
    // === Context Menu ===
    showContextMenu(event, chat) {
      this.contextMenu = {
        show: true,
        x: event.clientX,
        y: event.clientY,
        chat: chat
      }
    },
    
    closeContextMenu() {
      this.contextMenu.show = false
    },
    
    // === UI Helpers ===
    toggleSearch() {
      this.showSearch = !this.showSearch
      if (!this.showSearch) {
        this.searchQuery = ''
        this.filterHistory()
      }
    },
    
    // === Utility Functions ===
    formatDate(date) {
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 1) return 'Hôm qua'
      if (diffDays <= 7) return `${diffDays} ngày trước`
      if (diffDays <= 30) return `${Math.ceil(diffDays / 7)} tuần trước`
      
      return date.toLocaleDateString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    },
    
    isRecentChat(date) {
      const now = new Date()
      const diffHours = Math.abs(now - date) / (1000 * 60 * 60)
      return diffHours <= 24 // Recent if within 24 hours
    },
    
    truncateTitle(title, maxLength = 25) {
      return title.length > maxLength ? title.substring(0, maxLength) + '...' : title
    },
    
    truncateMessage(message, maxLength = 40) {
      return message.length > maxLength ? message.substring(0, maxLength) + '...' : message
    }
  }
}
</script>

<style scoped>
/* Sidebar Container - Gemini Design */
.sidebar {
  width: 300px;
  height: 100vh;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border-subtle);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(20px);
}

/* Sidebar Header */
.sidebar-header {
  padding: var(--space-6) var(--space-4);
  border-bottom: 1px solid var(--color-border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--gradient-primary);
  color: var(--color-text-inverse);
}

.app-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-inverse);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0;
  letter-spacing: -0.025em;
}

.app-icon {
  font-size: var(--font-size-3xl);
}

.app-version {
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.15);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-lg);
  font-weight: var(--font-weight-medium);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Sidebar Actions */
.sidebar-actions {
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border-subtle);
  background: var(--color-background-secondary);
}

/* Chat History */
.chat-history {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: var(--space-4) 0;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-4) var(--space-2) var(--space-4);
}

.history-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.btn-icon {
  padding: var(--space-2);
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-icon:hover {
  background: var(--color-background-secondary);
  color: var(--color-text-primary);
  transform: translateY(-1px);
}

.btn-icon.active {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Search */
.history-search {
  padding: 0 var(--space-4) var(--space-2) var(--space-4);
}

.search-input {
  width: 100%;
  font-size: var(--font-size-sm);
  border-radius: var(--radius-xl);
  border: 2px solid var(--color-border);
  padding: var(--space-3);
  font-family: var(--font-family-primary);
}

.search-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1);
}

/* History List */
.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-2);
}

.history-item {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-2);
  margin-bottom: var(--space-1);
  border-radius: var(--radius-xl);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
  position: relative;
  backdrop-filter: blur(10px);
}

.history-item:hover {
  background: var(--color-background-secondary);
  border-color: var(--color-border);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.history-item.active {
  background: var(--gradient-primary);
  color: var(--color-text-inverse);
  border-color: transparent;
  box-shadow: var(--shadow-md);
}

.history-item.recent::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--color-brown);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.history-content {
  flex: 1;
  min-width: 0;
}

.history-item .history-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}

.history-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.history-item.active .history-date {
  color: rgba(255, 255, 255, 0.8);
}

.history-message-count {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  background: var(--color-background-tertiary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-lg);
  font-weight: var(--font-weight-medium);
}

.history-item.active .history-message-count {
  background: rgba(255, 255, 255, 0.2);
  color: var(--color-text-inverse);
}

.history-preview {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-item.active .history-preview {
  color: rgba(255, 255, 255, 0.7);
}

/* History Actions */
.history-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.history-item:hover .history-actions {
  opacity: 1;
}

.history-action {
  padding: 0.25rem;
  font-size: 0.75rem;
}

.history-action .icon {
  font-size: 0.875rem;
}

/* Empty State */
.history-empty {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--text-secondary);
}

.history-empty .icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  display: block;
}

.history-empty p {
  margin: 0;
  font-size: 0.875rem;
}

/* Context Menu */
.context-menu {
  position: fixed;
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  z-index: var(--z-popover);
  min-width: 150px;
  padding: var(--space-2) 0;
  backdrop-filter: blur(20px);
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-2) var(--space-4);
  border: none;
  background: transparent;
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-family-primary);
  font-weight: var(--font-weight-medium);
}

.context-menu-item:hover {
  background: var(--color-background-secondary);
  transform: translateX(2px);
}

.context-menu-item.danger {
  color: var(--color-error);
}

.context-menu-item.danger:hover {
  background: var(--error-50);
}

.context-menu-divider {
  border: none;
  border-top: 1px solid var(--color-border-subtle);
  margin: var(--space-2) 0;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid var(--color-border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-background-secondary);
}

.footer-stats {
  display: flex;
  gap: var(--space-4);
}

.stat-item {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    width: 280px;
  }
  
  .history-item .history-title {
    font-size: var(--font-size-xs);
  }
  
  .sidebar-header {
    padding: var(--space-4) var(--space-3);
  }
  
  .sidebar-actions {
    padding: var(--space-3);
  }
  
  .chat-history {
    padding: var(--space-3) 0;
  }
}

@media (max-width: 480px) {
  .sidebar {
    width: 100%;
    position: fixed;
    z-index: var(--z-fixed);
  }
  
  .app-title {
    font-size: var(--font-size-lg);
  }
  
  .sidebar-header {
    padding: var(--space-3);
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .sidebar-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  }
  
  .sidebar-footer {
    background: var(--neutral-800);
  }
}

/* Accessibility improvements */
.btn-icon:focus-visible,
.search-input:focus-visible,
.context-menu-item:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
</style> 