<template>
  <div class="settings-screen">
    <!-- Settings Header -->
    <header class="settings-header">
      <div class="header-content">
        <button 
          class="btn btn-icon back-btn"
          @click="handleGoBack"
          title="Quay lại"
        >
          <span class="icon">←</span>
        </button>
        
        <div class="header-text">
          <h1 class="settings-title">⚙️ Cài Đặt RepoChat</h1>
          <p class="settings-subtitle">Cấu hình model LLM cho các chức năng khác nhau</p>
        </div>
        
        <div class="header-actions">
          <button 
            class="btn btn-secondary"
            @click="resetToDefaults"
            :disabled="loading"
          >
            <span class="icon">🔄</span>
            Mặc định
          </button>
        </div>
      </div>
    </header>

    <!-- Loading Banner -->
    <div v-if="loading" class="loading-banner">
      <span class="icon">⏳</span>
      <span>Đang tải cài đặt...</span>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      <span class="icon">❌</span>
      <span>{{ error }}</span>
      <button @click="clearError" class="btn-link">Đóng</button>
    </div>

    <!-- Settings Content -->
    <main class="settings-content">
      <div class="settings-container">
        
        <!-- Settings Tabs -->
        <div class="settings-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="['tab-button', { active: activeTab === tab.id }]"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>

        <!-- API Keys Tab -->
        <section v-if="activeTab === 'api-keys'" class="settings-section">
          <div class="section-header">
            <h2 class="section-title">🔑 API Keys Management</h2>
            <p class="section-description">
              Quản lý API keys cho các nhà cung cấp AI. Dữ liệu được mã hóa và bảo mật.
            </p>
          </div>

          <!-- Add New API Key -->
          <div class="api-key-form">
            <h3 class="form-title">Thêm API Key mới</h3>
            <div class="form-grid">
              <div class="form-group">
                <label for="provider-select">Nhà cung cấp</label>
                <select 
                  id="provider-select"
                  v-model="newApiKey.provider"
                  class="form-input"
                >
                  <option value="">Chọn nhà cung cấp</option>
                  <option v-for="provider in availableProviders" :key="provider.provider" :value="provider.provider">
                    {{ provider.name }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="api-key-input">API Key</label>
                <input 
                  id="api-key-input"
                  v-model="newApiKey.api_key"
                  type="password"
                  class="form-input"
                  placeholder="Nhập API key..."
                />
              </div>
              
              <div class="form-group">
                <label for="nickname-input">Tên gọi (tùy chọn)</label>
                <input 
                  id="nickname-input"
                  v-model="newApiKey.nickname"
                  type="text"
                  class="form-input"
                  placeholder="VD: My OpenAI Key"
                />
              </div>
            </div>
            
            <div class="form-actions">
              <button 
                @click="addApiKey"
                :disabled="!newApiKey.provider || !newApiKey.api_key || loading"
                class="btn btn-primary"
              >
                <span class="icon">➕</span>
                {{ loading ? 'Đang thêm...' : 'Thêm API Key' }}
              </button>
              
              <button 
                @click="clearApiKeyForm"
                class="btn btn-secondary"
              >
                <span class="icon">❌</span>
                Hủy
              </button>
            </div>
          </div>

          <!-- Current API Keys -->
          <div class="api-keys-list">
            <h3 class="list-title">API Keys hiện tại</h3>
            
            <div v-if="userApiKeys.length === 0" class="empty-state">
              <span class="empty-icon">🔑</span>
              <p class="empty-text">Chưa có API key nào được cấu hình</p>
              <p class="empty-description">Thêm API key để sử dụng các model AI khác nhau</p>
            </div>
            
            <div v-else class="api-key-items">
              <div 
                v-for="apiKey in userApiKeys" 
                :key="apiKey.provider"
                class="api-key-item"
              >
                <div class="api-key-info">
                  <div class="api-key-icon">
                    <span>🤖</span>
                  </div>
                  <div class="api-key-details">
                    <h4 class="api-key-name">
                      {{ getProviderName(apiKey.provider) }}
                      <span v-if="apiKey.nickname" class="api-key-nickname">({{ apiKey.nickname }})</span>
                    </h4>
                    <p class="api-key-meta">
                      Thêm vào: {{ formatDate(apiKey.created_at) }}
                      <span v-if="apiKey.last_used" class="last-used">
                        • Sử dụng lần cuối: {{ formatDate(apiKey.last_used) }}
                      </span>
                    </p>
                  </div>
                </div>
                
                <div class="api-key-actions">
                  <span 
                    :class="['status-badge', apiKey.is_valid ? 'valid' : 'invalid']"
                  >
                    {{ apiKey.is_valid ? 'Hoạt động' : 'Lỗi' }}
                  </span>
                  
                  <button 
                    @click="testApiKey(apiKey.provider)"
                    class="btn btn-sm btn-outline"
                  >
                    <span class="icon">🧪</span>
                    Test
                  </button>
                  
                  <button 
                    @click="removeApiKey(apiKey.provider)"
                    class="btn btn-sm btn-danger"
                  >
                    <span class="icon">🗑️</span>
                    Xóa
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        <!-- LLM Configuration Section -->
        <section v-if="activeTab === 'llm-models'" class="settings-section">
          <div class="section-header">
            <h2 class="section-title">🤖 Cấu Hình Model LLM</h2>
            <p class="section-description">
              Chọn model LLM phù hợp cho từng chức năng của RepoChat. 
              Các model khác nhau có thể tối ưu cho các tác vụ cụ thể.
            </p>
          </div>

          <div class="settings-grid">
            
            <!-- NLU Model -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label" for="nlu-model">
                  🧠 Natural Language Understanding
                </label>
                <p class="setting-description">
                  Model để hiểu và phân tích yêu cầu của người dùng
                </p>
                <div class="setting-meta">
                  <span class="setting-team">TEAM: Interaction & Tasking</span>
                  <span class="setting-usage">Sử dụng: Phân tích câu hỏi, tạo task definitions</span>
                </div>
              </div>
              <div class="setting-control">
                <select 
                  id="nlu-model"
                  v-model="settings.nluModel"
                  class="model-select"
                  :disabled="loading"
                  @change="markAsModified"
                >
                  <option 
                    v-for="model in availableModels" 
                    :key="model.id"
                    :value="model.id"
                  >
                    {{ model.name }}
                  </option>
                </select>
                <div class="model-info">
                  <span class="model-provider">{{ getModelInfo(settings.nluModel).provider }}</span>
                  <span class="model-cost">{{ getModelInfo(settings.nluModel).cost }}</span>
                </div>
              </div>
            </div>

            <!-- Code Analysis Model -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label" for="code-analysis-model">
                  📄 Code Analysis
                </label>
                <p class="setting-description">
                  Model để phân tích code, tìm kiếm dependencies và review
                </p>
                <div class="setting-meta">
                  <span class="setting-team">TEAM: Code Analysis</span>
                  <span class="setting-usage">Sử dụng: Static analysis, code review, dependency check</span>
                </div>
              </div>
              <div class="setting-control">
                <select 
                  id="code-analysis-model"
                  v-model="settings.codeAnalysisModel"
                  class="model-select"
                  :disabled="loading"
                  @change="markAsModified"
                >
                  <option 
                    v-for="model in availableModels" 
                    :key="model.id"
                    :value="model.id"
                  >
                    {{ model.name }}
                  </option>
                </select>
                <div class="model-info">
                  <span class="model-provider">{{ getModelInfo(settings.codeAnalysisModel).provider }}</span>
                  <span class="model-cost">{{ getModelInfo(settings.codeAnalysisModel).cost }}</span>
                </div>
              </div>
            </div>

            <!-- Report Generation Model -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label" for="report-model">
                  📊 Report Generation  
                </label>
                <p class="setting-description">
                  Model để tạo báo cáo tổng hợp và synthesis
                </p>
                <div class="setting-meta">
                  <span class="setting-team">TEAM: Synthesis & Reporting</span>
                  <span class="setting-usage">Sử dụng: Tạo final reports, summary, recommendations</span>
                </div>
              </div>
              <div class="setting-control">
                <select 
                  id="report-model"
                  v-model="settings.reportGenerationModel"
                  class="model-select"
                  :disabled="loading"
                  @change="markAsModified"
                >
                  <option 
                    v-for="model in availableModels" 
                    :key="model.id"
                    :value="model.id"
                  >
                    {{ model.name }}
                  </option>
                </select>
                <div class="model-info">
                  <span class="model-provider">{{ getModelInfo(settings.reportGenerationModel).provider }}</span>
                  <span class="model-cost">{{ getModelInfo(settings.reportGenerationModel).cost }}</span>
                </div>
              </div>
            </div>

            <!-- Theme Setting -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label" for="theme-select">
                  🎨 Giao Diện
                </label>
                <p class="setting-description">
                  Chọn theme cho giao diện ứng dụng
                </p>
                <div class="setting-meta">
                  <span class="setting-team">TEAM: Frontend</span>
                  <span class="setting-usage">Sử dụng: Màu sắc và hiển thị giao diện</span>
                </div>
              </div>
              <div class="setting-control">
                <select 
                  id="theme-select"
                  v-model="settings.theme"
                  class="model-select"
                  :disabled="loading"
                  @change="markAsModified"
                >
                  <option value="dark">Tối (Dark)</option>
                  <option value="light">Sáng (Light)</option>
                  <option value="auto">Tự động (Auto)</option>
                </select>
                <div class="model-info">
                  <span class="model-provider">Giao diện</span>
                  <span class="model-cost">Miễn phí</span>
                </div>
              </div>
            </div>

            <!-- Language Setting -->
            <div class="setting-item">
              <div class="setting-info">
                <label class="setting-label" for="language-select">
                  🌐 Ngôn Ngữ
                </label>
                <p class="setting-description">
                  Chọn ngôn ngữ hiển thị cho ứng dụng
                </p>
                <div class="setting-meta">
                  <span class="setting-team">TEAM: Frontend</span>
                  <span class="setting-usage">Sử dụng: Hiển thị text và messages</span>
                </div>
              </div>
              <div class="setting-control">
                <select 
                  id="language-select"
                  v-model="settings.language"
                  class="model-select"
                  :disabled="loading"
                  @change="markAsModified"
                >
                  <option value="vi">Tiếng Việt</option>
                  <option value="en">English</option>
                </select>
                <div class="model-info">
                  <span class="model-provider">Bản địa hóa</span>
                  <span class="model-cost">Miễn phí</span>
                </div>
              </div>
            </div>

          </div>
        </section>

      </div>
    </main>

    <!-- Settings Footer -->
    <footer class="settings-footer">
      <div class="footer-content">
        <div class="footer-info">
          <span class="save-status" :class="{ 'has-changes': hasModifications }">
            {{ hasModifications ? '⚠️ Có thay đổi chưa lưu' : '✅ Đã lưu' }}
          </span>
          <span class="last-saved" v-if="lastSavedTime">
            Lần cuối lưu: {{ formatTime(lastSavedTime) }}
          </span>
        </div>
        
        <div class="footer-actions">
          <button 
            class="btn btn-secondary"
            @click="discardChanges"
            :disabled="!hasModifications || loading"
          >
            <span class="icon">↶</span>
            Hủy thay đổi
          </button>
          
          <button 
            class="btn btn-primary save-btn"
            @click="saveSettings"
            :disabled="!hasModifications || loading"
            :class="{ 'saving': loading }"
          >
            <span class="icon">{{ loading ? '⏳' : '💾' }}</span>
            {{ loading ? 'Đang lưu...' : 'Lưu cài đặt' }}
          </button>
        </div>
      </div>
    </footer>

    <!-- Success Toast -->
    <div v-if="showSuccessToast" class="success-toast animate-slide-in-right">
      <span class="icon">✅</span>
      <span>Cài đặt đã được lưu thành công!</span>
    </div>

  </div>
</template>

<script>
import { useSettings } from '../composables/useApi.js'
import { ref, computed, onMounted, watch, nextTick } from 'vue'

export default {
  name: 'SettingsScreen',
  
  emits: ['go-back', 'settings-saved'],

  setup(props, { emit }) {
    // Settings API
    const {
      loading,
      error,
      settings,
      loadSettings,
      saveSettings: saveToDatabase,
      clearError
    } = useSettings()

    // Local state for tracking modifications
    const originalSettings = ref({})
    const hasModifications = ref(false)
    const lastSavedTime = ref(null)
    const showSuccessToast = ref(false)

    // Tabs state
    const activeTab = ref('api-keys')
    const tabs = ref([
      { id: 'api-keys', icon: '🔑', label: 'API Keys' },
      { id: 'llm-models', icon: '🤖', label: 'LLM Models' },
      { id: 'preferences', icon: '⚙️', label: 'Preferences' }
    ])

    // API Keys state
    const userId = ref('user123') // TODO: Get from auth
    const availableProviders = ref([])
    const userApiKeys = ref([])
    const newApiKey = ref({
      provider: '',
      api_key: '',
      nickname: ''
    })

    // Available LLM models
    const availableModels = ref([
      {
        id: 'gpt-4',
        name: 'GPT-4 (OpenAI)',
        provider: 'OpenAI',
        cost: '$0.03/1K tokens'
      },
      {
        id: 'gpt-3.5-turbo',
        name: 'GPT-3.5 Turbo (OpenAI)',
        provider: 'OpenAI',
        cost: '$0.002/1K tokens'
      },
      {
        id: 'claude-3-opus',
        name: 'Claude 3 Opus (Anthropic)',
        provider: 'Anthropic',
        cost: '$15/1M tokens'
      },
      {
        id: 'claude-3-sonnet',
        name: 'Claude 3 Sonnet (Anthropic)',
        provider: 'Anthropic',
        cost: '$3/1M tokens'
      },
      {
        id: 'gemini-pro',
        name: 'Gemini Pro (Google)',
        provider: 'Google',
        cost: '$0.5/1M tokens'
      },
      {
        id: 'ollama-llama2',
        name: 'Llama 2 (Local)',
        provider: 'Ollama',
        cost: 'Miễn phí'
      }
    ])

    // Computed
    const getModelInfo = (modelId) => {
      const model = availableModels.value.find(m => m.id === modelId)
      return model || { provider: 'Unknown', cost: 'N/A' }
    }

    // Methods
    const markAsModified = () => {
      hasModifications.value = true
    }

    const handleGoBack = () => {
      if (hasModifications.value) {
        const confirmLeave = confirm('Bạn có thay đổi chưa lưu. Bạn có chắc muốn rời khỏi trang này?')
        if (!confirmLeave) return
      }
      
      emit('go-back')
    }

    const resetToDefaults = async () => {
      const confirmReset = confirm('Bạn có chắc muốn khôi phục về cài đặt mặc định?')
      if (!confirmReset) return

      // Reset to default values
      settings.nluModel = 'gpt-3.5-turbo'
      settings.codeAnalysisModel = 'gpt-4'
      settings.reportGenerationModel = 'gpt-3.5-turbo'
      settings.theme = 'dark'
      settings.language = 'vi'
      
      markAsModified()
    }

    const discardChanges = async () => {
      const confirmDiscard = confirm('Bạn có chắc muốn hủy tất cả thay đổi?')
      if (!confirmDiscard) return

      // Reload settings from server
      await loadSettings()
      hasModifications.value = false
    }

    const saveSettings = async () => {
      try {
        const result = await saveToDatabase(settings)
        
        if (result) {
          hasModifications.value = false
          lastSavedTime.value = new Date()
          
          // Show success toast
          showSuccessToast.value = true
          setTimeout(() => {
            showSuccessToast.value = false
          }, 3000)
          
          // Emit event
          emit('settings-saved', settings)
          
          console.log('Settings saved successfully:', result)
        }
      } catch (err) {
        console.error('Failed to save settings:', err)
        // Error message sẽ được hiển thị qua error banner
      }
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      
      const now = new Date()
      const time = new Date(timestamp)
      const diffMs = now - time
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)

      if (diffMins < 1) return 'vừa xong'
      if (diffMins < 60) return `${diffMins} phút trước`
      if (diffHours < 24) return `${diffHours} giờ trước`
      
      return time.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // Watch for settings changes to track modifications
    watch(() => ({ ...settings }), (newSettings, oldSettings) => {
      if (oldSettings && Object.keys(oldSettings).length > 0) {
        const hasChanged = Object.keys(newSettings).some(key => 
          newSettings[key] !== originalSettings.value[key]
        )
        hasModifications.value = hasChanged
      }
    }, { deep: true })

    // API Keys methods
    const loadAvailableProviders = async () => {
      try {
        const response = await fetch('http://localhost:8000/api-providers')
        const data = await response.json()
        availableProviders.value = data.providers
      } catch (err) {
        console.error('Error loading providers:', err)
      }
    }

    const loadUserApiKeys = async () => {
      try {
        const response = await fetch(`http://localhost:8000/users/${userId.value}/api-keys`)
        const data = await response.json()
        userApiKeys.value = data.api_keys
      } catch (err) {
        console.error('Error loading API keys:', err)
      }
    }

    const addApiKey = async () => {
      if (!newApiKey.value.provider || !newApiKey.value.api_key) {
        alert('Vui lòng điền đầy đủ thông tin')
        return
      }

      try {
        const response = await fetch(`http://localhost:8000/users/${userId.value}/api-keys`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newApiKey.value)
        })

        if (response.ok) {
          showSuccessToast.value = true
          setTimeout(() => { showSuccessToast.value = false }, 3000)
          
          clearApiKeyForm()
          await loadUserApiKeys()
        } else {
          alert('Lỗi khi thêm API key')
        }
      } catch (err) {
        console.error('Error adding API key:', err)
        alert('Lỗi khi thêm API key')
      }
    }

    const removeApiKey = async (provider) => {
      if (!confirm('Bạn có chắc muốn xóa API key này?')) return

      try {
        const response = await fetch(`http://localhost:8000/users/${userId.value}/api-keys/${provider}`, {
          method: 'DELETE'
        })

        if (response.ok) {
          showSuccessToast.value = true
          setTimeout(() => { showSuccessToast.value = false }, 3000)
          
          await loadUserApiKeys()
        } else {
          alert('Lỗi khi xóa API key')
        }
      } catch (err) {
        console.error('Error removing API key:', err)
        alert('Lỗi khi xóa API key')
      }
    }

    const testApiKey = async (provider) => {
      try {
        const response = await fetch(`http://localhost:8000/users/${userId.value}/api-keys/${provider}/test`)
        const data = await response.json()
        
        if (data.is_valid) {
          alert(`API key ${provider} hoạt động tốt`)
        } else {
          alert(`API key ${provider} có lỗi: ${data.error_message}`)
        }
      } catch (err) {
        console.error('Error testing API key:', err)
        alert('Lỗi khi test API key')
      }
    }

    const clearApiKeyForm = () => {
      newApiKey.value = {
        provider: '',
        api_key: '',
        nickname: ''
      }
    }

    const getProviderName = (provider) => {
      const found = availableProviders.value.find(p => p.provider === provider)
      return found ? found.name : provider
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('vi-VN')
    }

    // Lifecycle
    onMounted(async () => {
      try {
        await Promise.all([
          loadSettings(),
          loadAvailableProviders(),
          loadUserApiKeys()
        ])
        
        // Store original settings for comparison
        originalSettings.value = { ...settings }
        hasModifications.value = false
      } catch (err) {
        console.error('Failed to load settings:', err)
        // Error sẽ được hiển thị qua error banner
      }
    })

    return {
      // API state
      loading,
      error,
      settings,
      clearError,
      
      // Local state
      hasModifications,
      lastSavedTime,
      showSuccessToast,
      availableModels,
      
      // Tabs state
      activeTab,
      tabs,
      
      // API Keys state
      userId,
      availableProviders,
      userApiKeys,
      newApiKey,
      
      // Computed
      getModelInfo,
      
      // Methods
      markAsModified,
      handleGoBack,
      resetToDefaults,
      discardChanges,
      saveSettings,
      formatTime,
      
      // API Keys methods
      loadAvailableProviders,
      loadUserApiKeys,
      addApiKey,
      removeApiKey,
      testApiKey,
      clearApiKeyForm,
      getProviderName,
      formatDate
    }
  }
}
</script>

