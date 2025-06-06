# Manual Test Instructions - Task 5.5: API Integration

## 🧪 Comprehensive Testing Guide

**Task**: Task 5.5 API Integration Validation  
**Status**: ✅ Implementation Complete  
**Date**: 2025-01-03  

## 🚀 Pre-Testing Setup

### 1. Environment Preparation
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Server should start at http://localhost:5173
```

### 2. Environment Variables Check
Ensure these files exist in `frontend/`:
- `.env` (development configuration)
- `.env.production` (production configuration)

## 🔍 Test Scenarios

### Scenario 1: Environment Configuration Validation ✅

**Test Steps:**
1. Open browser console (F12)
2. Navigate to http://localhost:5173
3. Check console for environment loading logs

**Expected Results:**
```javascript
🔧 Environment loaded: development
🌐 API Base URL: http://localhost:8000
⚡ Debug Mode: true
```

**Pass Criteria:**
- ✅ No environment configuration errors
- ✅ Proper API base URL loading
- ✅ Feature flags working correctly

---

### Scenario 2: Connection Status Monitoring ✅

**Test Steps:**
1. Open RepoChat frontend
2. Observe header status indicator
3. Click "Thử lại" if connection shows offline

**Expected Results:**
- 🔴 "Ngoại tuyến" status (backend not running - expected)
- ⚠️ Connection banner with retry option
- 🔄 Loading state during connection check

**Pass Criteria:**
- ✅ Connection status displayed correctly
- ✅ Retry mechanism functional
- ✅ No JavaScript errors in console

---

### Scenario 3: Chat Interface API Integration ✅

**Test Steps:**
1. Navigate to chat interface
2. Type a test message: "Hello RepoChat!"
3. Press Enter or click Send
4. Observe error handling

**Expected Results:**
```javascript
🔧 ChatInterface Debug: {
  connected: false,
  loading: false,
  error: "Không thể kết nối đến server",
  messagesCount: 1,
  repositoryContext: null
}
```

**Pass Criteria:**
- ✅ Message appears in chat with user avatar
- ✅ Error message displayed in Vietnamese
- ✅ Loading states work correctly
- ✅ No console errors during message flow

---

### Scenario 4: Repository Scanning UI ✅

**Test Steps:**
1. In welcome screen, enter repository URL: `https://github.com/octocat/Hello-World.git`
2. Click "🔍 Quét Repository"
3. Observe API call and error handling

**Expected Results:**
- 🔄 Loading state activated
- ⚠️ Error message: "Lỗi khi quét repository: [error details]"
- 📝 Message added to chat with scan attempt

**Pass Criteria:**
- ✅ Repository URL validation working
- ✅ API call structure correct
- ✅ Error handling comprehensive
- ✅ UI feedback appropriate

---

### Scenario 5: Settings Screen API Integration ✅

**Test Steps:**
1. Navigate to Settings (⚙️ icon)
2. Modify LLM model selection
3. Click "💾 Lưu Cài Đặt"
4. Check localStorage persistence

**Expected Results:**
```javascript
// In browser console:
localStorage.getItem('repochat_settings')
// Should return updated settings JSON
```

**Pass Criteria:**
- ✅ Settings UI loads without errors
- ✅ Model selection dropdowns functional
- ✅ Save attempt triggers API call
- ✅ Settings persist in localStorage as fallback

---

### Scenario 6: Error Handling Validation ✅

**Test Steps:**
1. Open browser Network tab (F12 → Network)
2. Try sending a chat message
3. Observe HTTP request attempts
4. Check error message display

**Expected Results:**
- 🌐 HTTP requests to `http://localhost:8000/api/chat/message`
- 🔴 Failed requests (backend not running)
- 💬 User-friendly error messages in Vietnamese
- 🔄 Retry mechanisms available

**Pass Criteria:**
- ✅ HTTP requests properly formatted
- ✅ Error messages user-friendly
- ✅ No application crashes
- ✅ Graceful degradation working

---

### Scenario 7: Development Debug Features ✅

**Test Steps:**
1. Open browser console
2. Look for debug logs
3. Trigger various UI actions
4. Monitor real-time logging

**Expected Results:**
```javascript
[2025-01-03T10:00:00.000Z] [INFO] 🚀 Starting API Integration Test Suite
[2025-01-03T10:00:00.001Z] [INFO] 🔧 Environment: development
[2025-01-03T10:00:00.002Z] [INFO] ✅ Test passed: Environment Configuration (3ms)
```

**Pass Criteria:**
- ✅ Comprehensive debug logging
- ✅ Performance timing information
- ✅ Real-time state monitoring
- ✅ Error tracking functional

---

## 🎯 Integration Test Checklist

### Core Functionality Tests
- [ ] Environment configuration loads correctly
- [ ] API service initializes without errors
- [ ] HTTP client configured with proper headers
- [ ] Connection status monitoring works
- [ ] Error handling displays Vietnamese messages
- [ ] Settings persistence in localStorage
- [ ] Chat interface API call structure correct
- [ ] Repository scanning UI integration functional

### Performance Tests
- [ ] Application starts within 3 seconds
- [ ] API calls have proper timeout handling
- [ ] No memory leaks in composables
- [ ] Reactive state updates efficiently

### Error Resilience Tests
- [ ] Network errors handled gracefully
- [ ] Backend unavailable scenario works
- [ ] Invalid input validation working
- [ ] Recovery mechanisms functional

### Development Experience Tests
- [ ] Hot reload works with API changes
- [ ] Debug logging comprehensive
- [ ] TypeScript types working (JSDoc)
- [ ] Console errors minimal

## 📊 Success Criteria Summary

**Task 5.5 is considered COMPLETE when:**

1. **✅ Environment Setup**: Configuration system working
2. **✅ API Integration**: HTTP client và composables functional
3. **✅ Component Updates**: ChatInterface và SettingsScreen integrated
4. **✅ Error Handling**: Comprehensive error management
5. **✅ Testing Framework**: Validation system in place
6. **✅ Documentation**: Complete implementation guide

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: "Module not found" errors
**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

#### Issue: Environment variables not loading
**Solution:**
1. Check `.env` file exists in `frontend/` directory
2. Verify Vite configuration in `vite.config.js`
3. Restart development server

#### Issue: API calls failing silently
**Solution:**
1. Enable debug mode: `VITE_ENABLE_DEBUG_MODE=true`
2. Check browser Network tab
3. Verify console logs for error details

#### Issue: Connection status not updating
**Solution:**
1. Check `useConnectionStatus` composable
2. Verify retry logic in API service
3. Monitor WebSocket connections (future feature)

## 🎉 Completion Validation

When all test scenarios pass:

1. **Frontend Integration**: ✅ Complete
2. **API Structure**: ✅ Production-ready
3. **Error Handling**: ✅ Comprehensive
4. **Development Tools**: ✅ Functional
5. **Documentation**: ✅ Complete

**Task 5.5: API Integration is successfully COMPLETED and ready for backend connection!**

---

**Next Steps:**
- Task 5.6: WebSocket Integration
- Task 5.7: Advanced Features
- Backend API endpoint development
- Production deployment preparation 