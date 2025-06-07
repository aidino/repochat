"""
Memory Service for Conversation Management using mem0ai.

This service manages conversation memory, context, and user preferences
to provide personalized and contextual chat experiences.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from mem0 import Memory
from mem0.configs.base import MemoryConfig

try:
    from src.shared.utils.logging_config import setup_logging, log_function_entry, log_function_exit
except ImportError:
    try:
        from shared.utils.logging_config import setup_logging, log_function_entry, log_function_exit
    except ImportError:
        # Fallback to basic logging
        import logging
        def setup_logging(name): return logging.getLogger(name)
        def log_function_entry(logger, func_name, **kwargs): logger.debug(f"ENTER {func_name}")
        def log_function_exit(logger, func_name, **kwargs): logger.debug(f"EXIT {func_name}")

logger = setup_logging(__name__)


class ConversationMemoryService:
    """
    Service để quản lý memory cuộc hội thoại sử dụng mem0ai.
    
    Features:
    - Lưu trữ và truy xuất memory từ cuộc hội thoại
    - Quản lý context cá nhân hóa cho từng user
    - Tích hợp với user preferences và settings
    - Tracking conversation history và patterns
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Memory Service.
        
        Args:
            config: Configuration for mem0ai (optional)
        """
        log_function_entry(logger, "ConversationMemoryService.__init__")
        
        self.memory_config = config or self._get_default_config()
        
        try:
            # Initialize mem0 Memory với config
            if self.memory_config:
                # Create MemoryConfig object from dict
                memory_config_obj = MemoryConfig(**self.memory_config)
                self.memory = Memory(config=memory_config_obj)
            else:
                # Use default config
                self.memory = Memory()
            logger.info("Memory service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize memory service: {e}")
            # Fallback: create simple in-memory storage
            self.memory = None
            self._fallback_memory = {}
            logger.warning("Using fallback in-memory storage")
        
        log_function_exit(logger, "ConversationMemoryService.__init__")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Lấy default configuration cho mem0ai.
        
        Returns:
            Default config dictionary (empty for now to use fallback)
        """
        # For now, return empty config to use fallback storage
        # This ensures memory functionality works even without mem0ai setup
        return {}
    
    def add_conversation_memory(
        self, 
        user_id: str, 
        session_id: str,
        user_message: str, 
        bot_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Thêm memory từ cuộc hội thoại vào storage.
        
        Args:
            user_id: ID của user
            session_id: ID của session
            user_message: Tin nhắn từ user
            bot_response: Response từ bot
            context: Additional context information
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        log_function_entry(logger, "add_conversation_memory", 
                          user_id=user_id, session_id=session_id)
        
        try:
            if self.memory:
                # Tạo conversation context
                conversation_data = {
                    "user_message": user_message,
                    "bot_response": bot_response,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "context": context or {}
                }
                
                # Add memory với user_id để phân biệt memory giữa các users
                memory_text = f"User: {user_message}\nBot: {bot_response}"
                
                result = self.memory.add(
                    memory_text,
                    user_id=user_id,
                    metadata=conversation_data
                )
                
                logger.info(f"Added conversation memory for user {user_id}, session {session_id}")
                log_function_exit(logger, "add_conversation_memory", result="success")
                return True
                
            else:
                # Fallback storage
                if user_id not in self._fallback_memory:
                    self._fallback_memory[user_id] = []
                
                self._fallback_memory[user_id].append({
                    "user_message": user_message,
                    "bot_response": bot_response,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "context": context or {}
                })
                
                logger.info(f"Added conversation memory to fallback storage for user {user_id}")
                log_function_exit(logger, "add_conversation_memory", result="fallback_success")
                return True
                
        except Exception as e:
            logger.error(f"Error adding conversation memory: {e}", exc_info=True)
            log_function_exit(logger, "add_conversation_memory", result="error")
            return False
    
    def get_relevant_memories(
        self, 
        user_id: str, 
        current_message: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Truy xuất memories liên quan đến message hiện tại.
        
        Args:
            user_id: ID của user
            current_message: Message hiện tại để tìm relevant memories
            limit: Số lượng memories tối đa trả về
            
        Returns:
            List of relevant memories
        """
        log_function_entry(logger, "get_relevant_memories", 
                          user_id=user_id, limit=limit)
        
        try:
            if self.memory:
                # Search memories liên quan
                memories = self.memory.search(
                    query=current_message,
                    user_id=user_id,
                    limit=limit
                )
                
                logger.info(f"Retrieved {len(memories)} relevant memories for user {user_id}")
                log_function_exit(logger, "get_relevant_memories", 
                                result=f"found_{len(memories)}_memories")
                return memories
                
            else:
                # Fallback: return recent conversations
                user_memories = self._fallback_memory.get(user_id, [])
                recent_memories = user_memories[-limit:] if user_memories else []
                
                logger.info(f"Retrieved {len(recent_memories)} recent memories from fallback for user {user_id}")
                log_function_exit(logger, "get_relevant_memories", 
                                result=f"fallback_{len(recent_memories)}_memories")
                return recent_memories
                
        except Exception as e:
            logger.error(f"Error retrieving relevant memories: {e}", exc_info=True)
            log_function_exit(logger, "get_relevant_memories", result="error")
            return []
    
    def get_user_memories(
        self, 
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Lấy tất cả memories của một user.
        
        Args:
            user_id: ID của user
            limit: Số lượng memories tối đa
            
        Returns:
            List of user memories
        """
        log_function_entry(logger, "get_user_memories", user_id=user_id, limit=limit)
        
        try:
            if self.memory:
                memories = self.memory.get_all(user_id=user_id, limit=limit)
                
                logger.info(f"Retrieved {len(memories)} total memories for user {user_id}")
                log_function_exit(logger, "get_user_memories", result="success")
                return memories
                
            else:
                # Fallback storage
                user_memories = self._fallback_memory.get(user_id, [])
                limited_memories = user_memories[-limit:] if user_memories else []
                
                logger.info(f"Retrieved {len(limited_memories)} memories from fallback for user {user_id}")
                log_function_exit(logger, "get_user_memories", result="fallback_success")
                return limited_memories
                
        except Exception as e:
            logger.error(f"Error retrieving user memories: {e}", exc_info=True)
            log_function_exit(logger, "get_user_memories", result="error")
            return []
    
    def delete_user_memories(self, user_id: str) -> bool:
        """
        Xóa tất cả memories của một user.
        
        Args:
            user_id: ID của user
            
        Returns:
            True nếu thành công
        """
        log_function_entry(logger, "delete_user_memories", user_id=user_id)
        
        try:
            if self.memory:
                # Delete all memories for user
                result = self.memory.delete_all(user_id=user_id)
                
                logger.info(f"Deleted all memories for user {user_id}")
                log_function_exit(logger, "delete_user_memories", result="success")
                return True
                
            else:
                # Fallback storage
                if user_id in self._fallback_memory:
                    del self._fallback_memory[user_id]
                
                logger.info(f"Deleted fallback memories for user {user_id}")
                log_function_exit(logger, "delete_user_memories", result="fallback_success")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting user memories: {e}", exc_info=True)
            log_function_exit(logger, "delete_user_memories", result="error")
            return False
    
    def update_memory(
        self, 
        memory_id: str, 
        new_data: str, 
        user_id: str
    ) -> bool:
        """
        Cập nhật một memory cụ thể.
        
        Args:
            memory_id: ID của memory cần update
            new_data: Dữ liệu mới
            user_id: ID của user
            
        Returns:
            True nếu thành công
        """
        log_function_entry(logger, "update_memory", 
                          memory_id=memory_id, user_id=user_id)
        
        try:
            if self.memory:
                result = self.memory.update(memory_id=memory_id, data=new_data)
                
                logger.info(f"Updated memory {memory_id} for user {user_id}")
                log_function_exit(logger, "update_memory", result="success")
                return True
                
            else:
                logger.warning("Memory update not supported in fallback mode")
                log_function_exit(logger, "update_memory", result="not_supported")
                return False
                
        except Exception as e:
            logger.error(f"Error updating memory: {e}", exc_info=True)
            log_function_exit(logger, "update_memory", result="error")
            return False
    
    def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Lấy thống kê về memories của user.
        
        Args:
            user_id: ID của user
            
        Returns:
            Dictionary chứa thống kê
        """
        try:
            memories = self.get_user_memories(user_id)
            
            # Safe access to last memory
            last_memory_date = None
            if memories and len(memories) > 0:
                try:
                    # Handle different memory formats
                    if isinstance(memories, list):
                        last_memory = memories[-1]
                    elif isinstance(memories, dict) and 'results' in memories:
                        results = memories['results']
                        last_memory = results[-1] if results else None
                    else:
                        last_memory = None
                    
                    if isinstance(last_memory, dict):
                        # Try different timestamp fields
                        last_memory_date = (
                            last_memory.get("timestamp") or 
                            last_memory.get("created_at") or
                            (last_memory.get("metadata", {}).get("timestamp"))
                        )
                except (KeyError, IndexError, TypeError) as e:
                    logger.warning(f"Could not extract last memory date: {e}")
            
            return {
                "total_memories": len(memories),
                "memory_service_active": self.memory is not None,
                "last_memory_date": last_memory_date,
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}", exc_info=True)
            return {
                "total_memories": 0,
                "memory_service_active": False,
                "error": str(e),
                "user_id": user_id
            }


# Global memory service instance
memory_service = ConversationMemoryService() 