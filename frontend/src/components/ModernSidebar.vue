<template>
  <div class="sidebar" :class="{ 'sidebar-mobile-hidden': !showOnMobile }">
    <!-- Sidebar Header -->
    <div class="sidebar-header">
      <div class="sidebar-brand">
        <h1 class="text-xl font-bold text-primary">RepoChat</h1>
        <p class="text-sm text-tertiary">AI Code Assistant</p>
      </div>
      <button 
        @click="$emit('close-sidebar')"
        class="sidebar-close-btn lg:hidden"
      >
        ✕
      </button>
    </div>

    <!-- Sidebar Content -->
    <div class="sidebar-content">
      <!-- New Chat Button -->
      <button 
        @click="createNewChat" 
        class="new-chat-btn"
        :disabled="isCreatingChat"
      >
        <span class="mr-2">💬</span>
        <span>Cuộc trò chuyện mới</span>
        <span v-if="isCreatingChat" class="ml-auto animate-pulse">⏳</span>
      </button>

      <!-- Chat History Section -->
      <div class="chat-history-section" v-if="chatHistory.length > 0">
        <div class="section-header">
          <h4 class="text-sm font-medium text-secondary mb-3">
            Lịch sử chat ({{ chatHistory.length }})
          </h4>
          <button 
            @click="toggleHistoryCollapsed"
            class="text-tertiary hover:text-secondary transition-colors"
          >
            <span v-if="historyCollapsed">▶</span>
            <span v-else>▼</span>
          </button>
        </div>

        <div v-if="!historyCollapsed" class="chat-list">
          <div 
            v-for="chat in displayedChats" 
            :key="chat.id"
            @click="selectChat(chat)"
            @contextmenu.prevent="showChatContextMenu(chat, $event)"
            :class="[
              'chat-item',
              { 'chat-item-active': chat.id === currentChatId }
            ]"
          >
            <div class="chat-icon">
              <span>{{ getChatIcon(chat) }}</span>
            </div>
            <div class="chat-info">
              <div class="chat-title">{{ chat.title }}</div>
              <div class="chat-preview">{{ chat.lastMessage || 'Cuộc trò chuyện mới' }}</div>
              <div class="chat-meta">
                <span class="chat-time">{{ formatChatTime(chat.updatedAt) }}</span>
                <span v-if="chat.messageCount" class="message-count">
                  {{ chat.messageCount }} tin nhắn
                </span>
              </div>
            </div>
            <div class="chat-actions">
              <button 
                @click.stop="toggleChatFavorite(chat)"
                class="action-btn"
                :class="{ 'favorited': chat.isFavorite }"
              >
                <span v-if="chat.isFavorite">⭐</span>
                <span v-else>☆</span>
              </button>
              <button 
                @click.stop="showChatContextMenu(chat, $event)"
                class="action-btn"
              >
                ⋯
              </button>
            </div>
          </div>

          <!-- Load More Button -->
          <button 
            v-if="hasMoreChats"
            @click="loadMoreChats"
            class="load-more-btn"
            :disabled="isLoadingMore"
          >
            <span v-if="isLoadingMore" class="animate-pulse">Đang tải...</span>
            <span v-else>Xem thêm {{ remainingChatsCount }} cuộc trò chuyện</span>
          </button>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions-section">
        <h4 class="text-sm font-medium text-secondary mb-3">Thao tác nhanh</h4>
        <div class="quick-actions">
          <button @click="$emit('open-settings')" class="quick-action-btn">
            <span class="mr-2">⚙️</span>
            Cài đặt
          </button>
          <button @click="exportChatHistory" class="quick-action-btn">
            <span class="mr-2">📥</span>
            Xuất lịch sử
          </button>
          <button @click="clearAllChats" class="quick-action-btn">
            <span class="mr-2">🗑️</span>
            Xóa tất cả
          </button>
        </div>
      </div>

      <!-- User Info -->
      <div class="user-info-section">
        <div class="user-info">
          <div class="user-avatar">
            <span>👤</span>
          </div>
          <div class="user-details">
            <div class="user-name">{{ userName || 'User' }}</div>
            <div class="user-status">
              <div class="status-dot online"></div>
              <span class="status-text">Trực tuyến</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Context Menu -->
    <div 
      v-if="contextMenu.show"
      ref="contextMenu"
      class="context-menu"
      :style="contextMenuStyle"
      @click.stop
    >
      <div class="context-menu-header">
        <strong>{{ contextMenu.chat?.title }}</strong>
      </div>
      <button 
        v-for="action in contextMenuActions" 
        :key="action.key"
        @click="executeContextAction(action.key)"
        class="context-menu-item"
        :class="{ destructive: action.destructive }"
      >
        <span class="mr-2">{{ action.icon }}</span>
        {{ action.label }}
      </button>
    </div>

    <!-- Overlay for mobile -->
    <div 
      v-if="showOnMobile" 
      class="sidebar-overlay lg:hidden"
      @click="$emit('close-sidebar')"
    ></div>
  </div>
