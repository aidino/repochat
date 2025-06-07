#!/bin/bash

# Simple Q&A Test Script for RepoChat
echo "🧪 Testing RepoChat Q&A Conversation System"
echo "=============================================="

BASE_URL="http://localhost:8000"

# Test 1: Greeting
echo -e "\n📝 Test 1: Greeting"
RESPONSE1=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào"}')

if echo "$RESPONSE1" | jq -e '.bot_response.content' | grep -q "Chào mừng"; then
  echo "✅ PASS: Greeting works"
  SESSION_ID=$(echo "$RESPONSE1" | jq -r '.session_id')
  echo "Session ID: $SESSION_ID"
else
  echo "❌ FAIL: Greeting failed"
  echo "Response: $RESPONSE1"
  exit 1
fi

# Test 2: Repository Intent
echo -e "\n📝 Test 2: Repository Scanning Intent"
RESPONSE2=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"Quét repository https://github.com/facebook/react.git\"}")

if echo "$RESPONSE2" | jq -e '.bot_response.content' | grep -q "github.com/facebook/react.git"; then
  echo "✅ PASS: Repository intent recognized"
else
  echo "❌ FAIL: Repository intent failed"
  echo "Response: $RESPONSE2"
fi

# Test 3: Q&A with Context
echo -e "\n📝 Test 3: Q&A about Code"
RESPONSE3=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"Định nghĩa của class User ở đâu?\"}")

if echo "$RESPONSE3" | jq -e '.bot_response.content' | grep -q "class User\|Class.*User"; then
  echo "✅ PASS: Q&A provides class information"
else
  echo "❌ FAIL: Q&A response insufficient"
  echo "Response: $RESPONSE3"
fi

# Test 4: Task Execution
echo -e "\n📝 Test 4: Task Execution"
RESPONSE4=$(curl -s -X POST "$BASE_URL/chat/$SESSION_ID/execute")

if echo "$RESPONSE4" | jq -e '.status' | grep -q "success"; then
  echo "✅ PASS: Task execution successful"
  EXECUTION_ID=$(echo "$RESPONSE4" | jq -r '.execution_id')
  echo "Execution ID: $EXECUTION_ID"
else
  echo "❌ FAIL: Task execution failed"
  echo "Response: $RESPONSE4"
fi

# Test 5: Chat History
echo -e "\n📝 Test 5: Chat History"
RESPONSE5=$(curl -s -X GET "$BASE_URL/chat/$SESSION_ID/history")

MESSAGE_COUNT=$(echo "$RESPONSE5" | jq '.messages | length')
if [ "$MESSAGE_COUNT" -gt 0 ]; then
  echo "✅ PASS: Chat history retrieved ($MESSAGE_COUNT messages)"
else
  echo "❌ FAIL: Chat history empty"
  echo "Response: $RESPONSE5"
fi

echo -e "\n🎉 Q&A Conversation Tests Completed!"
echo "Session ID: $SESSION_ID"
echo "Frontend URL: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs" 