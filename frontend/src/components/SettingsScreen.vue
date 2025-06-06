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
            :disabled="isSaving"
          >
            <span class="icon">🔄</span>
            Mặc định
          </button>
        </div>
      </div>
    </header>

    <!-- Settings Content -->
    <main class="settings-content">
      <div class="settings-container">
        
        <!-- LLM Configuration Section -->
        <section class="settings-section">
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
                  :disabled="isSaving"
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
                  :disabled="isSaving"
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
                  :disabled="isSaving"
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
            :disabled="!hasModifications || isSaving"
          >
            <span class="icon">↶</span>
            Hủy thay đổi
          </button>
          
          <button 
            class="btn btn-primary save-btn"
            @click="saveSettings"
            :disabled="!hasModifications || isSaving"
            :class="{ 'saving': isSaving }"
          >
            <span class="icon">{{ isSaving ? '⏳' : '💾' }}</span>
            {{ isSaving ? 'Đang lưu...' : 'Lưu cài đặt' }}
          </button>
        </div>
      </div>
    </footer>

    <!-- Success Toast -->
    <div v-if="showSuccessToast" class="toast toast-success">
      <span class="toast-icon">✅</span>
      <span class="toast-message">Cài đặt đã được lưu thành công!</span>
    </div>

  </div>
</template>

