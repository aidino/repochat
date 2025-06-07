#!/usr/bin/env node

/**
 * Test Script for Q&A Conversation Functionality
 * 
 * Tests the TEAM Interaction & Tasking Q&A system according to DESIGN.md
 */

const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m'
};

function log(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function testChatAPI(message, sessionId = null) {
  try {
    const payload = { message };
    if (sessionId) payload.session_id = sessionId;
    
    const response = await axios.post(`${BASE_URL}/chat`, payload, {
      headers: { 'Content-Type': 'application/json' }
    });
    
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message);
  }
}

async function testTaskExecution(sessionId) {
  try {
    const response = await axios.post(`${BASE_URL}/chat/${sessionId}/execute`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message);
  }
}

async function getChatHistory(sessionId) {
  try {
    const response = await axios.get(`${BASE_URL}/chat/${sessionId}/history`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message);
  }
}

async function runTests() {
  log('cyan', '🧪 Testing RepoChat Q&A Conversation System');
  log('cyan', '='.repeat(50));
  
  let sessionId = null;
  let testResults = [];
  
  // Test 1: Greeting
  try {
    log('blue', '\n📝 Test 1: Greeting and Welcome');
    const response1 = await testChatAPI('Xin chào');
    sessionId = response1.session_id;
    
    const botResponse = response1.bot_response.content;
    const hasWelcome = botResponse.includes('Chào mừng') && botResponse.includes('RepoChat');
    const hasOptions = botResponse.includes('Quét repository') && botResponse.includes('Review Pull Request');
    
    if (hasWelcome && hasOptions) {
      log('green', '✅ PASS: Greeting displays welcome message with options');
      testResults.push({ test: 'Greeting', status: 'PASS' });
    } else {
      log('red', '❌ FAIL: Welcome message missing components');
      testResults.push({ test: 'Greeting', status: 'FAIL' });
    }
    
    log('yellow', `Session ID: ${sessionId}`);
    log('yellow', `Response length: ${botResponse.length} chars`);
    
  } catch (error) {
    log('red', `❌ Test 1 FAILED: ${error.message}`);
    testResults.push({ test: 'Greeting', status: 'ERROR', error: error.message });
  }
  
  // Test 2: Repository Scanning Intent
  try {
    log('blue', '\n📝 Test 2: Repository Scanning Intent Recognition');
    const response2 = await testChatAPI('Quét repository https://github.com/facebook/react.git', sessionId);
    
    const botResponse = response2.bot_response;
    const hasRepoUrl = botResponse.content.includes('https://github.com/facebook/react.git');
    const hasConfirmation = botResponse.content.includes('bắt đầu quét');
    const correctIntent = botResponse.context?.intent === 'scan_repository';
    const correctState = response2.conversation_state === 'repository_provided';
    
    if (hasRepoUrl && hasConfirmation && correctIntent && correctState) {
      log('green', '✅ PASS: Repository scanning intent recognized correctly');
      testResults.push({ test: 'Repository Intent', status: 'PASS' });
    } else {
      log('red', '❌ FAIL: Repository scanning intent not properly recognized');
      log('yellow', `Intent: ${botResponse.context?.intent}, State: ${response2.conversation_state}`);
      testResults.push({ test: 'Repository Intent', status: 'FAIL' });
    }
    
  } catch (error) {
    log('red', `❌ Test 2 FAILED: ${error.message}`);
    testResults.push({ test: 'Repository Intent', status: 'ERROR', error: error.message });
  }
  
  // Test 3: Q&A about Code
  try {
    log('blue', '\n📝 Test 3: Q&A about Code (with repository context)');
    const response3 = await testChatAPI('Định nghĩa của class User ở đâu?', sessionId);
    
    const botResponse = response3.bot_response.content;
    const hasClassInfo = botResponse.includes('class User') || botResponse.includes('Class **User**');
    const hasFileLocation = botResponse.includes('.py') || botResponse.includes('src/');
    const correctIntent = response3.bot_response.context?.intent === 'ask_question';
    
    if (hasClassInfo && hasFileLocation && correctIntent) {
      log('green', '✅ PASS: Q&A provides code location information');
      testResults.push({ test: 'Q&A with Context', status: 'PASS' });
    } else {
      log('red', '❌ FAIL: Q&A response insufficient');
      log('yellow', `Response preview: ${botResponse.substring(0, 100)}...`);
      testResults.push({ test: 'Q&A with Context', status: 'FAIL' });
    }
    
  } catch (error) {
    log('red', `❌ Test 3 FAILED: ${error.message}`);
    testResults.push({ test: 'Q&A with Context', status: 'ERROR', error: error.message });
  }
  
  // Test 4: PR Review Intent
  try {
    log('blue', '\n📝 Test 4: PR Review Intent Recognition');
    const response4 = await testChatAPI('Review PR #123');
    
    const botResponse = response4.bot_response;
    const hasPRId = botResponse.content.includes('#123');
    const correctIntent = botResponse.context?.intent === 'review_pr';
    const needsRepo = botResponse.content.includes('repository');
    
    if (hasPRId && correctIntent && needsRepo) {
      log('green', '✅ PASS: PR review intent recognized and requests repository');
      testResults.push({ test: 'PR Review Intent', status: 'PASS' });
    } else {
      log('red', '❌ FAIL: PR review intent not properly handled');
      testResults.push({ test: 'PR Review Intent', status: 'FAIL' });
    }
    
  } catch (error) {
    log('red', `❌ Test 4 FAILED: ${error.message}`);
    testResults.push({ test: 'PR Review Intent', status: 'ERROR', error: error.message });
  }
  
  // Test 5: Task Execution from Chat
  try {
    log('blue', '\n📝 Test 5: Task Execution from Chat Session');
    
    if (!sessionId) {
      throw new Error('No session ID available');
    }
    
    const response5 = await testTaskExecution(sessionId);
    
    const hasExecutionId = response5.execution_id && response5.execution_id.length > 0;
    const correctStatus = response5.status === 'success';
    const hasRepoUrl = response5.repository_url && response5.repository_url.includes('github.com');
    
    if (hasExecutionId && correctStatus && hasRepoUrl) {
      log('green', '✅ PASS: Task execution initiated from chat session');
      log('yellow', `Execution ID: ${response5.execution_id}`);
      testResults.push({ test: 'Task Execution', status: 'PASS' });
    } else {
      log('red', '❌ FAIL: Task execution failed');
      log('yellow', `Status: ${response5.status}, Execution ID: ${response5.execution_id}`);
      testResults.push({ test: 'Task Execution', status: 'FAIL' });
    }
    
  } catch (error) {
    log('red', `❌ Test 5 FAILED: ${error.message}`);
    testResults.push({ test: 'Task Execution', status: 'ERROR', error: error.message });
  }
  
  // Test 6: Chat History
  try {
    log('blue', '\n📝 Test 6: Chat History Retrieval');
    
    if (!sessionId) {
      throw new Error('No session ID available');
    }
    
    const history = await getChatHistory(sessionId);
    
    const hasMessages = history.messages && history.messages.length > 0;
    const hasState = history.state && history.state.length > 0;
    const hasRepoUrl = history.repository_url && history.repository_url.includes('github.com');
    
    if (hasMessages && hasState && hasRepoUrl) {
      log('green', '✅ PASS: Chat history retrieved successfully');
      log('yellow', `Messages: ${history.messages.length}, State: ${history.state}`);
      testResults.push({ test: 'Chat History', status: 'PASS' });
    } else {
      log('red', '❌ FAIL: Chat history incomplete');
      testResults.push({ test: 'Chat History', status: 'FAIL' });
    }
    
  } catch (error) {
    log('red', `❌ Test 6 FAILED: ${error.message}`);
    testResults.push({ test: 'Chat History', status: 'ERROR', error: error.message });
  }
  
  // Test Summary
  log('cyan', '\n📊 TEST SUMMARY');
  log('cyan', '='.repeat(30));
  
  const passed = testResults.filter(r => r.status === 'PASS').length;
  const failed = testResults.filter(r => r.status === 'FAIL').length;
  const errors = testResults.filter(r => r.status === 'ERROR').length;
  
  testResults.forEach(result => {
    const color = result.status === 'PASS' ? 'green' : result.status === 'FAIL' ? 'red' : 'yellow';
    log(color, `${result.test}: ${result.status}`);
    if (result.error) {
      log('yellow', `  Error: ${result.error}`);
    }
  });
  
  log('cyan', `\nResults: ${passed} PASSED, ${failed} FAILED, ${errors} ERRORS`);
  
  const success_rate = ((passed / testResults.length) * 100).toFixed(1);
  log('cyan', `Success Rate: ${success_rate}%`);
  
  if (passed === testResults.length) {
    log('green', '\n🎉 ALL TESTS PASSED! Q&A Conversation system is working correctly.');
  } else if (passed > testResults.length / 2) {
    log('yellow', '\n⚠️  PARTIAL SUCCESS: Most tests passed, but some issues need attention.');
  } else {
    log('red', '\n❌ MAJOR ISSUES: Multiple tests failed, system needs fixes.');
  }
  
  return { passed, failed, errors, total: testResults.length };
}

// Run tests if called directly
if (require.main === module) {
  runTests().catch(error => {
    log('red', `\n💥 FATAL ERROR: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { runTests, testChatAPI, testTaskExecution, getChatHistory }; 