<style scoped>
/* Loading Banner */
.loading-banner {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: rgba(102, 126, 234, 0.1);
  border-left: 4px solid var(--color-primary);
  color: var(--color-text-primary);
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background: rgba(255, 0, 0, 0.1);
  border-left: 4px solid red;
  color: var(--color-text-primary);
}

/* Button Link */
.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  text-decoration: underline;
  cursor: pointer;
  font-size: inherit;
}

.btn-link:hover {
  color: var(--color-primary-hover);
}

/* Success Toast */
.success-toast {
  position: fixed;
  top: var(--space-4);
  right: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  z-index: 1000;
  box-shadow: var(--shadow-lg);
}

/* Settings Tabs */
.settings-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: var(--font-size-sm);
}

.tab-button:hover {
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.tab-button.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-icon {
  font-size: 1.2em;
}

/* API Key Form */
.api-key-form {
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--border-radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-6);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.form-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--space-3) 0;
  color: var(--color-text-primary);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.form-group label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.form-input {
  padding: var(--space-2) var(--space-3);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--border-radius-sm);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  transition: border-color 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-actions {
  display: flex;
  gap: var(--space-2);
}

/* API Keys List */
.api-keys-list {
  margin-top: var(--space-4);
}

.list-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--space-3) 0;
  color: var(--color-text-primary);
}

