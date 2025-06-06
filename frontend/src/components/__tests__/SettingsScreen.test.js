import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SettingsScreen from '../SettingsScreen.vue'

// Mock console methods
global.confirm = vi.fn()
global.alert = vi.fn()

describe('SettingsScreen.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(SettingsScreen)
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  // === Component Structure Tests ===
  describe('Component Structure', () => {
    it('renders settings screen correctly', () => {
      expect(wrapper.find('.settings-screen').exists()).toBe(true)
      expect(wrapper.find('.settings-header').exists()).toBe(true)
      expect(wrapper.find('.settings-content').exists()).toBe(true)
      expect(wrapper.find('.settings-footer').exists()).toBe(true)
    })

    it('displays correct title and subtitle', () => {
      expect(wrapper.find('.settings-title').text()).toContain('Cài Đặt RepoChat')
      expect(wrapper.find('.settings-subtitle').text()).toContain('Cấu hình model LLM')
    })

    it('shows back button', () => {
      const backBtn = wrapper.find('.back-btn')
      expect(backBtn.exists()).toBe(true)
      expect(backBtn.text()).toContain('←')
    })
  })

  // === LLM Model Configuration Tests ===
  describe('LLM Model Configuration', () => {
    it('renders all three model dropdown selects', () => {
      const selects = wrapper.findAll('.model-select')
      expect(selects).toHaveLength(3)
      
      // Check specific model selects
      expect(wrapper.find('#nlu-model').exists()).toBe(true)
      expect(wrapper.find('#code-analysis-model').exists()).toBe(true)
      expect(wrapper.find('#report-model').exists()).toBe(true)
    })

    it('displays correct default model selections', () => {
      expect(wrapper.vm.settings.nluModel).toBe('gpt-4o-mini')
      expect(wrapper.vm.settings.codeAnalysisModel).toBe('gpt-4-turbo')
      expect(wrapper.vm.settings.reportGenerationModel).toBe('gpt-4o-mini')
    })

    it('renders all available models in dropdown options', () => {
      const nluSelect = wrapper.find('#nlu-model')
      const options = nluSelect.findAll('option')
      
      expect(options).toHaveLength(5) // Based on availableModels array
      
      // Check that key models are available
      const optionTexts = options.map(opt => opt.text())
      expect(optionTexts).toContain('GPT-4O Mini')
      expect(optionTexts).toContain('GPT-4 Turbo')
      expect(optionTexts).toContain('Claude 3 Haiku')
    })

    it('displays model info (provider and cost) correctly', () => {
      const modelInfos = wrapper.findAll('.model-info')
      expect(modelInfos.length).toBeGreaterThan(0)
      
      // Check first model info
      const firstInfo = modelInfos[0]
      expect(firstInfo.find('.model-provider').exists()).toBe(true)
      expect(firstInfo.find('.model-cost').exists()).toBe(true)
    })
  })

  // === Model Selection Tests ===
  describe('Model Selection Functionality', () => {
    it('updates model selection when dropdown value changes', async () => {
      const nluSelect = wrapper.find('#nlu-model')
      
      await nluSelect.setValue('gpt-4')
      expect(wrapper.vm.settings.nluModel).toBe('gpt-4')
    })

    it('marks as modified when model selection changes', async () => {
      expect(wrapper.vm.hasModifications).toBe(false)
      
      const codeAnalysisSelect = wrapper.find('#code-analysis-model')
      await codeAnalysisSelect.setValue('claude-3-sonnet')
      
      expect(wrapper.vm.hasModifications).toBe(true)
    })

    it('updates model info display when selection changes', async () => {
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('claude-3-haiku')
      
      // Should update to show Anthropic provider
      const modelInfo = wrapper.find('.model-info .model-provider')
      expect(modelInfo.text()).toBe('Anthropic')
    })
  })

  // === Settings Actions Tests ===
  describe('Settings Actions', () => {
    it('emits go-back event when back button is clicked', async () => {
      const backBtn = wrapper.find('.back-btn')
      await backBtn.trigger('click')
      
      expect(wrapper.emitted('go-back')).toBeTruthy()
      expect(wrapper.emitted('go-back')).toHaveLength(1)
    })

    it('shows confirmation when going back with modifications', async () => {
      global.confirm.mockReturnValue(false)
      
      // Make a modification
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const backBtn = wrapper.find('.back-btn')
      await backBtn.trigger('click')
      
      expect(global.confirm).toHaveBeenCalledWith('Bạn có thay đổi chưa lưu. Bạn có chắc muốn thoát?')
      expect(wrapper.emitted('go-back')).toBeFalsy()
    })

    it('allows going back when modifications are confirmed', async () => {
      global.confirm.mockReturnValue(true)
      
      // Make a modification
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const backBtn = wrapper.find('.back-btn')
      await backBtn.trigger('click')
      
      expect(wrapper.emitted('go-back')).toBeTruthy()
    })
  })

  // === Save Settings Tests ===
  describe('Save Settings Functionality', () => {
    it('renders save button correctly', () => {
      const saveBtn = wrapper.find('.save-btn')
      expect(saveBtn.exists()).toBe(true)
      expect(saveBtn.text()).toContain('Lưu cài đặt')
    })

    it('disables save button when no modifications', () => {
      const saveBtn = wrapper.find('.save-btn')
      expect(saveBtn.attributes('disabled')).toBeDefined()
    })

    it('enables save button when there are modifications', async () => {
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const saveBtn = wrapper.find('.save-btn')
      expect(saveBtn.attributes('disabled')).toBeUndefined()
    })

    it('triggers save process when save button is clicked', async () => {
      // Make a modification to enable save button
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const saveBtn = wrapper.find('.save-btn')
      await saveBtn.trigger('click')
      
      expect(wrapper.vm.isSaving).toBe(true)
    })

    it('logs settings to console when saving (DoD requirement)', async () => {
      const consoleSpy = vi.spyOn(console, 'log')
      const consoleTableSpy = vi.spyOn(console, 'table')
      
      // Make modifications
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const saveBtn = wrapper.find('.save-btn')
      await saveBtn.trigger('click')
      
      // Wait for save process to complete
      await new Promise(resolve => setTimeout(resolve, 1600))
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('🎯 RepoChat LLM Configuration Saved:'),
        expect.any(Object)
      )
      expect(consoleTableSpy).toHaveBeenCalled()
      
      consoleSpy.mockRestore()
      consoleTableSpy.mockRestore()
    })

    it('emits settings-saved event after successful save', async () => {
      // Make a modification
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const saveBtn = wrapper.find('.save-btn')
      await saveBtn.trigger('click')
      
      // Wait for save process
      await new Promise(resolve => setTimeout(resolve, 1600))
      
      expect(wrapper.emitted('settings-saved')).toBeTruthy()
      expect(wrapper.emitted('settings-saved')[0]).toEqual([
        expect.objectContaining({
          llmModels: expect.objectContaining({
            nlu: 'gpt-4'
          })
        })
      ])
    })

    it('shows success toast after saving', async () => {
      // Make a modification
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const saveBtn = wrapper.find('.save-btn')
      await saveBtn.trigger('click')
      
      // Wait for save process
      await new Promise(resolve => setTimeout(resolve, 1600))
      
      expect(wrapper.find('.toast-success').exists()).toBe(true)
      expect(wrapper.find('.toast-message').text()).toContain('thành công')
    })

    it('updates save status after successful save', async () => {
      // Make a modification
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const saveBtn = wrapper.find('.save-btn')
      await saveBtn.trigger('click')
      
      // Wait for save process
      await new Promise(resolve => setTimeout(resolve, 1600))
      
      expect(wrapper.vm.hasModifications).toBe(false)
      expect(wrapper.vm.lastSavedTime).toBeTruthy()
    })
  })

  // === Reset and Discard Tests ===
  describe('Reset and Discard Functionality', () => {
    it('renders reset to defaults button', () => {
      const resetBtn = wrapper.find('button:contains("Mặc định")')
      expect(resetBtn.exists()).toBe(true)
    })

    it('resets settings to defaults when confirmed', async () => {
      global.confirm.mockReturnValue(true)
      
      // Make some modifications
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const resetBtn = wrapper.find('button').filter(btn => 
        btn.text().includes('Mặc định')
      )[0]
      await resetBtn.trigger('click')
      
      expect(wrapper.vm.settings.nluModel).toBe('gpt-4o-mini')
      expect(wrapper.vm.hasModifications).toBe(true) // Should mark as modified
    })

    it('renders discard changes button', () => {
      const discardBtn = wrapper.find('button:contains("Hủy thay đổi")')
      expect(discardBtn.exists()).toBe(true)
    })

    it('discards changes when confirmed', async () => {
      global.confirm.mockReturnValue(true)
      
      // Make a modification
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      expect(wrapper.vm.hasModifications).toBe(true)
      
      const discardBtn = wrapper.find('button').filter(btn => 
        btn.text().includes('Hủy thay đổi')
      )[0]
      await discardBtn.trigger('click')
      
      expect(wrapper.vm.settings.nluModel).toBe('gpt-4o-mini')
      expect(wrapper.vm.hasModifications).toBe(false)
    })
  })

  // === Status Display Tests ===
  describe('Status Display', () => {
    it('shows correct save status when no modifications', () => {
      const saveStatus = wrapper.find('.save-status')
      expect(saveStatus.text()).toContain('Đã lưu')
      expect(saveStatus.classes()).not.toContain('has-changes')
    })

    it('shows correct save status when there are modifications', async () => {
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const saveStatus = wrapper.find('.save-status')
      expect(saveStatus.text()).toContain('Có thay đổi chưa lưu')
      expect(saveStatus.classes()).toContain('has-changes')
    })

    it('displays last saved time when available', async () => {
      wrapper.vm.lastSavedTime = new Date()
      await wrapper.vm.$nextTick()
      
      const lastSaved = wrapper.find('.last-saved')
      expect(lastSaved.exists()).toBe(true)
      expect(lastSaved.text()).toContain('Lần cuối lưu:')
    })
  })

  // === Utility Functions Tests ===
  describe('Utility Functions', () => {
    it('getModelInfo returns correct model information', () => {
      const modelInfo = wrapper.vm.getModelInfo('gpt-4-turbo')
      expect(modelInfo.name).toBe('GPT-4 Turbo')
      expect(modelInfo.provider).toBe('OpenAI')
      expect(modelInfo.cost).toBe('Trung bình')
    })

    it('getModelInfo returns fallback for unknown model', () => {
      const modelInfo = wrapper.vm.getModelInfo('unknown-model')
      expect(modelInfo).toBe(wrapper.vm.availableModels[0])
    })

    it('formatTime returns correctly formatted time', () => {
      const testDate = new Date('2024-01-01T10:30:00')
      const formatted = wrapper.vm.formatTime(testDate)
      expect(formatted).toMatch(/^\d{2}:\d{2}$/)
    })
  })

  // === Persistence Tests ===
  describe('Settings Persistence', () => {
    it('loads settings from localStorage on mount', () => {
      const mockSettings = {
        nluModel: 'gpt-4',
        codeAnalysisModel: 'claude-3-sonnet',
        reportGenerationModel: 'gpt-4-turbo'
      }
      
      // Mock localStorage
      const getItemSpy = vi.spyOn(Storage.prototype, 'getItem')
      getItemSpy.mockReturnValue(JSON.stringify(mockSettings))
      
      const newWrapper = mount(SettingsScreen)
      
      expect(newWrapper.vm.settings.nluModel).toBe('gpt-4')
      expect(newWrapper.vm.settings.codeAnalysisModel).toBe('claude-3-sonnet')
      
      getItemSpy.mockRestore()
      newWrapper.unmount()
    })

    it('saves settings to localStorage after successful save', async () => {
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
      
      // Make a modification
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const saveBtn = wrapper.find('.save-btn')
      await saveBtn.trigger('click')
      
      // Wait for save process
      await new Promise(resolve => setTimeout(resolve, 1600))
      
      expect(setItemSpy).toHaveBeenCalledWith(
        'repochat_settings',
        expect.stringContaining('gpt-4')
      )
      
      setItemSpy.mockRestore()
    })
  })

  // === Edge Cases Tests ===
  describe('Edge Cases', () => {
    it('handles localStorage errors gracefully', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const getItemSpy = vi.spyOn(Storage.prototype, 'getItem')
      getItemSpy.mockImplementation(() => {
        throw new Error('LocalStorage error')
      })
      
      const newWrapper = mount(SettingsScreen)
      
      expect(consoleSpy).toHaveBeenCalled()
      expect(newWrapper.vm.settings.nluModel).toBe('gpt-4o-mini') // Should use defaults
      
      consoleSpy.mockRestore()
      getItemSpy.mockRestore()
      newWrapper.unmount()
    })

    it('disables controls during saving', async () => {
      // Make a modification
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const saveBtn = wrapper.find('.save-btn')
      await saveBtn.trigger('click')
      
      // During save process, controls should be disabled
      expect(wrapper.find('#nlu-model').attributes('disabled')).toBeDefined()
      expect(wrapper.find('#code-analysis-model').attributes('disabled')).toBeDefined()
      expect(wrapper.find('#report-model').attributes('disabled')).toBeDefined()
    })

    it('shows saving state in save button', async () => {
      // Make a modification
      const nluSelect = wrapper.find('#nlu-model')
      await nluSelect.setValue('gpt-4')
      
      const saveBtn = wrapper.find('.save-btn')
      await saveBtn.trigger('click')
      
      expect(saveBtn.text()).toContain('Đang lưu')
      expect(saveBtn.classes()).toContain('saving')
    })
  })

  // === Responsive Design Tests ===
  describe('Responsive Design', () => {
    it('applies correct CSS classes for responsive layout', () => {
      expect(wrapper.find('.settings-grid').exists()).toBe(true)
      expect(wrapper.find('.setting-item').exists()).toBe(true)
      expect(wrapper.find('.setting-control').exists()).toBe(true)
    })

    it('maintains proper structure for mobile layouts', () => {
      // Test grid layout structure
      const settingItems = wrapper.findAll('.setting-item')
      expect(settingItems.length).toBeGreaterThan(0)
      
      settingItems.forEach(item => {
        expect(item.find('.setting-info').exists()).toBe(true)
        expect(item.find('.setting-control').exists()).toBe(true)
      })
    })
  })
}) 