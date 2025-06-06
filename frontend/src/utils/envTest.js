import config from '@config/environment.js'

export function testEnvironmentConfig() {
  console.log('🧪 Testing Environment Configuration...')
  
  // Test API configuration
  console.log('API Base URL:', config.api.baseURL)
  console.log('API Timeout:', config.api.timeout)
  
  // Test feature flags
  console.log('Debug Mode:', config.features.debugMode)
  console.log('Mock API:', config.features.mockAPI)
  
  // Test environment detection
  console.log('Environment:', config.app.env)
  console.log('Is Development:', config.isDevelopment)
  console.log('Is Production:', config.isProduction)
  
  return config
}