.empty-state {
  text-align: center;
  padding: var(--space-8) var(--space-4);
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 3em;
  display: block;
  margin-bottom: var(--space-2);
}

.empty-text {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  margin: 0 0 var(--space-1) 0;
  color: var(--color-text-primary);
}

.empty-description {
  font-size: var(--font-size-sm);
  margin: 0;
}

.api-key-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.api-key-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--border-radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.api-key-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.api-key-icon {
  width: 40px;
  height: 40px;
  background: rgba(102, 126, 234, 0.2);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2em;
}

.api-key-details {
  flex: 1;
}

.api-key-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  margin: 0 0 var(--space-1) 0;
  color: var(--color-text-primary);
}

.api-key-nickname {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  color: var(--color-text-secondary);
}

.api-key-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin: 0;
}

.last-used {
  margin-left: var(--space-2);
}

.api-key-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-badge {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.valid {
  background: rgba(34, 197, 94, 0.2);
  color: rgb(34, 197, 94);
}

.status-badge.invalid {
  background: rgba(239, 68, 68, 0.2);
  color: rgb(239, 68, 68);
}

.btn-sm {
  padding: var(--space-1) var(--space-2);
  font-size: var(--font-size-xs);
}

.btn-outline {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--color-text-primary);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: rgb(239, 68, 68);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.3);
}

