# 🎮 DEMO INSTRUCTIONS - RepoChat Vue.js Chat Interface

**Hướng dẫn demo và test toàn diện cho Task 5.1**

---

## 🚀 **QUICK START (1 MINUTE SETUP)**

### **Option 1: Automatic Setup Script**
```bash
# Từ thư mục repochat/
cd frontend
./quick_start.sh
```

### **Option 2: Manual Setup**
```bash
# Bước 1: Di chuyển vào frontend directory
cd frontend

# Bước 2: Install dependencies  
npm install

# Bước 3: Start development server
npm run dev
```

### **Option 3: Nếu gặp lỗi**
```bash
# Fix common issues
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 🌐 **TRUY CẬP WEBSITE**

1. **Mở browser** (Chrome, Firefox, Safari, Edge)
2. **Truy cập:** `http://localhost:3000`
3. **Expected:** Trang chat Vue.js hiển thị đầy đủ

---

## 🎯 **DEMO SCENARIOS - TEST THỨ TỰ**

### **📍 Demo 1: First Impression (30 giây)**

**Mục tiêu:** Kiểm tra giao diện tổng thể

1. **Mở trang web:** `http://localhost:3000`
2. **Quan sát layout:**
   - **Sidebar (trái):** Logo RepoChat v1.0, buttons, chat history
   - **Main area (phải):** Welcome screen với instructions
3. **Check responsive:** Resize browser window để test mobile view

**✅ Expected Results:**
- Giao diện professional với colors xanh-trắng-xám
- Text toàn bộ bằng tiếng Việt
- Layout responsive không bị vỡ

### **📍 Demo 2: Welcome Experience (1 phút)**

**Mục tiêu:** Test welcome screen và example questions

1. **Đọc welcome message:**
   ```
   👋 Chào mừng đến với RepoChat!
   Tôi là trợ lý AI phân tích repository thông minh.
   ```

2. **Test 4 example questions:** Click từng button:
   - "Phân tích repository https://github.com/spring-projects/spring-petclinic.git"
   - "Review PR #123 của repository này" 
   - "Định nghĩa của class User ở đâu?"
   - "Tìm các circular dependencies trong code"

**✅ Expected Results:**
- Mỗi example question auto-fill vào input và send
- Bot response intelligent, khác nhau cho mỗi loại question
- Messages xuất hiện với user/bot avatars

### **📍 Demo 3: Manual Chat Testing (2 phút)**

**Mục tiêu:** Test manual input và conversation flow

1. **Test input field:** Click vào input box
   - Should focus với blue border
   - Placeholder: "Nhập tin nhắn của bạn..."

2. **Send messages (test cả 2 cách):**
   ```
   Message 1: "Xin chào RepoChat!"
   Method: Enter key
   
   Message 2: "Bạn có thể làm gì?"
   Method: Click Send button
   
   Message 3: "Phân tích code Java cho tôi"
   Method: Enter key
   ```

3. **Observe conversation flow:**
   - User messages: Blue background, bên phải
   - Bot messages: White background, bên trái  
   - Auto-scroll to latest message
   - Loading indicator (1.5s delay)

**✅ Expected Results:**
- Smooth conversation experience
- Intelligent bot responses based on content
- Proper message formatting với timestamps

### **📍 Demo 4: Sidebar Navigation (1 phút)**

**Mục tiêu:** Test all sidebar functionality

1. **Test "➕ Chat Mới":**
   - Click button
   - New chat entry appears in history
   - Chat area clears, welcome screen returns

2. **Test "⚙️ Cài Đặt":**
   - Click button
   - Alert message: "Chức năng cài đặt sẽ được triển khai trong Task 5.3!"

3. **Test chat history:**
   - Click different history items
   - Observe active chat highlighting
   - Header title updates

**✅ Expected Results:**
- All navigation functional
- Visual feedback for interactions
- State management working properly

### **📍 Demo 5: Edge Cases & Error Handling (1 phút)**

**Mục tiêu:** Test system robustness

1. **Test empty input:**
   - Try to send empty message → Button should be disabled
   - Try whitespace-only → Should be treated as empty

2. **Test long message:**
   ```
   "Đây là một tin nhắn rất dài để test word wrapping và layout. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
   ```

3. **Test special characters:**
   ```
   "Tiếng Việt: áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệ 🤖💻🚀"
   "Code: function() { return 'hello world'; }"
   ```

**✅ Expected Results:**
- Empty input properly blocked
- Long messages display without breaking layout
- Special characters render correctly

### **📍 Demo 6: Multiple Devices & Browsers (2 phút)**

**Mục tiêu:** Cross-platform compatibility

1. **Desktop testing:**
   - Full-width browser → Check full layout
   - Half-width → Check responsive adjustments