<script>
export default {
  name: 'SettingsScreen',
  
  emits: [
    'go-back',
    'settings-saved'
  ],
  
  data() {
    return {
      // Settings state
      settings: {
        nluModel: 'gpt-4o-mini',
        codeAnalysisModel: 'gpt-4-turbo',
        reportGenerationModel: 'gpt-4o-mini'
      },
      
      // Original settings for comparison
      originalSettings: {},
      
      // UI state
      isSaving: false,
      hasModifications: false,
      lastSavedTime: null,
      showSuccessToast: false,
      
      // Available LLM models (hardcoded as per DoD)
      availableModels: [
        {
          id: 'gpt-4o-mini',
          name: 'GPT-4O Mini',
          provider: 'OpenAI',
          cost: 'Thấp'
        },
        {
          id: 'gpt-4-turbo',
          name: 'GPT-4 Turbo',
          provider: 'OpenAI',
          cost: 'Trung bình'
        },
        {
          id: 'gpt-4',
          name: 'GPT-4',
          provider: 'OpenAI',
          cost: 'Cao'
        },
        {
          id: 'claude-3-haiku',
          name: 'Claude 3 Haiku',
          provider: 'Anthropic',
          cost: 'Thấp'
        },
        {
          id: 'claude-3-sonnet',
          name: 'Claude 3 Sonnet',
          provider: 'Anthropic',
          cost: 'Trung bình'
        }
      ]
    }
  },
  
  mounted() {
    // Initialize settings
    this.loadSettings()
    this.originalSettings = { ...this.settings }
  },
  
  methods: {
    // === Core Actions ===
    handleGoBack() {
      if (this.hasModifications) {
        const confirmLeave = confirm('Bạn có thay đổi chưa lưu. Bạn có chắc muốn thoát?')
        if (!confirmLeave) return
      }
      
      this.$emit('go-back')
    },
    
    saveSettings() {
      this.isSaving = true
      
      // Simulate API call delay
      setTimeout(() => {
        try {
          // Create settings object for logging (DoD requirement)
          const configToSave = {
            llmModels: {
              nlu: this.settings.nluModel,
              codeAnalysis: this.settings.codeAnalysisModel,
              reportGeneration: this.settings.reportGenerationModel
            },
            timestamp: new Date().toISOString(),
            userId: 'user_001' // Mock user ID
          }
          
          // Log to console as per DoD requirement
          console.log('🎯 RepoChat LLM Configuration Saved:', configToSave)
          console.table({
            'NLU Model': this.getModelInfo(this.settings.nluModel).name,
            'Code Analysis Model': this.getModelInfo(this.settings.codeAnalysisModel).name,
            'Report Generation Model': this.getModelInfo(this.settings.reportGenerationModel).name
          })
          
          // Update state
          this.originalSettings = { ...this.settings }
          this.hasModifications = false
          this.lastSavedTime = new Date()
          this.isSaving = false
          
          // Show success feedback
          this.showSuccessToast = true
          setTimeout(() => {
            this.showSuccessToast = false
          }, 3000)
          
          // Emit event for parent component
          this.$emit('settings-saved', configToSave)
          
          // Save to localStorage for persistence
          localStorage.setItem('repochat_settings', JSON.stringify(this.settings))
          
        } catch (error) {
          console.error('Error saving settings:', error)
          this.isSaving = false
        }
      }, 1500) // Simulate network delay
    },
    
    resetToDefaults() {
      const confirmReset = confirm('Bạn có chắc muốn reset về cài đặt mặc định?')
      if (!confirmReset) return
      
      this.settings = {
        nluModel: 'gpt-4o-mini',
        codeAnalysisModel: 'gpt-4-turbo',
        reportGenerationModel: 'gpt-4o-mini'
      }
      
      this.markAsModified()
      console.log('🔄 Settings reset to defaults')
    },
    
    discardChanges() {
      const confirmDiscard = confirm('Bạn có chắc muốn hủy tất cả thay đổi?')
      if (!confirmDiscard) return
      
      this.settings = { ...this.originalSettings }
      this.hasModifications = false
      console.log('↶ Changes discarded')
    },
    
    // === Settings Management ===
    loadSettings() {
      try {
        const saved = localStorage.getItem('repochat_settings')
        if (saved) {
          const parsedSettings = JSON.parse(saved)
          this.settings = { ...this.settings, ...parsedSettings }
          console.log('📂 Settings loaded from localStorage')
        }
      } catch (error) {
        console.warn('Could not load settings from localStorage:', error)
      }
    },
    
    markAsModified() {
      this.hasModifications = JSON.stringify(this.settings) !== JSON.stringify(this.originalSettings)
    },
    
    // === Utility Functions ===
    getModelInfo(modelId) {
      return this.availableModels.find(model => model.id === modelId) || this.availableModels[0]
    },
    
    formatTime(date) {
      return date.toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
/* Settings Screen Container */
.settings-screen {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  overflow: hidden;
}

/* Header */
.settings-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 1.5rem 2rem;
  flex-shrink: 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  font-size: 1.2rem;
  padding: 0.5rem;
}

.header-text {
  flex: 1;
}

.settings-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.settings-subtitle {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Content */
.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.settings-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* Sections */
.settings-section {
  margin-bottom: 3rem;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.section-description {
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* Settings Grid */
.settings-grid {
  display: grid;
  gap: 1.5rem;
}

.setting-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1.5rem;
  align-items: start;
  transition: all 0.2s ease;
}

.setting-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.1);
}

.setting-info {
  min-width: 0;
}

.setting-label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  display: block;
}

.setting-description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.setting-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.setting-team,
.setting-usage {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.setting-team {
  font-weight: 500;
}

/* Controls */
.setting-control {
  min-width: 200px;
}

.model-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background: var(--bg-primary);
  font-size: 0.875rem;
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.model-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.model-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.model-info {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.75rem;
}

.model-provider {
  color: var(--text-tertiary);
}

.model-cost {
  color: var(--text-secondary);
  font-weight: 500;
}

/* Footer */
.settings-footer {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: 1rem 2rem;
  flex-shrink: 0;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.save-status {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--success-color);
}

.save-status.has-changes {
  color: var(--error-color);
}

.last-saved {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.footer-actions {
  display: flex;
  gap: 1rem;
}

.save-btn.saving {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Toasts */
.toast {
  position: fixed;
  top: 2rem;
  right: 2rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  padding: 1rem 1.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 1000;
  animation: slideInRight 0.3s ease;
}

.toast-success {
  border-color: var(--success-color);
  background: #f0f9ff;
}

.toast-icon {
  font-size: 1.2rem;
}

.toast-message {
  font-weight: 500;
  color: var(--text-primary);
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .settings-header {
    padding: 1rem;
  }
  
  .settings-content {
    padding: 1rem;
  }
  
  .setting-item {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .setting-control {
    min-width: auto;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .footer-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .toast {
    top: 1rem;
    right: 1rem;
    left: 1rem;
    right: 1rem;
  }
}
</style> 