</template>

<script>
export default {
  name: 'ModernSidebar',

  props: {
    showOnMobile: {
      type: Boolean,
      default: false
    },
    currentChatId: {
      type: [String, Number],
      default: null
    },
    userName: {
      type: String,
      default: ''
    }
  },

  emits: [
    'new-chat',
    'select-chat', 
    'delete-chat',
    'rename-chat',
    'export-chat',
    'duplicate-chat',
    'open-settings',
    'close-sidebar'
  ],

  data() {
    return {
      chatHistory: [
        {
          id: 1,
          title: 'Phân tích dự án Vue.js',
          lastMessage: 'Component structure trông tốt...',
          messageCount: 15,
          updatedAt: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
          isFavorite: true
        },
        {
          id: 2,
          title: 'Review code React',
          lastMessage: 'Tìm thấy một số hook patterns...',
          messageCount: 8,
          updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
          isFavorite: false
        },
        {
          id: 3,
          title: 'Tối ưu performance',
          lastMessage: 'Bundle size có thể được reduce...',
          messageCount: 23,
          updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
          isFavorite: false
        },
        {
          id: 4,
          title: 'Security audit',
          lastMessage: 'Phát hiện các vấn đề CSRF...',
          messageCount: 12,
          updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
          isFavorite: true
        }
      ],
      historyCollapsed: false,
      displayLimit: 10,
      isCreatingChat: false,
      isLoadingMore: false,
      contextMenu: {
        show: false,
        chat: null,
        x: 0,
        y: 0
      }
    }
  },

  computed: {
    displayedChats() {
      // Sort by favorites first, then by updatedAt
      const sorted = [...this.chatHistory].sort((a, b) => {
        if (a.isFavorite !== b.isFavorite) {
          return b.isFavorite - a.isFavorite;
        }
        return new Date(b.updatedAt) - new Date(a.updatedAt);
      });
      return sorted.slice(0, this.displayLimit);
    },

    hasMoreChats() {
      return this.chatHistory.length > this.displayLimit;
    },

    remainingChatsCount() {
      return Math.max(0, this.chatHistory.length - this.displayLimit);
    },

    contextMenuStyle() {
      return {
        left: this.contextMenu.x + 'px',
        top: this.contextMenu.y + 'px'
      };
    },

    contextMenuActions() {
      return [
        { key: 'rename', icon: '✏️', label: 'Đổi tên' },
        { key: 'duplicate', icon: '📋', label: 'Nhân bản' },
        { key: 'export', icon: '📤', label: 'Xuất chat' },
        { key: 'delete', icon: '🗑️', label: 'Xóa', destructive: true }
      ];
    }
  },

  methods: {
    async createNewChat() {
      this.isCreatingChat = true;
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const newChat = {
        id: Date.now(),
        title: 'Cuộc trò chuyện mới',
        lastMessage: '',
        messageCount: 0,
        updatedAt: new Date(),
        isFavorite: false
      };

      this.chatHistory.unshift(newChat);
      this.isCreatingChat = false;
      
      this.$emit('new-chat', newChat);
    },

    selectChat(chat) {
      this.$emit('select-chat', chat);
    },

    toggleHistoryCollapsed() {
      this.historyCollapsed = !this.historyCollapsed;
    },

    async loadMoreChats() {
      this.isLoadingMore = true;
      // Simulate loading more chats
      await new Promise(resolve => setTimeout(resolve, 1000));
      this.displayLimit += 10;
      this.isLoadingMore = false;
    },

    toggleChatFavorite(chat) {
      chat.isFavorite = !chat.isFavorite;
      // Emit event for persistence
      this.$emit('toggle-favorite', chat);
    },

    showChatContextMenu(chat, event) {
      event.preventDefault();
      this.contextMenu = {
        show: true,
        chat: chat,
        x: event.clientX,
        y: event.clientY
      };

      // Close context menu when clicking outside
      const closeMenu = () => {
        this.contextMenu.show = false;
        document.removeEventListener('click', closeMenu);
      };
      
      setTimeout(() => {
        document.addEventListener('click', closeMenu);
      }, 100);
    },

    executeContextAction(action) {
      const chat = this.contextMenu.chat;
      this.contextMenu.show = false;

      switch (action) {
        case 'rename':
          this.renameChat(chat);
          break;
        case 'duplicate':
          this.duplicateChat(chat);
          break;
        case 'export':
          this.exportChat(chat);
          break;
        case 'delete':
          this.deleteChat(chat);
          break;
      }
    },

    async renameChat(chat) {
      const newTitle = prompt('Nhập tên mới cho cuộc trò chuyện:', chat.title);
      if (newTitle && newTitle.trim()) {
        chat.title = newTitle.trim();
        this.$emit('rename-chat', { id: chat.id, title: newTitle.trim() });
      }
    },

    duplicateChat(chat) {
      const duplicatedChat = {
        ...chat,
        id: Date.now(),
        title: chat.title + ' (Bản sao)',
        updatedAt: new Date()
      };
      this.chatHistory.unshift(duplicatedChat);
      this.$emit('duplicate-chat', duplicatedChat);
    },

    exportChat(chat) {
      this.$emit('export-chat', chat);
    },

    deleteChat(chat) {
      if (confirm(`Bạn có chắc chắn muốn xóa cuộc trò chuyện "${chat.title}"?`)) {
        const index = this.chatHistory.findIndex(c => c.id === chat.id);
        if (index > -1) {
          this.chatHistory.splice(index, 1);
        }
        this.$emit('delete-chat', chat);
      }
    },

    exportChatHistory() {
      const data = JSON.stringify(this.chatHistory, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'repochat-history.json';
      a.click();
      URL.revokeObjectURL(url);
    },

    clearAllChats() {
      if (confirm('Bạn có chắc chắn muốn xóa tất cả lịch sử chat? Hành động này không thể hoàn tác.')) {
        this.chatHistory = [];
        this.$emit('clear-all-chats');
      }
    },

    getChatIcon(chat) {
      if (chat.isFavorite) return '⭐';
      if (chat.title.includes('Vue')) return '💚';
      if (chat.title.includes('React')) return '⚛️';
      if (chat.title.includes('security') || chat.title.includes('Security')) return '🔒';
      if (chat.title.includes('performance') || chat.title.includes('Performance')) return '⚡';
      return '💬';
    },

    formatChatTime(date) {
      const now = new Date();
      const diff = now - date;
      const minutes = Math.floor(diff / (1000 * 60));
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));

      if (minutes < 1) return 'Vừa xong';
      if (minutes < 60) return `${minutes} phút trước`;
      if (hours < 24) return `${hours} giờ trước`;
      if (days < 7) return `${days} ngày trước`;
      
      return date.toLocaleDateString('vi-VN', {
        day: '2-digit',
        month: '2-digit'
      });
    }
  }
}
</script>