2. **Mobile simulation:**
   - Browser dev tools → Toggle mobile view
   - Check sidebar behavior
   - Test touch interactions

3. **Multiple browsers (nếu có):**
   - Chrome: Primary testing
   - Firefox: Alternative testing
   - Safari/Edge: Cross-browser verification

**✅ Expected Results:**
- Consistent experience across browsers
- Mobile-friendly responsive design
- Touch-friendly interactions

---

## 🎯 **CRITICAL SUCCESS CRITERIA**

### **Must Pass (Core DoD):**
- [ ] ✅ Vue.js application loads without errors
- [ ] ✅ User can type and send messages
- [ ] ✅ Bot responds with meaningful content
- [ ] ✅ Messages display properly in chat area
- [ ] ✅ Basic UI elements functional

### **Should Pass (Enhanced Features):**
- [ ] ✅ Welcome screen with example questions
- [ ] ✅ Sidebar navigation functional  
- [ ] ✅ Vietnamese language throughout
- [ ] ✅ Responsive mobile layout
- [ ] ✅ Loading states and animations
- [ ] ✅ Auto-scroll and proper UX

### **Nice to Have (Polish):**
- [ ] ✅ Cross-browser compatibility
- [ ] ✅ Edge case handling
- [ ] ✅ Performance optimization
- [ ] ✅ Professional design system

---

## 🐛 **TROUBLESHOOTING GUIDE**

### **❌ "npm run dev" fails với ENOENT error**
```bash
# You're in wrong directory
pwd
cd frontend  # Make sure you're in frontend/
npm run dev
```

### **❌ Page shows "This site can't be reached"**
```bash
# Server might not be running
npm run dev
# Wait for "Local: http://localhost:3000/"
```

### **❌ Styles look broken**
```bash
# Clear browser cache
Ctrl+F5 (hard refresh)
# Or restart dev server
Ctrl+C
npm run dev
```

### **❌ Messages don't send**
```bash
# Check browser console for errors
F12 → Console tab
# Look for JavaScript errors
```

### **❌ Port 3000 already in use**
```bash
# Kill existing process
lsof -ti:3000 | xargs kill -9
# Or use different port
npm run dev -- --port 3001
```

---

## 📊 **PERFORMANCE TESTING**

### **Load Time Test:**
1. **Hard refresh page:** Ctrl+F5
2. **Measure load time:** Should be < 2 seconds
3. **Check Console:** No error messages

### **Interaction Performance:**
1. **Message send:** Should respond immediately
2. **Bot response:** Should appear within 2 seconds
3. **Scroll performance:** Should be smooth với nhiều messages

### **Memory Usage:**
1. **Open Dev Tools:** F12 → Performance tab
2. **Send 10+ messages:** Monitor memory usage
3. **Should be stable:** No memory leaks

---

## 🎉 **DEMO COMPLETION CHECKLIST**

### **Setup Success:**
- [ ] ✅ Frontend server running at localhost:3000
- [ ] ✅ No errors in terminal output
- [ ] ✅ Browser can access application

### **Core Functionality:**
- [ ] ✅ Welcome screen displays correctly
- [ ] ✅ Example questions work
- [ ] ✅ Manual message input works
- [ ] ✅ Bot responses are intelligent
- [ ] ✅ Conversation flow natural

### **UI/UX Excellence:**
- [ ] ✅ Sidebar navigation functional
- [ ] ✅ Responsive design works
- [ ] ✅ Vietnamese text renders properly
- [ ] ✅ Loading states visible
- [ ] ✅ Animations smooth

### **Edge Cases:**
- [ ] ✅ Empty input handled properly
- [ ] ✅ Long messages display correctly
- [ ] ✅ Special characters work
- [ ] ✅ Error states graceful

---

## 🚀 **NEXT STEPS AFTER DEMO**

### **If Demo Successful:**
1. **Task 5.1:** ✅ Mark as completed
2. **Task 5.2:** Ready để proceed với sidebar enhancements
3. **Backend Integration:** Prepare for real API connections

### **If Issues Found:**
1. **Document bugs:** Note specific issues
2. **Prioritize fixes:** Critical vs nice-to-have
3. **Retest:** After fixes applied

---

## 📞 **SUPPORT & FEEDBACK**

### **Demo went well?**
🎉 Congratulations! Task 5.1 Vue.js Chat Interface successfully implemented!

### **Found issues?**
📝 Please document:
- Specific steps to reproduce
- Expected vs actual behavior
- Browser/OS information
- Screenshots if helpful

### **Ready for next phase?**
🚀 Task 5.2 sẽ enhance sidebar với:
- Persistent chat history
- Improved settings modal
- Enhanced user experience

---

**Happy Demo Testing! 🎯**

*RepoChat v1.0 Frontend Team* 