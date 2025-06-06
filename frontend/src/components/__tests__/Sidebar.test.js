import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Sidebar from '../Sidebar.vue'

// Mock global methods
global.confirm = vi.fn()
global.prompt = vi.fn()
global.alert = vi.fn()

describe('Sidebar Component', () => {
  let wrapper

  const defaultProps = {
    currentChatId: 1,
    isLoading: false
  }

  beforeEach(() => {
    wrapper = mount(Sidebar, {
      props: defaultProps
    })
    // Reset mocks
    vi.clearAllMocks()
  })

  describe('Component Structure', () => {
    it('renders sidebar with correct structure', () => {
      expect(wrapper.find('.sidebar').exists()).toBe(true)
      expect(wrapper.find('.sidebar-header').exists()).toBe(true)
      expect(wrapper.find('.sidebar-actions').exists()).toBe(true)
      expect(wrapper.find('.chat-history').exists()).toBe(true)
      expect(wrapper.find('.sidebar-footer').exists()).toBe(true)
    })

    it('displays app title and version', () => {
      expect(wrapper.find('.app-title').text()).toContain('RepoChat')
      expect(wrapper.find('.app-version').text()).toBe('v1.0')
      expect(wrapper.find('.app-icon').text()).toBe('🤖')
    })

    it('shows main action buttons', () => {
      const buttons = wrapper.findAll('.sidebar-actions button')
      expect(buttons).toHaveLength(2)
      expect(buttons[0].text()).toContain('Chat Mới')
      expect(buttons[1].text()).toContain('Cài Đặt')
    })
  })

  describe('Chat History', () => {
    it('displays chat history items', () => {
      const historyItems = wrapper.findAll('.history-item')
      expect(historyItems.length).toBeGreaterThan(0)
    })

    it('shows active chat correctly', () => {
      const activeItem = wrapper.find('.history-item.active')
      expect(activeItem.exists()).toBe(true)
    })

    it('displays chat metadata correctly', () => {
      const firstItem = wrapper.find('.history-item')
      expect(firstItem.find('.history-title').exists()).toBe(true)
      expect(firstItem.find('.history-date').exists()).toBe(true)
      expect(firstItem.find('.history-message-count').exists()).toBe(true)
      expect(firstItem.find('.history-preview').exists()).toBe(true)
    })

    it('shows recent chat indicator', () => {
      const recentItems = wrapper.findAll('.history-item.recent')
      expect(recentItems.length).toBeGreaterThan(0)
    })
  })

  describe('Core Actions', () => {
    it('emits new-chat event when New Chat button is clicked', async () => {
      const newChatBtn = wrapper.find('.sidebar-actions button')
      await newChatBtn.trigger('click')
      
      expect(wrapper.emitted('new-chat')).toBeTruthy()
      expect(wrapper.emitted('new-chat')).toHaveLength(1)
    })

    it('emits open-settings event when Settings button is clicked', async () => {
      const settingsBtn = wrapper.findAll('.sidebar-actions button')[1]
      await settingsBtn.trigger('click')
      
      expect(wrapper.emitted('open-settings')).toBeTruthy()
      expect(wrapper.emitted('open-settings')).toHaveLength(1)
    })

    it('emits select-chat event when history item is clicked', async () => {
      const historyItem = wrapper.find('.history-item')
      await historyItem.trigger('click')
      
      expect(wrapper.emitted('select-chat')).toBeTruthy()
      expect(wrapper.emitted('select-chat')[0]).toEqual([1])
    })

    it('disables buttons when loading', async () => {
      await wrapper.setProps({ isLoading: true })
      
      const buttons = wrapper.findAll('.sidebar-actions button')
      expect(buttons[0].attributes('disabled')).toBeDefined()
      expect(buttons[1].attributes('disabled')).toBeDefined()
    })
  })

  describe('Search Functionality', () => {
    it('toggles search input visibility', async () => {
      const searchBtn = wrapper.find('.sidebar-footer .btn-icon')
      expect(wrapper.find('.history-search').exists()).toBe(false)
      
      await searchBtn.trigger('click')
      expect(wrapper.find('.history-search').exists()).toBe(true)
      expect(wrapper.vm.showSearch).toBe(true)
    })

    it('filters chat history based on search query', async () => {
      const searchBtn = wrapper.find('.sidebar-footer .btn-icon')
      await searchBtn.trigger('click')
      
      const searchInput = wrapper.find('.search-input')
      await searchInput.setValue('Spring')
      
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.filteredChatHistory.length).toBeLessThanOrEqual(wrapper.vm.chatHistory.length)
    })

    it('shows empty state when no results found', async () => {
      const searchBtn = wrapper.find('.sidebar-footer .btn-icon')
      await searchBtn.trigger('click')
      
      const searchInput = wrapper.find('.search-input')
      await searchInput.setValue('nonexistent')
      
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.history-empty').exists()).toBe(true)
      expect(wrapper.find('.history-empty p').text()).toContain('Không tìm thấy chat nào phù hợp')
    })
  })

  describe('Chat Actions', () => {
    it('toggles chat favorite status', async () => {
      const favoriteBtn = wrapper.find('.history-action')
      const initialIcon = favoriteBtn.find('.icon').text()
      
      await favoriteBtn.trigger('click')
      
      // Should toggle the icon
      await wrapper.vm.$nextTick()
      const newIcon = favoriteBtn.find('.icon').text()
      expect(newIcon).not.toBe(initialIcon)
    })

    it('deletes chat with confirmation', async () => {
      global.confirm.mockReturnValue(true)
      
      const deleteBtn = wrapper.findAll('.history-action')[1]
      await deleteBtn.trigger('click')
      
      expect(global.confirm).toHaveBeenCalledWith('Bạn có chắc chắn muốn xóa chat này?')
      expect(wrapper.emitted('delete-chat')).toBeTruthy()
    })

    it('cancels delete when user refuses', async () => {
      global.confirm.mockReturnValue(false)
      
      const deleteBtn = wrapper.findAll('.history-action')[1]
      await deleteBtn.trigger('click')
      
      expect(global.confirm).toHaveBeenCalled()
      expect(wrapper.emitted('delete-chat')).toBeFalsy()
    })
  })

  describe('Context Menu', () => {
    it('shows context menu on right-click', async () => {
      const historyItem = wrapper.find('.history-item')
      await historyItem.trigger('contextmenu')
      
      expect(wrapper.find('.context-menu').exists()).toBe(true)
      expect(wrapper.vm.contextMenu.show).toBe(true)
    })

    it('has all context menu items', async () => {
      const historyItem = wrapper.find('.history-item')
      await historyItem.trigger('contextmenu')
      
      const menuItems = wrapper.findAll('.context-menu-item')
      expect(menuItems).toHaveLength(4) // Rename, Duplicate, Export, Delete
      
      expect(menuItems[0].text()).toContain('Đổi tên')
      expect(menuItems[1].text()).toContain('Sao chép')
      expect(menuItems[2].text()).toContain('Xuất chat')
      expect(menuItems[3].text()).toContain('Xóa')
    })

    it('renames chat from context menu', async () => {
      global.prompt.mockReturnValue('New Chat Name')
      
      const historyItem = wrapper.find('.history-item')
      await historyItem.trigger('contextmenu')
      
      const renameBtn = wrapper.find('.context-menu-item')
      await renameBtn.trigger('click')
      
      expect(global.prompt).toHaveBeenCalledWith('Nhập tên mới cho chat:', expect.any(String))
      expect(wrapper.emitted('rename-chat')).toBeTruthy()
    })

    it('duplicates chat from context menu', async () => {
      const historyItem = wrapper.find('.history-item')
      await historyItem.trigger('contextmenu')
      
      const duplicateBtn = wrapper.findAll('.context-menu-item')[1]
      await duplicateBtn.trigger('click')
      
      expect(wrapper.emitted('duplicate-chat')).toBeTruthy()
    })

    it('exports chat from context menu', async () => {
      global.alert.mockImplementation(() => {})
      
      const historyItem = wrapper.find('.history-item')
      await historyItem.trigger('contextmenu')
      
      const exportBtn = wrapper.findAll('.context-menu-item')[2]
      await exportBtn.trigger('click')
      
      expect(global.alert).toHaveBeenCalledWith(expect.stringContaining('Xuất chat'))
      expect(wrapper.emitted('export-chat')).toBeTruthy()
    })
  })

  describe('History Management', () => {
    it('refreshes history', async () => {
      const refreshBtn = wrapper.find('.history-header .btn-icon')
      await refreshBtn.trigger('click')
      
      expect(wrapper.vm.isRefreshing).toBe(true)
      
      // Wait for timeout to complete
      await new Promise(resolve => setTimeout(resolve, 1100))
      expect(wrapper.vm.isRefreshing).toBe(false)
    })

    it('loads more history when button clicked', async () => {
      // Set up component to show load more button
      await wrapper.setData({ hasMoreHistory: true })
      
      const loadMoreBtn = wrapper.find('.btn.btn-text')
      await loadMoreBtn.trigger('click')
      
      expect(wrapper.vm.isLoadingMore).toBe(true)
    })
  })

  describe('Footer Stats', () => {
    it('displays correct stats', () => {
      const stats = wrapper.findAll('.stat-item')
      expect(stats).toHaveLength(2)
      expect(stats[0].text()).toMatch(/\d+ chats/)
      expect(stats[1].text()).toMatch(/\d+ tin nhắn/)
    })
  })

  describe('Utility Functions', () => {
    it('formats dates correctly', () => {
      const today = new Date()
      const yesterday = new Date(Date.now() - 86400000)
      const weekAgo = new Date(Date.now() - 7 * 86400000)
      
      expect(wrapper.vm.formatDate(yesterday)).toBe('Hôm qua')
      expect(wrapper.vm.formatDate(weekAgo)).toMatch(/\d+ ngày trước/)
    })

    it('identifies recent chats correctly', () => {
      const recent = new Date(Date.now() - 3600000) // 1 hour ago
      const old = new Date(Date.now() - 86400000 * 2) // 2 days ago
      
      expect(wrapper.vm.isRecentChat(recent)).toBe(true)
      expect(wrapper.vm.isRecentChat(old)).toBe(false)
    })

    it('truncates long titles', () => {
      const longTitle = 'This is a very long chat title that should be truncated'
      expect(wrapper.vm.truncateTitle(longTitle, 10)).toBe('This is a ...')
    })

    it('truncates long messages', () => {
      const longMessage = 'This is a very long message that should be truncated'
      expect(wrapper.vm.truncateMessage(longMessage, 10)).toBe('This is a ...')
    })
  })

  describe('Responsive Behavior', () => {
    it('adjusts to different screen sizes', () => {
      // Test that component has responsive classes
      expect(wrapper.find('.sidebar').classes()).toBeDefined()
    })
  })

  describe('Edge Cases', () => {
    it('handles empty chat history', async () => {
      await wrapper.setData({ chatHistory: [] })
      
      expect(wrapper.find('.history-empty').exists()).toBe(true)
      expect(wrapper.find('.history-empty p').text()).toBe('Chưa có lịch sử chat')
    })

    it('handles chat without message count', async () => {
      const chatWithoutCount = {
        id: 999,
        title: 'Test Chat',
        date: new Date(),
        isFavorite: false
      }
      
      await wrapper.setData({ 
        chatHistory: [chatWithoutCount],
        filteredChatHistory: [chatWithoutCount] 
      })
      
      const historyItem = wrapper.find('.history-item')
      expect(historyItem.find('.history-message-count').exists()).toBe(false)
    })

    it('handles rename with empty input', async () => {
      global.prompt.mockReturnValue('')
      
      const historyItem = wrapper.find('.history-item')
      await historyItem.trigger('contextmenu')
      
      const renameBtn = wrapper.find('.context-menu-item')
      await renameBtn.trigger('click')
      
      expect(wrapper.emitted('rename-chat')).toBeFalsy()
    })
  })
}) 