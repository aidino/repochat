# RepoChat Frontend Components

## Sidebar.vue

Enhanced sidebar component for RepoChat application with advanced chat history management.

### Features

#### Core Functionality
- **New Chat**: Create new chat sessions
- **Settings Access**: Navigate to application settings
- **Chat History**: Display and manage chat history with rich metadata

#### Advanced Features
- **Search**: Real-time search through chat history (title, message content, tags)
- **Favorites**: Mark/unmark chats as favorites
- **Context Menu**: Right-click actions (rename, duplicate, export, delete)
- **Pagination**: Load more history on demand
- **Recent Indicators**: Visual indicators for recent chats (within 24 hours)
- **Statistics**: Display total chats and message counts

#### User Experience
- **Responsive Design**: Mobile and desktop optimization
- **Loading States**: Visual feedback for async operations
- **Empty States**: Helpful messages when no data is available
- **Animations**: Smooth transitions and micro-interactions

### Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `currentChatId` | Number/String | Yes | - | ID of currently active chat |
| `isLoading` | Boolean | No | `false` | Loading state for disabling interactions |

### Events

| Event | Payload | Description |
|-------|---------|-------------|
| `new-chat` | - | User clicked "New Chat" button |
| `open-settings` | - | User clicked "Settings" button |
| `select-chat` | `chatId` | User selected a chat from history |
| `delete-chat` | `chatId` | User deleted a chat |
| `rename-chat` | `{id, title}` | User renamed a chat |
| `duplicate-chat` | `chatObject` | User duplicated a chat |
| `export-chat` | `chatObject` | User exported a chat |

### Usage Example

```vue
<template>
  <Sidebar 
    :currentChatId="currentChatId"
    :isLoading="isLoading"
    @new-chat="handleNewChat"
    @open-settings="handleSettings"
    @select-chat="handleSelectChat"
    @delete-chat="handleDeleteChat"
    @rename-chat="handleRenameChat"
    @duplicate-chat="handleDuplicateChat"
    @export-chat="handleExportChat"
  />
</template>

<script>
import Sidebar from './components/Sidebar.vue'

export default {
  components: {
    Sidebar
  },
  data() {
    return {
      currentChatId: 1,
      isLoading: false
    }
  },
  methods: {
    handleNewChat() {
      // Create new chat logic
    },
    handleSettings() {
      // Open settings logic
    },
    handleSelectChat(chatId) {
      // Switch to selected chat
      this.currentChatId = chatId
    },
    handleDeleteChat(chatId) {
      // Delete chat logic
    },
    handleRenameChat(data) {
      // Rename chat logic
      console.log(`Chat ${data.id} renamed to: ${data.title}`)
    },
    handleDuplicateChat(chat) {
      // Duplicate chat logic
    },
    handleExportChat(chat) {
      // Export chat logic
    }
  }
}
</script>
```

### Data Structure

The component expects chat history items with the following structure:

```javascript
{
  id: 1,                              // Unique identifier
  title: 'Chat Title',                // Display title
  date: new Date(),                   // Creation/last updated date
  messageCount: 15,                   // Number of messages (optional)
  lastMessage: 'Last message text',   // Preview of last message (optional)
  isFavorite: true,                   // Favorite status
  tags: ['tag1', 'tag2']             // Search tags (optional)
}
```

### Styling

The component uses CSS custom properties for theming:

```css
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-tertiary: #94a3b8;
  --primary-color: #4f46e5;
  --primary-dark: #3730a3;
  --accent-color: #06b6d4;
  --border-color: #e2e8f0;
  --error-color: #ef4444;
  --error-bg: #fef2f2;
  --success-color: #10b981;
}
```

### Responsive Behavior

- **Desktop (>768px)**: Full width sidebar (300px)
- **Tablet (768px)**: Reduced width (280px) 
- **Mobile (<480px)**: Full-screen overlay

### Accessibility

- Proper ARIA labels and roles
- Keyboard navigation support
- Focus management for context menus
- Screen reader friendly text

### Testing

Comprehensive test suite covering:
- Component structure and rendering
- User interactions and events
- Search functionality
- Context menu operations
- Edge cases and error handling

Run tests with:
```bash
npm run test
npm run test:ui
npm run test:coverage
```

### Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Performance Considerations

- Virtual scrolling for large chat history lists (future enhancement)
- Debounced search to prevent excessive filtering
- Lazy loading of chat metadata
- Efficient event handling with proper cleanup

### Future Enhancements

- Drag and drop chat reordering
- Chat categories/folders
- Bulk operations (multi-select)
- Keyboard shortcuts
- Custom themes
- Export/import functionality
- Chat synchronization across devices 