<style scoped>
/* Mobile sidebar overlay */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
}

.sidebar-mobile-hidden {
  transform: translateX(-100%);
}

/* Sidebar header */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-brand {
  flex: 1;
}

.sidebar-close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--color-surface-hover);
  color: var(--color-text-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
}

.sidebar-close-btn:hover {
  background: var(--color-border);
  color: var(--color-text-primary);
}

/* New Chat Button */
.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  padding: var(--space-3);
  background: var(--color-primary);
  color: var(--color-text-primary);
  border: none;
  border-radius: var(--radius-lg);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: var(--transition-fast);
  margin-bottom: var(--space-4);
}

.new-chat-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
  transform: translateY(-1px);
}

.new-chat-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* Chat History Section */
.chat-history-section {
  margin-bottom: var(--space-6);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

/* Chat Items */
.chat-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: var(--transition-fast);
  border: 1px solid transparent;
}

.chat-item:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border);
}

.chat-item-active {
  background: rgba(102, 126, 234, 0.1);
  border-color: var(--color-primary);
}

.chat-icon {
  font-size: var(--font-size-lg);
  line-height: 1;
}

.chat-info {
  flex: 1;
  min-width: 0;
}

.chat-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-preview {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.message-count {
  padding: 2px 6px;
  background: var(--color-surface-hover);
  border-radius: var(--radius-full);
}

/* Chat Actions */
.chat-actions {
  display: flex;
  gap: var(--space-1);
  opacity: 0;
  transition: var(--transition-fast);
}

.chat-item:hover .chat-actions {
  opacity: 1;
}

.action-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
}

.action-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text-primary);
}

.action-btn.favorited {
  color: var(--color-warning);
}

/* Load More Button */
.load-more-btn {
  width: 100%;
  padding: var(--space-2);
  background: transparent;
  color: var(--color-text-tertiary);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-fast);
  font-size: var(--font-size-xs);
}

.load-more-btn:hover:not(:disabled) {
  color: var(--color-text-primary);
  border-color: var(--color-primary);
}

.load-more-btn:disabled {
  cursor: not-allowed;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.quick-action-btn {
  display: flex;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-fast);
  font-size: var(--font-size-sm);
}

.quick-action-btn:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-primary);
  color: var(--color-text-primary);
}

/* User Info */
.user-info-section {
  margin-top: auto;
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border-light);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--color-surface-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.user-status {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

/* Context Menu */
.context-menu {
  position: fixed;
  z-index: 1000;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--space-2);
  min-width: 180px;
}

.context-menu-header {
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-border-light);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.context-menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background: transparent;
  color: var(--color-text-primary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-fast);
  font-size: var(--font-size-sm);
  text-align: left;
}

.context-menu-item:hover {
  background: var(--color-surface-hover);
}

.context-menu-item.destructive {
  color: var(--color-error);
}

.context-menu-item.destructive:hover {
  background: rgba(245, 101, 101, 0.1);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 999;
    transform: translateX(0);
    transition: transform var(--transition-normal);
  }
  
  .sidebar-mobile-hidden {
    transform: translateX(-100%);
  }
}
</style> 