/* Existing styles would remain the same */
.settings-screen {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
  color: var(--color-text-primary);
}

.settings-header {
  flex-shrink: 0;
  padding: var(--space-4) var(--space-6);
  background: var(--color-surface);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  max-width: 1200px;
  margin: 0 auto;
}

.back-btn {
  padding: var(--space-2);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(-2px);
}

.header-text {
  flex: 1;
}

.settings-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  margin: 0 0 var(--space-1) 0;
  color: var(--color-text-primary);
}

.settings-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-2);
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.settings-container {
  max-width: 1200px;
  margin: 0 auto;
}

.settings-section {
  background: var(--color-surface);
  border-radius: var(--border-radius-lg);
  padding: var(--space-6);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-header {
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--space-2) 0;
  color: var(--color-text-primary);
}

.section-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

.settings-grid {
  display: grid;
  gap: var(--space-6);
}

.setting-item {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-4);
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--border-radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.setting-info {
  flex: 1;
}

.setting-label {
  display: block;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-2);
  color: var(--color-text-primary);
}

.setting-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: var(--space-3);
}

.setting-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.setting-team, .setting-usage {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.setting-control {
  flex-shrink: 0;
  width: 280px;
}

.model-select {
  width: 100%;
  padding: var(--space-3);
  background: var(--color-background);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--border-radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.model-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.model-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.model-info {
  display: flex;
  justify-content: space-between;
  margin-top: var(--space-2);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.settings-footer {
  flex-shrink: 0;
  padding: var(--space-4) var(--space-6);
  background: var(--color-surface);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
}

.footer-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.save-status {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.save-status.has-changes {
  color: orange;
}

.last-saved {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.footer-actions {
  display: flex;
  gap: var(--space-3);
}

.save-btn.saving {
  opacity: 0.8;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .settings-content {
    padding: var(--space-4);
  }
  
  .settings-section {
    padding: var(--space-4);
  }
  
  .setting-item {
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .setting-control {
    width: 100%;
  }
  
  .footer-content {
    flex-direction: column;
    gap: var(--space-3);
    align-items: stretch;
  }
  
  .footer-actions {
    justify-content: center;
  }
}

/* Animation */
@keyframes slide-in-right {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.animate-slide-in-right {
  animation: slide-in-right 0.3s ease-out;
}
</style> 