/**
 * Environment Configuration
 * Centralized environment variable access cho RepoChat Frontend
 */

// Validate required environment variables
const requiredEnvVars = ['VITE_API_BASE_URL']

for (const envVar of requiredEnvVars) {
  if (!import.meta.env[envVar]) {
    console.warn(`Missing environment variable: ${envVar}, using default value`)
  }
}

// Environment configuration object
export const config = {
  // API Configuration
  api: {
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
    wsURL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
    retryAttempts: parseInt(import.meta.env.VITE_API_RETRY_ATTEMPTS || '3'),
    retryDelay: parseInt(import.meta.env.VITE_API_RETRY_DELAY || '1000')
  },

  // Application Configuration
  app: {
    name: import.meta.env.VITE_APP_NAME || 'RepoChat',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    env: import.meta.env.VITE_APP_ENV || 'development'
  },

  // Feature Flags
  features: {
    debugMode: import.meta.env.VITE_ENABLE_DEBUG_MODE === 'true',
    mockAPI: import.meta.env.VITE_ENABLE_MOCK_API === 'true',
    logging: import.meta.env.VITE_ENABLE_LOGGING !== 'false', // Default to true
    healthCheck: import.meta.env.VITE_ENABLE_HEALTH_CHECK !== 'false',
    autoRetry: import.meta.env.VITE_ENABLE_AUTO_RETRY !== 'false'
  },

  // Authentication Configuration
  auth: {
    enabled: import.meta.env.VITE_AUTH_ENABLED === 'true',
    tokenStorageKey: import.meta.env.VITE_JWT_STORAGE_KEY || 'repochat_token',
    refreshTokenKey: import.meta.env.VITE_REFRESH_TOKEN_KEY || 'repochat_refresh_token',
    tokenExpiration: parseInt(import.meta.env.VITE_TOKEN_EXPIRATION || '3600') // 1 hour
  },

  // UI Configuration
  ui: {
    defaultTheme: import.meta.env.VITE_DEFAULT_THEME || 'dark',
    defaultLanguage: import.meta.env.VITE_DEFAULT_LANGUAGE || 'vi',
    showWelcomeScreen: import.meta.env.VITE_SHOW_WELCOME_SCREEN !== 'false',
    autoScroll: import.meta.env.VITE_AUTO_SCROLL !== 'false'
  },

  // Repository Configuration
  repository: {
    maxScanTimeMs: parseInt(import.meta.env.VITE_MAX_SCAN_TIME_MS || '300000'), // 5 minutes
    supportedLanguages: (import.meta.env.VITE_SUPPORTED_LANGUAGES || 'java,python,kotlin,dart,javascript,typescript').split(','),
    maxRepositorySize: parseInt(import.meta.env.VITE_MAX_REPOSITORY_SIZE || '100') // MB
  },

  // Performance Configuration
  performance: {
    requestTimeout: parseInt(import.meta.env.VITE_REQUEST_TIMEOUT || '30000'),
    connectionTimeout: parseInt(import.meta.env.VITE_CONNECTION_TIMEOUT || '10000'),
    maxConcurrentRequests: parseInt(import.meta.env.VITE_MAX_CONCURRENT_REQUESTS || '5'),
    cacheDuration: parseInt(import.meta.env.VITE_CACHE_DURATION || '300000') // 5 minutes
  },

  // Development helpers
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  mode: import.meta.env.MODE
}

// Export individual configurations for convenience
export const { api, app, features, auth, ui, repository, performance } = config

// Development logging
if (config.features.debugMode) {
  console.group('🔧 RepoChat Environment Configuration')
  console.log('Environment:', config.mode)
  console.log('API Base URL:', config.api.baseURL)
  console.log('Debug Mode:', config.features.debugMode)
  console.log('Mock API:', config.features.mockAPI)
  console.log('Full Config:', config)
  console.groupEnd()
}

// Export validation function
export function validateEnvironment() {
  const issues = []
  
  // Check API URL format
  try {
    new URL(config.api.baseURL)
  } catch (e) {
    issues.push(`Invalid API base URL: ${config.api.baseURL}`)
  }
  
  // Check timeout values
  if (config.api.timeout < 1000) {
    issues.push('API timeout should be at least 1000ms')
  }
  
  // Check repository configuration
  if (config.repository.maxScanTimeMs < 30000) {
    issues.push('Max scan time should be at least 30 seconds')
  }
  
  return {
    valid: issues.length === 0,
    issues
  }
}

export default config