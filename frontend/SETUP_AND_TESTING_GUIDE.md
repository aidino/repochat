# 🚀 SETUP & MANUAL TESTING GUIDE - RepoChat Frontend

**Hướng dẫn thiết lập môi trường và test Vue.js Chat Interface trên web browser**

---

## 📋 **YÊU CẦU HỆ THỐNG**

### **Prerequisites:**
- **Node.js:** 16+ (khuyến nghị 18+)
- **npm:** 7+ (đi kèm với Node.js)
- **Web Browser:** Chrome 90+, Firefox 88+, Safari 14+, hoặc Edge 90+
- **Terminal/Command Prompt:** Để chạy commands

### **Kiểm tra phiên bản:**
```bash
node --version    # Phải >= 16.0.0
npm --version     # Phải >= 7.0.0
```

---

## 🛠️ **SETUP MÔI TRƯỜNG**

### **Bước 1: Di chuyển vào thư mục frontend**
```bash
# Từ thư mục gốc repochat/
cd frontend

# Kiểm tra bạn đang ở đúng thư mục
pwd
# Output phải là: /path/to/repochat/frontend
```

**⚠️ QUAN TRỌNG:** Đảm bảo bạn đang ở trong thư mục `frontend/` trước khi chạy npm commands!

### **Bước 2: Cài đặt dependencies**
```bash
# Cài đặt tất cả packages cần thiết
npm install

# Verify installation thành công
npm list --depth=0
```

**Expected output:**
```
repochat-frontend@1.0.0
├── @vitejs/plugin-vue@5.2.4
├── vite@6.3.5
└── vue@3.5.16
```

### **Bước 3: Khởi chạy development server**
```bash
# Start dev server
npm run dev
```

**Expected output:**
```
> repochat-frontend@1.0.0 dev
> vite

  VITE v6.3.5  ready in 234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.x.x:3000/
  ➜  press h to show help
```

### **Bước 4: Mở trình duyệt**
1. **Tự động:** Vite có thể tự động mở browser
2. **Thủ công:** Mở browser và truy cập `http://localhost:3000`

---

## 🧪 **MANUAL TESTING TRÊN WEB BROWSER**

### **Test 1: Giao diện cơ bản**

#### **✅ Kiểm tra Layout:**
1. **Sidebar (bên trái):**
   - Logo "🤖 RepoChat" với version "v1.0"
   - Button "➕ Chat Mới" (màu xanh)
   - Button "⚙️ Cài Đặt" (màu xám)
   - Section "Lịch Sử Chat" với 3 chat mẫu

2. **Main Chat Area (bên phải):**
   - Header với title "Phân tích Spring Pet Clinic"
   - Status "🟢 Trực tuyến"
   - Welcome message area
   - Input box ở dưới cùng với button "📤 Gửi"

#### **✅ Kiểm tra Responsive:**
```bash
# Test trên different screen sizes:
# 1. Desktop (1920x1080) - Full layout
# 2. Tablet (768x1024) - Compact sidebar
# 3. Mobile (375x667) - Mobile-optimized layout
```

### **Test 2: Chat Functionality**

#### **✅ Test Welcome Screen:**
1. **Verify welcome message hiển thị:**
   ```
   👋 Chào mừng đến với RepoChat!
   Tôi là trợ lý AI phân tích repository thông minh.
   ```

2. **Test example questions (4 buttons):**
   - "Phân tích repository https://github.com/spring-projects/spring-petclinic.git"
   - "Review PR #123 của repository này"
   - "Định nghĩa của class User ở đâu?"
   - "Tìm các circular dependencies trong code"

#### **✅ Test User Input:**
1. **Click vào input field:**
   - Input field should focus với blue border
   - Placeholder text: "Nhập tin nhắn của bạn..."

2. **Type test message:**
   ```
   Test message: "Hello RepoChat!"
   ```

3. **Send message (2 cách):**
   - **Method 1:** Click button "📤 Gửi"
   - **Method 2:** Press Enter key

#### **✅ Test Message Flow:**
1. **User message xuất hiện:**
   - Message hiển thị bên phải (blue background)
   - Avatar "👤" 
   - Timestamp (format Vietnamese)

2. **Bot response (sau 1.5s):**
   - Loading state: Button shows "⏳ Đang xử lý..."
   - Bot message xuất hiện bên trái (white background)
   - Avatar "🤖"
   - Intelligent response based on message content

3. **Auto-scroll:**
   - Chat area tự động scroll xuống message mới nhất

### **Test 3: Interactive Features**

#### **✅ Test Example Questions:**
1. **Click "Phân tích repository...":**
   - Input field auto-fill với text
   - Send message automatically
   - Expect bot response về repository analysis

2. **Click "Review PR #123...":**
   - Expect bot response về PR review functionality

3. **Click "Định nghĩa của class User...":**
   - Expect bot response về class definition search

4. **Click "Tìm các circular dependencies...":**
   - Expect bot response về dependency analysis

#### **✅ Test Sidebar Navigation:**
1. **Click "➕ Chat Mới":**
   - New chat entry xuất hiện ở top của history list
   - Current chat area clears
   - Welcome screen hiển thị lại

2. **Click "⚙️ Cài Đặt":**
   - Alert message: "Chức năng cài đặt sẽ được triển khai trong Task 5.3!"

3. **Click chat history items:**
   - Active chat highlighting changes
   - Chat title updates trong header

### **Test 4: Advanced Features**

#### **✅ Test Multiple Messages:**
1. **Send series of messages:**
   ```
   Message 1: "Hello"
   Message 2: "How are you?"
   Message 3: "Analyze this repository"
   ```

2. **Verify:**
   - All messages display correctly
   - Conversation flow makes sense
   - Auto-scroll works for multiple messages

