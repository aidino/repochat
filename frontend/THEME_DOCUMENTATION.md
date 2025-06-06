# RepoChat Modern Chat Theme Documentation

## 🎨 Theme Overview

RepoChat v1.0 hiện đã được áp dụng **Modern Chat Theme** - một theme chuyên nghiệp được thiết kế dành riêng cho ứng dụng chat AI code assistant. Theme này lấy cảm hứng từ các ứng dụng chat hiện đại như Discord, Slack và các professional chat applications.

## 🌟 Key Features

### ✨ **Professional Dark Theme**
- **Primary Color**: `#667eea` (Modern purple-blue)
- **Background**: Deep dark tones (`#0f1419`, `#1a202c`, `#2d3748`)
- **Chat-optimized**: Specialized colors cho user/bot messages
- **Light Mode Support**: Automatic theme switching infrastructure

### 🎯 **Chat-Specific Components**
- **Message Bubbles**: Modern rounded corners với proper shadows
- **User/Bot Differentiation**: Distinct styling cho different message types
- **Avatar System**: Professional circular avatars
- **Timestamps**: Subtle time indicators
- **Input Area**: Enhanced với focus states và loading indicators

### 📱 **Responsive Design**
- **Mobile-First**: Optimized cho mobile devices
- **Breakpoints**: Tablet và desktop layouts
- **Flexible Grid**: Proper flex/grid usage

### ♿ **Accessibility**
- **Focus Management**: Proper keyboard navigation
- **Color Contrast**: WCAG compliant ratios
- **Reduced Motion**: Support cho users với motion sensitivity
- **Screen Reader**: Semantic HTML structure

## 🏗️ **Architecture**

### **CSS Custom Properties**
Theme sử dụng CSS custom properties cho consistency:

```css
:root {
  /* Primary Theme Colors */
  --color-primary: #667eea;
  --color-primary-hover: #5a67d8;
  
  /* Chat-specific colors */
  --color-chat-sidebar: #1a202c;
  --color-chat-main: #2d3748;
  --color-message-user: #667eea;
  --color-message-bot: #4a5568;
  
  /* Status Colors */
  --color-online: #48bb78;
  --color-offline: #718096;
  --color-typing: #ed8936;
}
```

### **Utility Classes System**
Comprehensive utility classes (similar to Tailwind CSS):

```css
/* Layout */
.flex, .items-center, .justify-between

/* Spacing */
.gap-1, .gap-2, .p-4, .m-2

/* Typography */
.text-lg, .font-semibold, .text-primary

/* Colors */
.bg-surface, .text-secondary

/* Responsive */
.sm:hidden, .md:flex, .lg:block
```

## 🎨 **Design Tokens**

### **Color Palette**
| Token | Value | Usage |
|-------|--------|--------|
| `--color-primary` | `#667eea` | Primary buttons, links, user messages |
| `--color-background` | `#0f1419` | Main app background |
| `--color-surface` | `#2d3748` | Cards, modals, elevated surfaces |
| `--color-text-primary` | `#f7fafc` | Primary text content |
| `--color-text-secondary` | `#e2e8f0` | Secondary text, labels |
| `--color-success` | `#48bb78` | Success states, online indicators |
| `--color-error` | `#f56565` | Error states, warnings |

### **Typography Scale**
| Size | Token | Value | Usage |
|------|--------|--------|--------|
| XS | `--font-size-xs` | `0.75rem` | Timestamps, small labels |
| SM | `--font-size-sm` | `0.875rem` | Secondary text |
| Base | `--font-size-base` | `1rem` | Body text, messages |
| LG | `--font-size-lg` | `1.125rem` | Headings, titles |
| XL | `--font-size-xl` | `1.25rem` | Large headings |
| 2XL | `--font-size-2xl` | `1.5rem` | Page titles |

### **Spacing Scale**
| Size | Value | Usage |
|------|--------|--------|
| `--space-1` | `0.25rem` | Fine adjustments |
| `--space-2` | `0.5rem` | Small gaps |
| `--space-3` | `0.75rem` | Standard gaps |
| `--space-4` | `1rem` | Component padding |
| `--space-6` | `1.5rem` | Section spacing |
| `--space-8` | `2rem` | Large spacing |

## 🧩 **Component Structure**

### **App Container**
```css
.app-container {
  display: flex;
  width: 100%;
  height: 100vh;
  background: var(--color-background);
  overflow: hidden;
}
```

### **Sidebar**
```css
.sidebar {
  width: 320px;
  background: var(--color-chat-sidebar);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}
```

