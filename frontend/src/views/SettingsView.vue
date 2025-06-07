<template>
  <div class="settings-page">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Cài đặt</h1>
        <p class="text-gray-600">Quản lý API keys, preferences và cài đặt bảo mật</p>
      </div>

      <!-- Settings Tabs -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200">
        <!-- Tab Navigation -->
        <div class="border-b border-gray-200">
          <nav class="flex">
            <button 
              v-for="tab in tabs" 
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
                activeTab === tab.id 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              <i :class="tab.icon" class="mr-2"></i>
              {{ tab.name }}
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="p-6">
          <!-- API Keys Tab -->
          <div v-if="activeTab === 'api-keys'" class="space-y-6">
            <div class="mb-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-2">API Keys</h2>
              <p class="text-gray-600">Quản lý API keys cho các nhà cung cấp AI khác nhau</p>
            </div>

            <!-- Add New API Key -->
            <div class="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 class="font-medium text-gray-900 mb-3">Thêm API Key mới</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <select 
                  v-model="newApiKey.provider" 
                  class="form-select rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="">Chọn nhà cung cấp</option>
                  <option v-for="provider in availableProviders" :key="provider.provider" :value="provider.provider">
                    {{ provider.name }}
                  </option>
                </select>
                
                <input 
                  v-model="newApiKey.api_key"
                  type="password" 
                  placeholder="Nhập API key..."
                  class="form-input rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                
                <input 
                  v-model="newApiKey.nickname"
                  type="text" 
                  placeholder="Tên gọi (tùy chọn)"
                  class="form-input rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div class="flex gap-2 mt-4">
                <button 
                  @click="addApiKey"
                  :disabled="!newApiKey.provider || !newApiKey.api_key || isLoading"
                  class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <i class="fas fa-plus mr-2"></i>
                  {{ isLoading ? 'Đang thêm...' : 'Thêm API Key' }}
                </button>
                
                <button 
                  @click="clearForm"
                  class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Hủy
                </button>
              </div>
            </div>

            <!-- API Keys List -->
            <div class="space-y-4">
              <h3 class="font-medium text-gray-900">API Keys hiện tại</h3>
              
              <div v-if="userApiKeys.length === 0" class="text-center py-8 text-gray-500">
                <i class="fas fa-key text-4xl mb-2"></i>
                <p>Chưa có API key nào được cấu hình</p>
              </div>
              
              <div v-else class="space-y-3">
                <div 
                  v-for="apiKey in userApiKeys" 
                  :key="apiKey.provider"
                  class="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg"
                >
                  <div class="flex items-center">
                    <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                      <i class="fas fa-robot text-blue-600"></i>
                    </div>
                    <div>
                      <h4 class="font-medium text-gray-900">
                        {{ getProviderName(apiKey.provider) }}
                        <span v-if="apiKey.nickname" class="text-sm text-gray-500">({{ apiKey.nickname }})</span>
                      </h4>
                      <p class="text-sm text-gray-600">
                        Thêm vào: {{ formatDate(apiKey.created_at) }}
                        <span v-if="apiKey.last_used" class="ml-2">
                          • Sử dụng lần cuối: {{ formatDate(apiKey.last_used) }}
                        </span>
                      </p>
                    </div>
                  </div>
                  
                  <div class="flex items-center space-x-2">
                    <span 
                      :class="[
                        'px-2 py-1 text-xs rounded-full',
                        apiKey.is_valid 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      ]"
                    >
                      {{ apiKey.is_valid ? 'Hoạt động' : 'Lỗi' }}
                    </span>
                    
                    <button 
                      @click="testApiKey(apiKey.provider)"
                      class="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200"
                    >
                      <i class="fas fa-vial mr-1"></i>
                      Test
                    </button>
                    
                    <button 
                      @click="removeApiKey(apiKey.provider)"
                      class="px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200"
                    >
                      <i class="fas fa-trash mr-1"></i>
                      Xóa
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Preferences Tab -->
          <div v-if="activeTab === 'preferences'" class="space-y-6">
            <div class="mb-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-2">Tùy chọn</h2>
              <p class="text-gray-600">Cài đặt ngôn ngữ, giao diện và các tùy chọn khác</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Language -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Ngôn ngữ</label>
                <select 
                  v-model="preferences.language"
                  class="form-select w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="vi">Tiếng Việt</option>
                  <option value="en">English</option>
                </select>
              </div>

              <!-- Theme -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Giao diện</label>
                <select 
                  v-model="preferences.theme"
                  class="form-select w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="light">Sáng</option>
                  <option value="dark">Tối</option>
                  <option value="auto">Tự động</option>
                </select>
              </div>

              <!-- Default LLM Provider -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Nhà cung cấp AI mặc định</label>
                <select 
                  v-model="preferences.default_llm_provider"
                  class="form-select w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option v-for="provider in availableProviders" :key="provider.provider" :value="provider.provider">
                    {{ provider.name }}
                  </option>
                </select>
              </div>

              <!-- Default LLM Model -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Model AI mặc định</label>
                <select 
                  v-model="preferences.default_llm_model"
                  class="form-select w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                  <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                </select>
              </div>
            </div>

            <!-- Checkboxes -->
            <div class="space-y-4">
              <div class="flex items-center">
                <input 
                  id="verbose-output" 
                  v-model="preferences.verbose_output"
                  type="checkbox" 
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="verbose-output" class="ml-2 block text-sm text-gray-900">
                  Output chi tiết
                </label>
              </div>

              <div class="flex items-center">
                <input 
                  id="auto-confirm" 
                  v-model="preferences.auto_confirm"
                  type="checkbox" 
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="auto-confirm" class="ml-2 block text-sm text-gray-900">
                  Tự động xác nhận các thao tác
                </label>
              </div>

              <div class="flex items-center">
                <input 
                  id="notification-email" 
                  v-model="preferences.notification_email"
                  type="checkbox" 
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="notification-email" class="ml-2 block text-sm text-gray-900">
                  Nhận thông báo qua email
                </label>
              </div>
            </div>

            <!-- Save Button -->
            <div class="pt-4">
              <button 
                @click="savePreferences"
                :disabled="isLoading"
                class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                <i class="fas fa-save mr-2"></i>
                {{ isLoading ? 'Đang lưu...' : 'Lưu thay đổi' }}
              </button>
            </div>
          </div>

          <!-- Security Tab -->
          <div v-if="activeTab === 'security'" class="space-y-6">
            <div class="mb-6">
              <h2 class="text-xl font-semibold text-gray-900 mb-2">Bảo mật</h2>
              <p class="text-gray-600">Cài đặt bảo mật và quyền riêng tư</p>
            </div>

            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">Xác thực 2 yếu tố</h3>
                  <p class="text-sm text-gray-500">Thêm lớp bảo mật cho tài khoản</p>
                </div>
                <input 
                  v-model="security.two_factor_enabled"
                  type="checkbox" 
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>

              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-medium text-gray-900">Mã hóa dữ liệu</h3>
                  <p class="text-sm text-gray-500">Yêu cầu mã hóa cho tất cả dữ liệu</p>
                </div>
                <input 
                  v-model="security.require_encryption"
                  type="checkbox" 
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Timeout phiên làm việc (phút)
                </label>
                <select 
                  v-model="security.session_timeout_minutes"
                  class="form-select w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option :value="30">30 phút</option>
                  <option :value="60">1 giờ</option>
                  <option :value="240">4 giờ</option>
                  <option :value="480">8 giờ</option>
                  <option :value="1440">24 giờ</option>
                </select>
              </div>
            </div>

            <!-- Save Button -->
            <div class="pt-4">
              <button 
                @click="saveSecuritySettings"
                :disabled="isLoading"
                class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                <i class="fas fa-shield-alt mr-2"></i>
                {{ isLoading ? 'Đang lưu...' : 'Lưu cài đặt bảo mật' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" class="fixed bottom-4 right-4 max-w-sm">
      <div 
        :class="[
          'p-4 rounded-lg shadow-lg',
          message.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        ]"
      >
        <div class="flex items-center">
          <i :class="message.type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'" class="mr-2"></i>
          {{ message.text }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'SettingsView',
  setup() {
    const activeTab = ref('api-keys')
    const isLoading = ref(false)
    const message = ref(null)

    const tabs = [
      { id: 'api-keys', name: 'API Keys', icon: 'fas fa-key' },
      { id: 'preferences', name: 'Tùy chọn', icon: 'fas fa-cog' },
      { id: 'security', name: 'Bảo mật', icon: 'fas fa-shield-alt' }
    ]

    // Sample user ID - trong thực tế sẽ lấy từ authentication
    const userId = ref('user123')

    const availableProviders = ref([])
    const userApiKeys = ref([])

    const newApiKey = reactive({
      provider: '',
      api_key: '',
      nickname: ''
    })

    const preferences = reactive({
      language: 'vi',
      theme: 'light',
      default_llm_provider: 'openai',
      default_llm_model: 'gpt-4o-mini',
      verbose_output: false,
      auto_confirm: false,
      notification_email: true,
      notification_browser: true
    })

    const security = reactive({
      two_factor_enabled: false,
      session_timeout_minutes: 480,
      require_encryption: true
    })

    // Load data
    onMounted(async () => {
      await Promise.all([
        loadAvailableProviders(),
        loadUserSettings(),
        loadUserApiKeys()
      ])
    })

    const loadAvailableProviders = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api-providers')
        availableProviders.value = response.data.providers
      } catch (error) {
        console.error('Error loading providers:', error)
        showMessage('Lỗi khi tải danh sách nhà cung cấp', 'error')
      }
    }

    const loadUserSettings = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/users/${userId.value}/settings`)
        const settings = response.data
        
        // Update preferences
        Object.assign(preferences, settings.preferences)
        Object.assign(security, settings.security)
        
      } catch (error) {
        console.error('Error loading user settings:', error)
        showMessage('Lỗi khi tải cài đặt người dùng', 'error')
      }
    }

    const loadUserApiKeys = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/users/${userId.value}/api-keys`)
        userApiKeys.value = response.data.api_keys
      } catch (error) {
        console.error('Error loading API keys:', error)
        showMessage('Lỗi khi tải danh sách API keys', 'error')
      }
    }

    const addApiKey = async () => {
      if (!newApiKey.provider || !newApiKey.api_key) {
        showMessage('Vui lòng điền đầy đủ thông tin', 'error')
        return
      }

      isLoading.value = true
      try {
        await axios.post(`http://localhost:8000/users/${userId.value}/api-keys`, {
          provider: newApiKey.provider,
          api_key: newApiKey.api_key,
          nickname: newApiKey.nickname
        })

        showMessage('Thêm API key thành công', 'success')
        clearForm()
        await loadUserApiKeys()
      } catch (error) {
        console.error('Error adding API key:', error)
        showMessage('Lỗi khi thêm API key', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const removeApiKey = async (provider) => {
      if (!confirm('Bạn có chắc muốn xóa API key này?')) return

      try {
        await axios.delete(`http://localhost:8000/users/${userId.value}/api-keys/${provider}`)
        showMessage('Xóa API key thành công', 'success')
        await loadUserApiKeys()
      } catch (error) {
        console.error('Error removing API key:', error)
        showMessage('Lỗi khi xóa API key', 'error')
      }
    }

    const testApiKey = async (provider) => {
      try {
        const response = await axios.get(`http://localhost:8000/users/${userId.value}/api-keys/${provider}/test`)
        
        if (response.data.is_valid) {
          showMessage(`API key ${provider} hoạt động tốt`, 'success')
        } else {
          showMessage(`API key ${provider} có lỗi: ${response.data.error_message}`, 'error')
        }
      } catch (error) {
        console.error('Error testing API key:', error)
        showMessage('Lỗi khi test API key', 'error')
      }
    }

    const savePreferences = async () => {
      isLoading.value = true
      try {
        await axios.put(`http://localhost:8000/users/${userId.value}/settings`, {
          preferences: preferences
        })
        showMessage('Lưu tùy chọn thành công', 'success')
      } catch (error) {
        console.error('Error saving preferences:', error)
        showMessage('Lỗi khi lưu tùy chọn', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const saveSecuritySettings = async () => {
      isLoading.value = true
      try {
        await axios.put(`http://localhost:8000/users/${userId.value}/settings`, {
          security: security
        })
        showMessage('Lưu cài đặt bảo mật thành công', 'success')
      } catch (error) {
        console.error('Error saving security settings:', error)
        showMessage('Lỗi khi lưu cài đặt bảo mật', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const clearForm = () => {
      newApiKey.provider = ''
      newApiKey.api_key = ''
      newApiKey.nickname = ''
    }

    const getProviderName = (provider) => {
      const found = availableProviders.value.find(p => p.provider === provider)
      return found ? found.name : provider
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('vi-VN')
    }

    const showMessage = (text, type) => {
      message.value = { text, type }
      setTimeout(() => {
        message.value = null
      }, 3000)
    }

    return {
      activeTab,
      isLoading,
      message,
      tabs,
      userId,
      availableProviders,
      userApiKeys,
      newApiKey,
      preferences,
      security,
      addApiKey,
      removeApiKey,
      testApiKey,
      savePreferences,
      saveSecuritySettings,
      clearForm,
      getProviderName,
      formatDate,
      showMessage
    }
  }
}
</script>

<style scoped>
.form-input, .form-select {
  @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm;
}
</style> 