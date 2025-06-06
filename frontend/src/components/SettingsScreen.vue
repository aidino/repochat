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
/* Settings Screen - Gemini-Inspired Design */
.settings-screen {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--gradient-secondary);
  font-family: var(--font-family-primary);
  color: var(--color-text-primary);
  overflow: hidden;
}

/* Header */
.settings-header {
  background: var(--gradient-primary);
  color: var(--color-text-inverse);
  padding: var(--space-6) var(--space-8);
  flex-shrink: 0;
  box-shadow: var(--shadow-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.back-btn {
  font-size: var(--font-size-lg);
  padding: var(--space-2);
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--color-text-inverse);
  border-radius: var(--radius-xl);
  transition: all var(--transition-fast);
  backdrop-filter: blur(10px);
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.header-text {
  flex: 1;
}

.settings-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-inverse);
  margin: 0 0 var(--space-1) 0;
  letter-spacing: -0.025em;
}

.settings-subtitle {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

/* Content */
.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-8);
}

.settings-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* Sections */
.settings-section {
  margin-bottom: var(--space-12);
}

.section-header {
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2) 0;
  letter-spacing: -0.025em;
}

.section-description {
  color: var(--color-text-secondary);
  margin: 0;
  line-height: var(--line-height-relaxed);
}

/* Settings Grid */
.settings-grid {
  display: grid;
  gap: var(--space-6);
}

.setting-item {
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-2xl);
  padding: var(--space-6);
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--space-6);
  align-items: start;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(20px);
}

.setting-item:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.setting-info {
  min-width: 0;
}

.setting-label {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
  display: block;
}

.setting-description {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-3);
  line-height: var(--line-height-normal);
}

.setting-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.setting-team,
.setting-usage {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.setting-team {
  font-weight: var(--font-weight-medium);
}

/* Controls */
.setting-control {
  min-width: 200px;
}

.model-select {
  width: 100%;
  padding: var(--space-4) var(--space-5);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-xl);
  background: var(--color-surface);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  transition: all var(--transition-fast);
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23B6B09F' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right var(--space-4) center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: calc(var(--space-10) + var(--space-2));
  font-family: var(--font-family-primary);
  font-weight: var(--font-weight-medium);
}

.model-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(182, 176, 159, 0.2);
}

.model-select:hover {
  border-color: var(--color-border-strong);
  background-color: var(--color-background-secondary);
}

.model-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.model-info {
  display: flex;
  justify-content: space-between;
  margin-top: var(--space-3);
  font-size: var(--font-size-xs);
  padding: var(--space-3);
  background: var(--color-background-secondary);
  border-radius: var(--radius-lg);
  border-left: 4px solid var(--color-primary);
}

.model-provider {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.model-cost {
  color: var(--color-text-tertiary);
  font-weight: var(--font-weight-medium);
}

/* Footer */
.settings-footer {
  background: rgba(255, 255, 255, 0.8);
  border-top: 1px solid var(--color-border-subtle);
  padding: var(--space-6) var(--space-8);
  flex-shrink: 0;
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(20px);
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
  gap: var(--space-1);
}

.save-status {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-success);
}

.save-status.has-changes {
  color: var(--color-warning);
}

.last-saved {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.footer-actions {
  display: flex;
  gap: var(--space-4);
}

.save-btn.saving {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Toasts */
.toast {
  position: fixed;
  top: var(--space-8);
  right: var(--space-8);
  background: var(--color-surface);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-4) var(--space-6);
  box-shadow: var(--shadow-xl);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  z-index: var(--z-toast);
  animation: slideInRight var(--transition-normal) ease;
  backdrop-filter: blur(20px);
}

.toast-success {
  border-color: var(--color-success);
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
}

.toast-icon {
  font-size: var(--font-size-lg);
}

.toast-message {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
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

/* Responsive Design */
@media (max-width: 768px) {
  .settings-header {
    padding: var(--space-4) var(--space-6);
  }
  
  .settings-content {
    padding: var(--space-4);
  }
  
  .setting-item {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }
  
  .setting-control {
    min-width: auto;
  }
  
  .footer-content {
    flex-direction: column;
    gap: var(--space-4);
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
    gap: var(--space-3);
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .toast {
    top: var(--space-4);
    right: var(--space-4);
    left: var(--space-4);
  }
  
  .settings-header {
    padding: var(--space-4);
  }
  
  .settings-content {
    padding: var(--space-4);
  }
  
  .setting-item {
    padding: var(--space-4);
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .settings-screen {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  }
  
  .settings-footer {
    background: rgba(38, 38, 38, 0.8);
  }
  
  .toast-success {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
  }
}

/* Accessibility improvements */
.back-btn:focus-visible,
.model-select:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Enhanced animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style> 