### **Chat Container**
```css
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-chat-main);
}
```

### **Message Bubbles**
```css
.message-text {
  background: var(--color-message-bot);
  color: var(--color-message-bot-text);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  max-width: 70%;
}

.user-message .message-text {
  background: var(--color-message-user);
  color: var(--color-message-user-text);
}
```

## 🎬 **Animations**

### **Smooth Transitions**
```css
/* Transition Variables */
--transition-fast: 0.15s ease;
--transition-normal: 0.3s ease;
--transition-slow: 0.5s ease;

/* Usage */
.message {
  transition: var(--transition-fast);
}
```

### **Keyframe Animations**
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### **Animation Classes**
- `.animate-fade-in`: Fade in effect
- `.animate-slide-in-up`: Slide up animation
- `.animate-pulse`: Pulsing effect cho loading states

## 📱 **Responsive Breakpoints**

```css
/* Mobile First Approach */
@media (max-width: 640px) {
  .sm\:hidden { display: none; }
  .sm\:flex { display: flex; }
}

@media (max-width: 768px) {
  .md\:hidden { display: none; }
  .md\:flex-col { flex-direction: column; }
}

@media (max-width: 1024px) {
  .lg\:hidden { display: none; }
  .lg\:block { display: block; }
}
```

## 🌙 **Theme Switching**

### **Light Mode Support**
```css
[data-theme="light"] {
  --color-background: #ffffff;
  --color-surface: #ffffff;
  --color-text-primary: #1a202c;
  --color-border: #e2e8f0;
}
```

### **Implementation**
```javascript
// Toggle theme
document.documentElement.setAttribute('data-theme', 'light');
document.documentElement.setAttribute('data-theme', 'dark');
```

## 🎯 **Usage Examples**

### **Creating a Message**
```vue
<div class="message user-message animate-slide-in-up">
  <div class="message-avatar">
    <span>👤</span>
  </div>
  <div class="message-content">
    <div class="message-text">
      Hello, this is a user message!
    </div>
    <div class="message-time">
      14:30
    </div>
  </div>
</div>
```

### **Input Area**
```vue
<div class="input-area">
  <div class="input-container">
    <textarea
      class="message-input"
      placeholder="Type your message..."
    ></textarea>
    <button class="send-btn">
      <span class="icon">📤</span>
      Send
    </button>
  </div>
</div>
```

### **Status Indicators**
```vue
<div class="chat-status">
  <div class="status-dot online"></div>
  <span class="status-text">Online</span>
</div>
```

## 🔮 **Future Enhancements**

### **Ready-to-Implement Features**
1. **Theme Switching**: Infrastructure đã sẵn sàng
2. **Message Types**: File uploads, code blocks, images
3. **Emoji Picker**: Integration points prepared
4. **Typing Indicators**: Animation classes available
5. **Message Reactions**: Hover states ready

### **Customization Options**
1. **Custom Color Schemes**: Easy CSS variable overrides
2. **Typography Variants**: Font family switching
3. **Component Sizes**: Compact/comfortable modes
4. **Animation Preferences**: Motion reduction support

## 📊 **Performance**

### **Optimized CSS**
- **CSS Variables**: Efficient theme switching
- **Utility Classes**: Reduced CSS bundle size
- **Modern Properties**: Hardware acceleration
- **Minimal Reflows**: Optimized layout changes

### **Browser Support**
- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## 🚀 **Getting Started**

### **Installation**
Theme được tích hợp sẵn trong `frontend/src/styles/main.css`

### **Development**
```bash
cd frontend
npm run dev
# Visit http://localhost:3000
```

### **Customization**
1. Modify CSS custom properties trong `:root`
2. Override specific component styles
3. Add new utility classes nếu cần
4. Test trong both light và dark modes

## 📝 **Migration Guide**

### **From Previous Theme**
1. **CSS Classes**: Đã được migrate sang utility system
2. **Color Variables**: Updated với new naming convention
3. **Component Structure**: Enhanced với better semantics
4. **Animation**: Upgraded với smoother transitions

### **Breaking Changes**
- Old gradient backgrounds removed
- Updated color variable names
- Enhanced component class structure
- New responsive utility classes

## 🎨 **Design System Integration**

Theme này tương thích với:
- **Tailwind CSS**: Similar utility approach
- **Material Design**: Color contrast guidelines
- **Apple Design**: Typography và spacing principles
- **Google Design**: Accessibility standards

---

**Theme Version**: 1.0  
**Last Updated**: 2025-01-03  
**Compatibility**: Vue.js 3+, Modern Browsers  
**License**: MIT 