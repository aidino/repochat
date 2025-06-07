"""
Unit tests for Memory Service.

Tests bao gồm:
1. Memory service initialization
2. Adding conversation memories
3. Retrieving memories
4. Searching relevant memories
5. Memory persistence
6. Error handling
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.memory_service import ConversationMemoryService


class TestConversationMemoryService:
    """Test cases for ConversationMemoryService."""
    
    def setup_method(self):
        """Setup test environment."""
        self.test_user_id = "test_user_123"
        self.test_session_id = "test_session_456"
        
    @patch('services.memory_service.Memory')
    def test_memory_service_initialization_success(self, mock_memory_class):
        """Test successful memory service initialization."""
        # Setup
        mock_memory_instance = Mock()
        mock_memory_class.return_value = mock_memory_instance
        
        # Execute
        service = ConversationMemoryService()
        
        # Verify
        assert service.memory is not None
        assert service.memory == mock_memory_instance
        mock_memory_class.assert_called_once()
    
    @patch('services.memory_service.Memory')
    def test_memory_service_initialization_failure(self, mock_memory_class):
        """Test fallback when memory service initialization fails."""
        # Setup
        mock_memory_class.side_effect = Exception("Memory initialization failed")
        
        # Execute
        service = ConversationMemoryService()
        
        # Verify
        assert service.memory is None
        assert hasattr(service, '_fallback_memory')
        assert service._fallback_memory == {}
    
    def test_add_conversation_memory_fallback(self):
        """Test adding conversation memory with fallback storage."""
        # Setup
        service = ConversationMemoryService()
        service.memory = None  # Force fallback mode
        service._fallback_memory = {}
        
        # Execute
        result = service.add_conversation_memory(
            user_id=self.test_user_id,
            session_id=self.test_session_id,
            user_message="Test user message",
            bot_response="Test bot response",
            context={"intent": "test", "confidence": 0.9}
        )
        
        # Verify
        assert result is True
        assert self.test_user_id in service._fallback_memory
        assert len(service._fallback_memory[self.test_user_id]) == 1
        
        memory_entry = service._fallback_memory[self.test_user_id][0]
        assert memory_entry["user_message"] == "Test user message"
        assert memory_entry["bot_response"] == "Test bot response"
        assert memory_entry["session_id"] == self.test_session_id
        assert memory_entry["context"]["intent"] == "test"
    
    @patch('services.memory_service.Memory')
    def test_add_conversation_memory_with_mem0(self, mock_memory_class):
        """Test adding conversation memory with mem0ai."""
        # Setup
        mock_memory_instance = Mock()
        mock_memory_class.return_value = mock_memory_instance
        mock_memory_instance.add.return_value = {"id": "memory_123"}
        
        service = ConversationMemoryService()
        
        # Execute
        result = service.add_conversation_memory(
            user_id=self.test_user_id,
            session_id=self.test_session_id,
            user_message="Test user message",
            bot_response="Test bot response"
        )
        
        # Verify
        assert result is True
        mock_memory_instance.add.assert_called_once()
        
        # Check call arguments
        args, kwargs = mock_memory_instance.add.call_args
        assert self.test_user_id in kwargs.get('user_id', '')
        assert "Test user message" in args[0]
        assert "Test bot response" in args[0]
    
    def test_get_user_memories_fallback(self):
        """Test retrieving user memories with fallback storage."""
        # Setup
        service = ConversationMemoryService()
        service.memory = None  # Force fallback mode
        service._fallback_memory = {
            self.test_user_id: [
                {
                    "user_message": "Message 1",
                    "bot_response": "Response 1",
                    "timestamp": "2025-06-07T10:00:00",
                    "session_id": "session_1"
                },
                {
                    "user_message": "Message 2", 
                    "bot_response": "Response 2",
                    "timestamp": "2025-06-07T11:00:00",
                    "session_id": "session_2"
                }
            ]
        }
        
        # Execute
        memories = service.get_user_memories(self.test_user_id, limit=5)
        
        # Verify
        assert len(memories) == 2
        assert memories[0]["user_message"] == "Message 1"
        assert memories[1]["user_message"] == "Message 2"
    
    def test_get_user_memories_with_limit(self):
        """Test retrieving user memories with limit."""
        # Setup
        service = ConversationMemoryService()
        service.memory = None  # Force fallback mode
        service._fallback_memory = {
            self.test_user_id: [
                {"user_message": f"Message {i}", "bot_response": f"Response {i}"} 
                for i in range(10)
            ]
        }
        
        # Execute
        memories = service.get_user_memories(self.test_user_id, limit=3)
        
        # Verify
        assert len(memories) == 3
        # Should return last 3 memories
        assert memories[0]["user_message"] == "Message 7"
        assert memories[2]["user_message"] == "Message 9"
    
    @patch('services.memory_service.Memory')
    def test_get_relevant_memories_with_mem0(self, mock_memory_class):
        """Test searching relevant memories with mem0ai."""
        # Setup
        mock_memory_instance = Mock()
        mock_memory_class.return_value = mock_memory_instance
        mock_memory_instance.search.return_value = [
            {"memory": "Relevant memory 1", "score": 0.9},
            {"memory": "Relevant memory 2", "score": 0.8}
        ]
        
        service = ConversationMemoryService()
        
        # Execute
        memories = service.get_relevant_memories(
            user_id=self.test_user_id,
            current_message="Search query",
            limit=5
        )
        
        # Verify
        assert len(memories) == 2
        mock_memory_instance.search.assert_called_once_with(
            query="Search query",
            user_id=self.test_user_id,
            limit=5
        )
    
    def test_get_relevant_memories_fallback(self):
        """Test searching relevant memories with fallback storage."""
        # Setup
        service = ConversationMemoryService()
        service.memory = None  # Force fallback mode
        service._fallback_memory = {
            self.test_user_id: [
                {"user_message": "Python programming", "bot_response": "Python is great"},
                {"user_message": "Web development", "bot_response": "Use frameworks"},
                {"user_message": "Machine learning", "bot_response": "Try TensorFlow"}
            ]
        }
        
        # Execute
        memories = service.get_relevant_memories(
            user_id=self.test_user_id,
            current_message="How to learn Python?",
            limit=2
        )
        
        # Verify (fallback returns recent memories)
        assert len(memories) == 2
        assert memories[0]["user_message"] == "Web development"
        assert memories[1]["user_message"] == "Machine learning"
    
    def test_delete_user_memories_fallback(self):
        """Test deleting user memories with fallback storage."""
        # Setup
        service = ConversationMemoryService()
        service.memory = None  # Force fallback mode
        service._fallback_memory = {
            self.test_user_id: [{"user_message": "Test", "bot_response": "Response"}],
            "other_user": [{"user_message": "Other", "bot_response": "Other response"}]
        }
        
        # Execute
        result = service.delete_user_memories(self.test_user_id)
        
        # Verify
        assert result is True
        assert self.test_user_id not in service._fallback_memory
        assert "other_user" in service._fallback_memory  # Other user's memories preserved
    
    @patch('services.memory_service.Memory')
    def test_delete_user_memories_with_mem0(self, mock_memory_class):
        """Test deleting user memories with mem0ai."""
        # Setup
        mock_memory_instance = Mock()
        mock_memory_class.return_value = mock_memory_instance
        mock_memory_instance.delete_all.return_value = True
        
        service = ConversationMemoryService()
        
        # Execute
        result = service.delete_user_memories(self.test_user_id)
        
        # Verify
        assert result is True
        mock_memory_instance.delete_all.assert_called_once_with(user_id=self.test_user_id)
    
    def test_get_memory_stats(self):
        """Test getting memory statistics."""
        # Setup
        service = ConversationMemoryService()
        service.memory = None  # Force fallback mode
        service._fallback_memory = {
            self.test_user_id: [
                {
                    "user_message": "Test",
                    "bot_response": "Response",
                    "timestamp": "2025-06-07T10:00:00"
                }
            ]
        }
        
        # Execute
        stats = service.get_memory_stats(self.test_user_id)
        
        # Verify
        assert stats["total_memories"] == 1
        assert stats["memory_service_active"] is False
        assert stats["last_memory_date"] == "2025-06-07T10:00:00"
        assert stats["user_id"] == self.test_user_id
    
    def test_get_memory_stats_no_memories(self):
        """Test getting memory statistics for user with no memories."""
        # Setup
        service = ConversationMemoryService()
        service.memory = None  # Force fallback mode
        service._fallback_memory = {}
        
        # Execute
        stats = service.get_memory_stats(self.test_user_id)
        
        # Verify
        assert stats["total_memories"] == 0
        assert stats["memory_service_active"] is False
        assert stats["last_memory_date"] is None
        assert stats["user_id"] == self.test_user_id
    
    @patch('services.memory_service.Memory')
    def test_update_memory_with_mem0(self, mock_memory_class):
        """Test updating memory with mem0ai."""
        # Setup
        mock_memory_instance = Mock()
        mock_memory_class.return_value = mock_memory_instance
        mock_memory_instance.update.return_value = True
        
        service = ConversationMemoryService()
        
        # Execute
        result = service.update_memory("memory_123", "Updated data", self.test_user_id)
        
        # Verify
        assert result is True
        mock_memory_instance.update.assert_called_once_with(
            memory_id="memory_123",
            data="Updated data"
        )
    
    def test_update_memory_fallback_not_supported(self):
        """Test update memory with fallback storage (not supported)."""
        # Setup
        service = ConversationMemoryService()
        service.memory = None  # Force fallback mode
        
        # Execute
        result = service.update_memory("memory_123", "Updated data", self.test_user_id)
        
        # Verify
        assert result is False
    
    def test_error_handling_in_add_memory(self):
        """Test error handling when adding memory fails."""
        # Setup
        service = ConversationMemoryService()
        service.memory = None  # Force fallback mode
        service._fallback_memory = None  # Force error
        
        # Execute
        result = service.add_conversation_memory(
            user_id=self.test_user_id,
            session_id=self.test_session_id,
            user_message="Test",
            bot_response="Response"
        )
        
        # Verify
        assert result is False
    
    def test_error_handling_in_get_memories(self):
        """Test error handling when retrieving memories fails."""
        # Setup
        service = ConversationMemoryService()
        service.memory = None  # Force fallback mode
        service._fallback_memory = None  # Force error
        
        # Execute
        memories = service.get_user_memories(self.test_user_id)
        
        # Verify
        assert memories == []
    
    def test_error_handling_in_get_stats(self):
        """Test error handling when getting stats fails."""
        # Setup
        service = ConversationMemoryService()
        
        # Mock get_user_memories to raise exception
        with patch.object(service, 'get_user_memories', side_effect=Exception("Test error")):
            # Execute
            stats = service.get_memory_stats(self.test_user_id)
            
            # Verify
            assert stats["total_memories"] == 0
            assert stats["memory_service_active"] is False
            assert "error" in stats
            assert stats["user_id"] == self.test_user_id


class TestMemoryServiceConfiguration:
    """Test memory service configuration."""
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key_123"})
    def test_default_config_with_api_key(self):
        """Test default configuration when OpenAI API key is available."""
        service = ConversationMemoryService()
        config = service._get_default_config()
        
        assert "llm" in config
        assert "embedder" in config 
        assert "vector_store" in config
        assert config["llm"]["config"]["api_key"] == "test_key_123"
        assert config["embedder"]["config"]["api_key"] == "test_key_123"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_default_config_without_api_key(self):
        """Test default configuration when no OpenAI API key."""
        service = ConversationMemoryService()
        config = service._get_default_config()
        
        assert config == {}
    
    def test_custom_config(self):
        """Test memory service with custom configuration."""
        custom_config = {
            "llm": {"provider": "custom", "config": {"model": "custom-model"}},
            "vector_store": {"provider": "custom"}
        }
        
        service = ConversationMemoryService(config=custom_config)
        assert service.memory_config == custom_config


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 