#### **✅ Test Loading States:**
1. **Send message và observe:**
   - Send button changes to "⏳ Đang xử lý..."
   - Button becomes disabled
   - After 1.5s: Button returns to "📤 Gửi"

#### **✅ Test Online Status:**
1. **Check status indicator:**
   - Green dot "🟢" + "Trực tuyến" text
   - Status updates every 5 seconds based on `navigator.onLine`

### **Test 5: Error Handling & Edge Cases**

#### **✅ Test Empty Input:**
1. **Try to send empty message:**
   - Send button should be disabled
   - No message sent

2. **Try to send whitespace-only:**
   - Should be treated as empty
   - No message sent

#### **✅ Test Long Messages:**
1. **Send very long message (500+ characters):**
   - Message should display correctly
   - Word wrap should work
   - Layout should not break

#### **✅ Test Special Characters:**
1. **Send messages với special characters:**
   ```
   Test 1: "Xin chào! 👋 🤖 💻"
   Test 2: "Code: function() { return 'hello'; }"
   Test 3: "Tiếng Việt: áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệ"
   ```

---

## 🔧 **TROUBLESHOOTING**

### **❌ Lỗi "ENOENT: no such file or directory, open package.json"**

**Nguyên nhân:** Đang chạy npm command từ sai thư mục

**Giải pháp:**
```bash
# Check current directory
pwd

# Nếu bạn đang ở /path/to/repochat thay vì /path/to/repochat/frontend
cd frontend

# Rồi chạy lại
npm run dev
```

### **❌ Port 3000 already in use**

**Giải pháp:**
```bash
# Option 1: Kill process using port 3000
lsof -ti:3000 | xargs kill -9

# Option 2: Use different port
npm run dev -- --port 3001
```

### **❌ Browser không tự động reload**

**Giải pháp:**
```bash
# Hard refresh browser
Ctrl+F5 (Windows/Linux) hoặc Cmd+Shift+R (Mac)

# Hoặc restart dev server
Ctrl+C (stop server)
npm run dev (restart)
```

### **❌ Styles không hiển thị đúng**

**Kiểm tra:**
1. Browser cache cleared
2. Dev tools Console có errors không
3. Network tab trong Dev Tools để check CSS file loading

---

## 📱 **TESTING TRÊN DIFFERENT BROWSERS**

### **Chrome (Recommended):**
```bash
# Open Chrome với specific profile (optional)
google-chrome --new-window http://localhost:3000
```

### **Firefox:**
```bash
firefox http://localhost:3000
```

### **Safari (Mac only):**
```bash
open -a Safari http://localhost:3000
```

### **Edge:**
```bash
msedge http://localhost:3000
```

---

## 🎯 **TESTING CHECKLIST**

### **Core Functionality:**
- [ ] ✅ Vue.js app loads successfully
- [ ] ✅ Welcome screen displays correctly
- [ ] ✅ User can type messages
- [ ] ✅ Send button works (click + Enter)
- [ ] ✅ Bot responds intelligently
- [ ] ✅ Messages display với proper formatting
- [ ] ✅ Auto-scroll to latest message
- [ ] ✅ Example questions functional

### **UI/UX:**
- [ ] ✅ Sidebar navigation works
- [ ] ✅ Chat history clickable
- [ ] ✅ Loading states visible
- [ ] ✅ Online status indicator
- [ ] ✅ Responsive design on mobile
- [ ] ✅ Vietnamese text displays correctly
- [ ] ✅ Animations smooth

### **Advanced:**
- [ ] ✅ Multiple messages conversation
- [ ] ✅ New chat functionality
- [ ] ✅ Empty input validation
- [ ] ✅ Long message handling
- [ ] ✅ Special characters support
- [ ] ✅ Cross-browser compatibility

---

## 🚀 **PRODUCTION BUILD TESTING**

### **Build for Production:**
```bash
# Từ thư mục frontend/
npm run build

# Kiểm tra dist/ folder được tạo
ls -la dist/
```

### **Preview Production Build:**
```bash
npm run preview
# Hoặc
npm run serve
```

### **Expected Build Output:**
```
dist/index.html                  0.59 kB │ gzip:  0.39 kB
dist/assets/index-BzANXDCg.css   7.73 kB │ gzip:  1.89 kB
dist/assets/index-DbY3JMBQ.js   67.30 kB │ gzip: 26.99 kB
✓ built in 787ms
```

---

## 🎉 **SUCCESS CRITERIA**

### **Task 5.1 được coi là thành công khi:**

1. **✅ Development Server:** `npm run dev` chạy without errors
2. **✅ Browser Access:** Application loads tại `http://localhost:3000`
3. **✅ Basic Chat:** User có thể send messages và receive bot responses
4. **✅ UI Complete:** All sidebar elements và chat interface functional
5. **✅ Vietnamese Support:** All text hiển thị correctly trong tiếng Việt
6. **✅ Responsive:** App works trên desktop và mobile browsers
7. **✅ Production Ready:** `npm run build` successful với optimized output

---

## 📞 **SUPPORT**

### **Nếu gặp issues:**

1. **Check Console:** Browser Dev Tools > Console cho error messages
2. **Check Network:** Dev Tools > Network tab cho failed requests  
3. **Clear Cache:** Hard refresh browser (Ctrl+F5)
4. **Restart Server:** Stop (`Ctrl+C`) và restart (`npm run dev`)
5. **Check Dependencies:** `npm install` lại nếu cần

### **Common Commands Reference:**
```bash
cd frontend              # Di chuyển vào frontend directory
npm install             # Cài đặt dependencies
npm run dev            # Start development server
npm run build          # Build for production
npm run preview        # Preview production build
```

---

**🎯 Happy Testing! Chúc bạn test thành công Vue.js Chat Interface! 🚀** 