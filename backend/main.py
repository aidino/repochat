"""
RepoChat v1.0 - Main FastAPI Application

Entry point for the RepoChat backend service with comprehensive logging
and health monitoring for Docker development environment.
"""

import os
import sys
import time
import json
import re
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional, Generator
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
import uvicorn

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.shared.utils.logging_config import (
    get_logger, 
    log_function_entry, 
    log_function_exit,
    log_performance_metric
)
from src.shared.models.task_definition import TaskDefinition
from src.orchestrator.orchestrator_agent import OrchestratorAgent

# Import LLM-based components for intelligent conversation
from src.teams.interaction_tasking.user_intent_parser_agent import UserIntentParserAgent
from src.teams.interaction_tasking.dialog_manager_agent import DialogManagerAgent

# Import user settings and API key management components
from services.user_settings_service import UserSettingsService
from shared.models.user_settings import APIKeyRequest, APIKeyProvider, UserSettingsRequest


# Custom JSON encoder for datetime objects
def custom_jsonable_encoder(obj):
    """Custom encoder that handles datetime objects recursively."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: custom_jsonable_encoder(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [custom_jsonable_encoder(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Handle custom objects by converting to dict first
        return custom_jsonable_encoder(obj.__dict__)
    else:
        return obj


# Global variables for application state
app_logger = get_logger("main", extra_context={'service': 'fastapi'})
orchestrator: OrchestratorAgent = None
app_start_time = datetime.now()

# Q&A conversation components (will be initialized after class definitions)
session_manager = None
dialog_manager = None
streaming_dialog_manager = None

# Initialize user settings service
user_settings_service = UserSettingsService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager with comprehensive logging.
    Handles startup and shutdown procedures.
    """
    global orchestrator, session_manager, dialog_manager, streaming_dialog_manager
    startup_time = time.time()
    
    app_logger.info("Starting RepoChat FastAPI application", extra={
        'extra_data': {
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'log_level': os.getenv('LOG_LEVEL', 'DEBUG'),
            'neo4j_uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            'startup_time': datetime.now().isoformat()
        }
    })
    
    try:
        # Initialize Orchestrator Agent
        app_logger.info("Initializing Orchestrator Agent...")
        orchestrator = OrchestratorAgent()
        
        # Initialize Q&A conversation components with LLM integration
        app_logger.info("Initializing LLM-powered conversation components...")
        session_manager = ChatSessionManager()
        dialog_manager = SimplifiedLLMDialogManager(session_manager)  # ✅ LLM-powered dialog system
        streaming_dialog_manager = StreamingLLMDialogManager(session_manager)  # ✅ Streaming dialog system
        
        startup_duration = time.time() - startup_time
        log_performance_metric(
            app_logger,
            "application_startup_time",
            startup_duration * 1000,
            "ms",
            environment=os.getenv('ENVIRONMENT', 'development')
        )
        
        app_logger.info("RepoChat application started successfully", extra={
            'extra_data': {
                'startup_duration_ms': startup_duration * 1000,
                'orchestrator_id': orchestrator.agent_id,
                'status': 'ready'
            }
        })
        
        yield
        
    except Exception as e:
        app_logger.error(f"Failed to start application: {e}", exc_info=True)
        raise
    finally:
        # Shutdown procedures
        shutdown_time = time.time()
        app_logger.info("Shutting down RepoChat application...")
        
        if orchestrator:
            try:
                orchestrator.shutdown()
                app_logger.info("Orchestrator Agent shutdown completed")
            except Exception as e:
                app_logger.error(f"Error during orchestrator shutdown: {e}", exc_info=True)
        
        shutdown_duration = time.time() - shutdown_time
        app_logger.info("Application shutdown completed", extra={
            'extra_data': {
                'shutdown_duration_ms': shutdown_duration * 1000,
                'total_uptime_seconds': (datetime.now() - app_start_time).total_seconds()
            }
        })


# Create FastAPI application
app = FastAPI(
    title="RepoChat API",
    description="AI-powered repository analysis and code review assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_orchestrator() -> OrchestratorAgent:
    """
    Dependency to get the orchestrator agent instance.
    
    Returns:
        OrchestratorAgent: The global orchestrator instance
        
    Raises:
        HTTPException: If orchestrator is not available
    """
    if orchestrator is None:
        app_logger.error("Orchestrator agent is not available")
        raise HTTPException(
            status_code=503, 
            detail="Orchestrator service is not available"
        )
    return orchestrator


@app.get("/")
async def root():
    """
    Root endpoint with basic service information.
    """
    start_time = time.time()
    log_function_entry(app_logger, "root")
    
    uptime = datetime.now() - app_start_time
    
    response = {
        "service": "RepoChat API",
        "version": "1.0.0",
        "status": "healthy",
        "uptime_seconds": uptime.total_seconds(),
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }
    
    execution_time = time.time() - start_time
    log_function_exit(app_logger, "root", result="success", execution_time=execution_time)
    
    return response


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint for Docker monitoring.
    """
    start_time = time.time()
    log_function_entry(app_logger, "health_check")
    
    try:
        # Check orchestrator health
        orchestrator_healthy = False
        orchestrator_info = {}
        
        if orchestrator:
            orchestrator_info = orchestrator.get_agent_stats()
            orchestrator_healthy = orchestrator_info.get('is_initialized', False)
        
        # System health info with proper datetime serialization
        health_data = {
            "status": "healthy" if orchestrator_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - app_start_time).total_seconds(),
            "checks": {
                "orchestrator": {
                    "status": "healthy" if orchestrator_healthy else "unhealthy",
                    "details": custom_jsonable_encoder(orchestrator_info)
                },
                "environment": {
                    "log_level": os.getenv("LOG_LEVEL", "DEBUG"),
                    "neo4j_uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                    "environment": os.getenv("ENVIRONMENT", "development")
                }
            }
        }
        
        status_code = 200 if orchestrator_healthy else 503
        
        execution_time = time.time() - start_time
        log_function_exit(
            app_logger, 
            "health_check", 
            result=f"status_{status_code}", 
            execution_time=execution_time
        )
        
        return JSONResponse(content=health_data, status_code=status_code)
        
    except Exception as e:
        app_logger.error(f"Health check failed: {e}", exc_info=True)
        
        error_response = {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        
        log_function_exit(app_logger, "health_check", result="error", execution_time=time.time() - start_time)
        return JSONResponse(content=error_response, status_code=503)


@app.post("/tasks")
async def create_task(
    task_definition: TaskDefinition,
    agent: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Create a new task for repository analysis.
    
    Args:
        task_definition: Task definition containing repository information
        agent: Orchestrator agent dependency
        
    Returns:
        Task creation response with execution ID
    """
    start_time = time.time()
    log_function_entry(
        app_logger, 
        "create_task",
        repository_url=task_definition.repository_url
    )
    
    try:
        app_logger.info(f"Creating new task for repository: {task_definition.repository_url}")
        
        # Handle task with orchestrator
        execution_id = agent.handle_task(task_definition)
        
        response = {
            "execution_id": execution_id,
            "status": "created",
            "task_definition": {
                "repository_url": task_definition.repository_url,
                "task_id": task_definition.task_id,
                "created_at": task_definition.created_at.isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
        execution_time = time.time() - start_time
        log_performance_metric(
            app_logger,
            "task_creation_time",
            execution_time * 1000,
            "ms",
            repository_url=task_definition.repository_url,
            execution_id=execution_id
        )
        
        app_logger.info(f"Task created successfully: {execution_id}", extra={
            'extra_data': {
                'execution_id': execution_id,
                'repository_url': task_definition.repository_url,
                'execution_time_ms': execution_time * 1000
            }
        })
        
        log_function_exit(app_logger, "create_task", result=execution_id, execution_time=execution_time)
        return response
        
    except Exception as e:
        app_logger.error(f"Failed to create task: {e}", exc_info=True, extra={
            'extra_data': {
                'repository_url': task_definition.repository_url,
                'error_type': type(e).__name__
            }
        })
        
        log_function_exit(app_logger, "create_task", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@app.get("/tasks/{execution_id}")
async def get_task_status(
    execution_id: str,
    agent: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Get the status of a specific task.
    
    Args:
        execution_id: Task execution ID
        agent: Orchestrator agent dependency
        
    Returns:
        Task status information
    """
    start_time = time.time()
    log_function_entry(app_logger, "get_task_status", execution_id=execution_id)
    
    try:
        task_info = agent.get_task_status(execution_id)
        
        if task_info is None:
            app_logger.warning(f"Task not found: {execution_id}")
            log_function_exit(app_logger, "get_task_status", result="not_found", execution_time=time.time() - start_time)
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Prepare response
        response = {
            "execution_id": execution_id,
            "status": task_info['status'],
            "created_at": task_info['created_at'].isoformat(),
            "steps_completed": task_info.get('steps_completed', []),
            "errors": task_info.get('errors', []),
            "repository_url": task_info['definition'].repository_url,
            "timestamp": datetime.now().isoformat()
        }
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "get_task_status", result="found", execution_time=execution_time)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Failed to get task status: {e}", exc_info=True)
        log_function_exit(app_logger, "get_task_status", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@app.get("/stats")
async def get_stats(agent: OrchestratorAgent = Depends(get_orchestrator)):
    """
    Get comprehensive system statistics.
    
    Args:
        agent: Orchestrator agent dependency
        
    Returns:
        System and agent statistics
    """
    try:
        return agent.get_agent_stats()
    except Exception as e:
        app_logger.error(f"Failed to get stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# === Q&A Conversation Models ===

class ChatMessage(BaseModel):
    """Chat message model for Q&A conversation."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str = Field(..., description="Message content")
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    timestamp: datetime = Field(default_factory=datetime.now)
    message_type: Optional[str] = Field(None, description="Type: question, clarification, response")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class ChatSessionRequest(BaseModel):
    """Request model for chat sessions."""
    session_id: Optional[str] = Field(None, description="Existing session ID")
    message: str = Field(..., description="User message")
    repository_context: Optional[Dict[str, Any]] = Field(None, description="Repository context if available")
    user_id: Optional[str] = Field("user123", description="User identifier for API key management")

class ChatSessionResponse(BaseModel):
    """Response model for chat sessions."""
    session_id: str = Field(..., description="Session ID")
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    bot_response: ChatMessage = Field(..., description="Bot response")
    conversation_state: str = Field(..., description="Current conversation state")
    requires_input: Optional[Dict[str, Any]] = Field(None, description="Additional input needed")

class IntentParseResult(BaseModel):
    """Result of intent parsing."""
    intent: str = Field(..., description="Parsed intent")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    confidence: float = Field(..., description="Confidence score")
    next_action: str = Field(..., description="Next action needed")

# === Session Management ===
class ChatSessionManager:
    """Simple in-memory session manager for Q&A conversations."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger("chat.session_manager")
    
    def create_session(self) -> str:
        """Create a new chat session."""
        session_id = str(uuid4())
        self.sessions[session_id] = {
            'created_at': datetime.now(),
            'messages': [],
            'state': 'greeting',
            'context': {},
            'repository_url': None,
            'pat_token': None,
            'task_type': None
        }
        self.logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update session data."""
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
    
    def add_message(self, session_id: str, message: ChatMessage):
        """Add message to session."""
        if session_id in self.sessions:
            self.sessions[session_id]['messages'].append(message)

# === Simplified LLM Dialog Manager ===
class SimplifiedLLMDialogManager:
    """
    Simplified LLM Dialog Manager để tránh circular import.
    """
    
    def __init__(self, session_manager: 'ChatSessionManager'):
        """Khởi tạo với session manager và memory service"""
        self.session_manager = session_manager
        self.logger = get_logger("simplified.llm.dialog")
        
        # Initialize memory service
        try:
            from src.services.memory_service import memory_service
            self.memory_service = memory_service
            self.logger.info("Memory service integrated successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize memory service: {e}")
            self.memory_service = None
    
    def _get_memory_count(self, relevant_memories) -> int:
        """Helper to get memory count regardless of format."""
        if not relevant_memories:
            return 0
        if isinstance(relevant_memories, dict) and 'results' in relevant_memories:
            return len(relevant_memories['results'])
        return len(relevant_memories) if relevant_memories else 0
    
    def _has_memory_context(self, relevant_memories) -> bool:
        """Helper to check if there's actual memory context."""
        if not relevant_memories:
            return False
        if isinstance(relevant_memories, dict) and 'results' in relevant_memories:
            return len(relevant_memories['results']) > 0
        return len(relevant_memories) > 0 if relevant_memories else False
    
    def _setup_llm_parser(self):
        """Setup LLM parser if needed."""
        # Import LLM parser trực tiếp
        import sys
        import os
        llm_path = os.path.join(os.path.dirname(__file__), 'src', 'teams', 'interaction_tasking')
        if llm_path not in sys.path:
            sys.path.append(llm_path)
        
        try:
            import simplified_llm_intent_parser
            self.llm_parser = simplified_llm_intent_parser.SimplifiedLLMIntentParser()
            self.logger.info("LLM parser initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM parser: {e}")
            self.llm_parser = None
    
    def process_message(self, session_id: str, user_message: str, repository_context: Optional[Dict[str, Any]] = None, user_id: str = "user123") -> 'ChatSessionResponse':
        """
        Process user message với LLM-powered intent parsing.
        """
        try:
            # Get or create session
            if not session_id:
                session_id = self.session_manager.create_session()
            
            session = self.session_manager.get_session(session_id)
            if not session:
                session_id = self.session_manager.create_session()
                session = self.session_manager.get_session(session_id)
            
            # Add user message to session
            user_msg = ChatMessage(
                content=user_message,
                role="user",
                message_type="user_input"
            )
            self.session_manager.add_message(session_id, user_msg)
            
            # Retrieve relevant memories for context
            relevant_memories = []
            if self.memory_service:
                try:
                    relevant_memories = self.memory_service.get_relevant_memories(
                        user_id=user_id,
                        current_message=user_message,
                        limit=3
                    )
                    self.logger.info(f"Retrieved {len(relevant_memories)} relevant memories for user {user_id}")
                except Exception as e:
                    self.logger.error(f"Error retrieving memories: {e}")
            
            # Parse intent với LLM - always try to create user-specific parser
            try:
                # Create user-specific parser with their API key
                from src.teams.interaction_tasking.simplified_llm_intent_parser import SimplifiedLLMIntentParser
                user_parser = SimplifiedLLMIntentParser(user_id=user_id)
                
                # Enhanced message with memory context
                enhanced_message = user_message
                if relevant_memories:
                    # Handle both dict format {"results": [...]} and list format
                    memory_list = relevant_memories
                    if isinstance(relevant_memories, dict) and 'results' in relevant_memories:
                        memory_list = relevant_memories['results']
                    
                    if memory_list and len(memory_list) > 0:
                        # Use only 2 most recent memories
                        recent_memories = memory_list[-2:] if len(memory_list) >= 2 else memory_list
                        memory_context = "\n".join([
                            f"Previous: {mem.get('memory', mem.get('user_message', ''))}" 
                            for mem in recent_memories
                        ])
                        enhanced_message = f"Context từ cuộc hội thoại trước:\n{memory_context}\n\nTin nhắn hiện tại: {user_message}"
                
                user_intent = user_parser.parse_user_intent(enhanced_message)
                
                self.logger.info(f"LLM parsed intent: {user_intent.intent_type.value}, confidence: {user_intent.confidence}")
                
                # Use LLM response directly - memory context already in enhanced_message sent to OpenAI
                if user_intent.suggested_questions:
                    bot_content = user_intent.suggested_questions[0]
                else:
                    bot_content = "Tôi hiểu yêu cầu của bạn. Bạn có thể cung cấp thêm thông tin không?"
                
                # DO NOT add hard-coded memory indicator - OpenAI should handle context awareness naturally
                
                # Tạo bot response
                bot_response = ChatMessage(
                    content=bot_content,
                    role="assistant",
                    message_type="response",
                    context={
                        "intent": user_intent.intent_type.value,
                        "confidence": user_intent.confidence,
                        "llm_powered": True,
                        "memories_used": self._get_memory_count(relevant_memories),
                        "has_memory_context": self._has_memory_context(relevant_memories)
                    }
                )
                
                # Update session state
                session['state'] = 'llm_processed'
                if user_intent.extracted_entities:
                    session.update(user_intent.extracted_entities)
                    
            except Exception as e:
                self.logger.error(f"LLM processing failed: {e}")
                
                # Try direct intent parsing without user-specific parser as fallback
                try:
                    from src.teams.interaction_tasking.simplified_llm_intent_parser import SimplifiedLLMIntentParser
                    fallback_parser = SimplifiedLLMIntentParser()
                    
                    # Enhanced message with memory context for fallback
                    enhanced_message = user_message
                    if relevant_memories:
                        # Handle both dict format {"results": [...]} and list format
                        memory_list = relevant_memories
                        if isinstance(relevant_memories, dict) and 'results' in relevant_memories:
                            memory_list = relevant_memories['results']
                        
                        if memory_list and len(memory_list) > 0:
                            recent_memories = memory_list[-2:] if len(memory_list) >= 2 else memory_list
                            memory_context = "\n".join([
                                f"Previous: {mem.get('memory', mem.get('user_message', ''))}" 
                                for mem in recent_memories
                            ])
                            enhanced_message = f"Context từ cuộc hội thoại trước:\n{memory_context}\n\nTin nhắn hiện tại: {user_message}"
                    
                    user_intent = fallback_parser.parse_user_intent(enhanced_message)
                    
                    # Use parsed intent response directly - memory context already handled by OpenAI
                    if user_intent.suggested_questions:
                        fallback_content = user_intent.suggested_questions[0]
                    else:
                        fallback_content = "Tôi hiểu yêu cầu của bạn. Bạn có thể cung cấp thêm thông tin không?"
                    
                    # DO NOT add hard-coded memory text - OpenAI should respond contextually
                    
                    bot_response = ChatMessage(
                        content=fallback_content,
                        role="assistant",
                        message_type="response",
                        context={
                            "intent": user_intent.intent_type.value,
                            "confidence": user_intent.confidence,
                            "llm_powered": True, 
                            "fallback_parser": True,
                            "memories_used": self._get_memory_count(relevant_memories),
                            "has_memory_context": self._has_memory_context(relevant_memories)
                        }
                    )
                    session['state'] = 'fallback_parsed'
                    
                except Exception as fallback_error:
                    self.logger.error(f"Fallback parsing also failed: {fallback_error}")
                    # Final static fallback
                    fallback_content = "Xin chào! Tôi có thể giúp gì cho bạn? Bạn muốn quét repository hay review PR?"
                    
                    # Static fallback - no memory context added to avoid hard-coding
                    
                    bot_response = ChatMessage(
                        content=fallback_content,
                        role="assistant",
                        message_type="response",
                        context={
                            "llm_powered": False, 
                            "fallback": True,
                            "memories_used": self._get_memory_count(relevant_memories),
                            "has_memory_context": self._has_memory_context(relevant_memories)
                        }
                    )
                    session['state'] = 'fallback'
            
            # Add bot response to session
            self.session_manager.add_message(session_id, bot_response)
            self.session_manager.update_session(session_id, session)
            
            # Save conversation to memory
            if self.memory_service:
                try:
                    self.memory_service.add_conversation_memory(
                        user_id=user_id,
                        session_id=session_id,
                        user_message=user_message,
                        bot_response=bot_response.content,
                        context={
                            "intent": bot_response.context.get('intent') if bot_response.context else None,
                            "confidence": bot_response.context.get('confidence') if bot_response.context else None,
                            "session_state": session.get('state'),
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    self.logger.info(f"Saved conversation to memory for user {user_id}")
                except Exception as e:
                    self.logger.error(f"Error saving conversation to memory: {e}")
            
            return ChatSessionResponse(
                session_id=session_id,
                messages=session['messages'],
                bot_response=bot_response,
                conversation_state=session['state'],
                requires_input=None
            )
            
        except Exception as e:
            self.logger.error(f"Error in simplified LLM dialog processing: {e}", exc_info=True)
            
            # Fallback error response
            error_msg = ChatMessage(
                content="Xin lỗi, tôi gặp chút vấn đề khi xử lý yêu cầu của bạn. Bạn có thể thử lại không? 😅",
                role="assistant",
                message_type="error"
            )
            
            if session_id and session_id in self.session_manager.sessions:
                self.session_manager.add_message(session_id, error_msg)
                session = self.session_manager.get_session(session_id)
                messages = session['messages'] if session else [error_msg]
            else:
                messages = [error_msg]
            
            return ChatSessionResponse(
                session_id=session_id or "error",
                messages=messages,
                bot_response=error_msg,
                conversation_state="error",
                requires_input=None
            )


# === Streaming LLM Dialog Manager ===
class StreamingLLMDialogManager(SimplifiedLLMDialogManager):
    """
    Extended LLM Dialog Manager with real-time status streaming capability.
    """
    
    def __init__(self, session_manager: 'ChatSessionManager'):
        super().__init__(session_manager)
        self.logger = get_logger("streaming.llm.dialog")
    
    def _create_status_event(self, status: str, progress: int = 0, metadata: Dict[str, Any] = None) -> str:
        """Create SSE formatted status event."""
        event_data = {
            "type": "status",
            "status": status,
            "progress": progress,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        return f"data: {json.dumps(event_data)}\n\n"
    
    def _create_message_event(self, message: ChatMessage) -> str:
        """Create SSE formatted message event."""
        event_data = {
            "type": "message",
            "message": {
                "id": message.id,
                "content": message.content,
                "role": message.role,
                "timestamp": message.timestamp.isoformat(),
                "message_type": message.message_type,
                "context": message.context
            }
        }
        return f"data: {json.dumps(event_data)}\n\n"
    
    def _create_complete_event(self, session_response: 'ChatSessionResponse') -> str:
        """Create SSE formatted completion event."""
        event_data = {
            "type": "complete",
            "session_id": session_response.session_id,
            "conversation_state": session_response.conversation_state,
            "bot_response": {
                "id": session_response.bot_response.id,
                "content": session_response.bot_response.content,
                "role": session_response.bot_response.role,
                "timestamp": session_response.bot_response.timestamp.isoformat(),
                "message_type": session_response.bot_response.message_type,
                "context": session_response.bot_response.context
            }
        }
        return f"data: {json.dumps(event_data)}\n\n"
    
    def _extract_repository_url(self, message: str) -> Optional[str]:
        """
        Extract repository URL from user message.
        
        Args:
            message: User message text
            
        Returns:
            Repository URL if found, None otherwise
        """
        import re
        
        # GitHub patterns
        github_patterns = [
            r'https?://github\.com/[\w\-\.]+/[\w\-\.]+',
            r'github\.com/[\w\-\.]+/[\w\-\.]+',
            r'git@github\.com:[\w\-\.]+/[\w\-\.]+\.git'
        ]
        
        # GitLab patterns  
        gitlab_patterns = [
            r'https?://gitlab\.com/[\w\-\.]+/[\w\-\.]+',
            r'gitlab\.com/[\w\-\.]+/[\w\-\.]+',
        ]
        
        # Bitbucket patterns
        bitbucket_patterns = [
            r'https?://bitbucket\.org/[\w\-\.]+/[\w\-\.]+',
            r'bitbucket\.org/[\w\-\.]+/[\w\-\.]+',
        ]
        
        all_patterns = github_patterns + gitlab_patterns + bitbucket_patterns
        
        for pattern in all_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                url = match.group(0)
                # Normalize URL
                if not url.startswith('http'):
                    if 'github.com' in url:
                        url = f"https://{url}"
                    elif 'gitlab.com' in url:
                        url = f"https://{url}"
                    elif 'bitbucket.org' in url:
                        url = f"https://{url}"
                
                # Remove .git suffix if present
                if url.endswith('.git'):
                    url = url[:-4]
                    
                return url
        
        return None
    
    async def process_message_stream(self, session_id: str, user_message: str, repository_context: Optional[Dict[str, Any]] = None, user_id: str = "user123") -> Generator[str, None, None]:
        """
        Process user message với real-time status streaming.
        """
        try:
            # Start processing
            yield self._create_status_event("🔄 Đang khởi tạo phiên chat...", 5)
            await asyncio.sleep(0.1)  # Small delay for visual effect
            
            # Get or create session
            if not session_id:
                session_id = self.session_manager.create_session()
            
            session = self.session_manager.get_session(session_id)
            if not session:
                session_id = self.session_manager.create_session()
                session = self.session_manager.get_session(session_id)
            
            yield self._create_status_event("📝 Đang lưu tin nhắn người dùng...", 10)
            await asyncio.sleep(0.1)
            
            # Add user message to session
            user_msg = ChatMessage(
                content=user_message,
                role="user",
                message_type="user_input"
            )
            self.session_manager.add_message(session_id, user_msg)
            
            yield self._create_status_event("🧠 Đang tìm kiếm ngữ cảnh từ bộ nhớ...", 20)
            await asyncio.sleep(0.2)
            
            # Retrieve relevant memories for context
            relevant_memories = []
            if self.memory_service:
                try:
                    relevant_memories = self.memory_service.get_relevant_memories(
                        user_id=user_id,
                        current_message=user_message,
                        limit=3
                    )
                    memory_count = self._get_memory_count(relevant_memories)
                    yield self._create_status_event(
                        f"💭 Đã tìm thấy {memory_count} bối cảnh liên quan...", 
                        35,
                        {"memories_found": memory_count}
                    )
                    self.logger.info(f"Retrieved {memory_count} relevant memories for user {user_id}")
                except Exception as e:
                    self.logger.error(f"Error retrieving memories: {e}")
                    yield self._create_status_event("⚠️ Không thể truy cập bộ nhớ, tiếp tục...", 35)
            
            yield self._create_status_event("🤖 Đang phân tích ý định người dùng...", 50)
            await asyncio.sleep(0.3)
            
            # Parse intent với LLM - always try to create user-specific parser
            try:
                # Create user-specific parser with their API key
                from src.teams.interaction_tasking.simplified_llm_intent_parser import SimplifiedLLMIntentParser
                user_parser = SimplifiedLLMIntentParser(user_id=user_id)
                
                yield self._create_status_event("🔗 Đang kết hợp ngữ cảnh cuộc hội thoại...", 65)
                await asyncio.sleep(0.2)
                
                # Enhanced message with memory context
                enhanced_message = user_message
                if relevant_memories:
                    # Handle both dict format {"results": [...]} and list format
                    memory_list = relevant_memories
                    if isinstance(relevant_memories, dict) and 'results' in relevant_memories:
                        memory_list = relevant_memories['results']
                    
                    if memory_list and len(memory_list) > 0:
                        # Use only 2 most recent memories
                        recent_memories = memory_list[-2:] if len(memory_list) >= 2 else memory_list
                        memory_context = "\n".join([
                            f"Previous: {mem.get('memory', mem.get('user_message', ''))}" 
                            for mem in recent_memories
                        ])
                        enhanced_message = f"Context từ cuộc hội thoại trước:\n{memory_context}\n\nTin nhắn hiện tại: {user_message}"
                
                yield self._create_status_event("🎯 Đang tạo phản hồi từ AI...", 80)
                await asyncio.sleep(0.4)
                
                user_intent = user_parser.parse_user_intent(enhanced_message)
                
                self.logger.info(f"LLM parsed intent: {user_intent.intent_type.value}, confidence: {user_intent.confidence}")
                
                # Use LLM response directly - memory context already in enhanced_message sent to OpenAI
                if user_intent.suggested_questions:
                    bot_content = user_intent.suggested_questions[0]
                else:
                    bot_content = "Tôi hiểu yêu cầu của bạn. Bạn có thể cung cấp thêm thông tin không?"
                
                yield self._create_status_event("✨ Đang hoàn thiện phản hồi...", 95)
                await asyncio.sleep(0.2)
                
                # Tạo bot response
                bot_response = ChatMessage(
                    content=bot_content,
                    role="assistant",
                    message_type="response",
                    context={
                        "intent": user_intent.intent_type.value,
                        "confidence": user_intent.confidence,
                        "llm_powered": True,
                        "memories_used": self._get_memory_count(relevant_memories),
                        "has_memory_context": self._has_memory_context(relevant_memories)
                    }
                )
                
                # Update session state
                session['state'] = 'llm_processed'
                if user_intent.extracted_entities:
                    session.update(user_intent.extracted_entities)
                    
            except Exception as e:
                self.logger.error(f"LLM processing failed: {e}")
                yield self._create_status_event("⚠️ Đang thử phương pháp dự phòng...", 70)
                await asyncio.sleep(0.2)
                
                # Try direct intent parsing without user-specific parser as fallback
                try:
                    from src.teams.interaction_tasking.simplified_llm_intent_parser import SimplifiedLLMIntentParser
                    fallback_parser = SimplifiedLLMIntentParser()
                    
                    # Enhanced message with memory context for fallback
                    enhanced_message = user_message
                    if relevant_memories:
                        # Handle both dict format {"results": [...]} and list format
                        memory_list = relevant_memories
                        if isinstance(relevant_memories, dict) and 'results' in relevant_memories:
                            memory_list = relevant_memories['results']
                        
                        if memory_list and len(memory_list) > 0:
                            recent_memories = memory_list[-2:] if len(memory_list) >= 2 else memory_list
                            memory_context = "\n".join([
                                f"Previous: {mem.get('memory', mem.get('user_message', ''))}" 
                                for mem in recent_memories
                            ])
                            enhanced_message = f"Context từ cuộc hội thoại trước:\n{memory_context}\n\nTin nhắn hiện tại: {user_message}"
                    
                    yield self._create_status_event("🔄 Đang xử lý với parser dự phòng...", 85)
                    await asyncio.sleep(0.3)
                    
                    user_intent = fallback_parser.parse_user_intent(enhanced_message)
                    
                    # Use parsed intent response directly - memory context already handled by OpenAI
                    if user_intent.suggested_questions:
                        fallback_content = user_intent.suggested_questions[0]
                    else:
                        fallback_content = "Tôi hiểu yêu cầu của bạn. Bạn có thể cung cấp thêm thông tin không?"
                    
                    bot_response = ChatMessage(
                        content=fallback_content,
                        role="assistant",
                        message_type="response",
                        context={
                            "intent": user_intent.intent_type.value,
                            "confidence": user_intent.confidence,
                            "llm_powered": True, 
                            "fallback_parser": True,
                            "memories_used": self._get_memory_count(relevant_memories),
                            "has_memory_context": self._has_memory_context(relevant_memories)
                        }
                    )
                    session['state'] = 'fallback_parsed'
                    
                except Exception as fallback_error:
                    self.logger.error(f"Fallback parsing also failed: {fallback_error}")
                    yield self._create_status_event("🔧 Đang sử dụng phản hồi mặc định...", 90)
                    await asyncio.sleep(0.2)
                    
                    # Final static fallback
                    fallback_content = "Xin chào! Tôi có thể giúp gì cho bạn? Bạn muốn quét repository hay review PR?"
                    
                    bot_response = ChatMessage(
                        content=fallback_content,
                        role="assistant",
                        message_type="response",
                        context={
                            "intent": "greeting",
                            "confidence": 0.8,
                            "llm_powered": False,
                            "fallback": True,
                            "memories_used": self._get_memory_count(relevant_memories),
                            "has_memory_context": self._has_memory_context(relevant_memories)
                        }
                    )
                    session['state'] = 'static_fallback'
            
            # Add bot response to session
            self.session_manager.add_message(session_id, bot_response)
            
            # Store memory nếu có memory service
            if self.memory_service:
                try:
                    self.memory_service.store_user_memory(
                        user_id=user_id,
                        user_message=user_message,
                        ai_response=bot_response.content
                    )
                except Exception as e:
                    self.logger.error(f"Error storing memory: {e}")
            
            # Create response object
            session_response = ChatSessionResponse(
                session_id=session_id,
                messages=session['messages'],
                bot_response=bot_response,
                conversation_state=session.get('state', 'processed')
            )
            
            # === TASK EXECUTION INTEGRATION ===
            # Check if intent requires task execution (scan_project, pr_review, etc.)
            intent_type = bot_response.context.get('intent', '') if bot_response.context else ''
            if intent_type in ['scan_project', 'repository_scan', 'pr_review', 'code_analysis']:
                yield self._create_status_event("🚀 Đang khởi tạo task execution...", 100)
                await asyncio.sleep(0.5)
                
                try:
                    # Extract repository URL from user message or context
                    repo_url = self._extract_repository_url(user_message)
                    if repo_url:
                        yield self._create_status_event("📦 Đã tìm thấy repository URL, đang bắt đầu scan...", 100)
                        
                        # Create task definition for repository scanning
                        from src.models.task_models import TaskDefinition, TaskType
                        task_definition = TaskDefinition(
                            type=TaskType.REPOSITORY_SCAN,
                            input_data={"repository_url": repo_url},
                            config={"deep_scan": True, "include_dependencies": True}
                        )
                        
                        # Execute task via orchestrator
                        orchestrator = get_orchestrator()
                        execution_result = await orchestrator.execute_task(task_definition)
                        
                        # Update session với task execution ID
                        session = self.session_manager.get_session(session_id)
                        if session:
                            session['task_execution_id'] = execution_result.execution_id
                            session['task_status'] = 'running'
                            self.session_manager.update_session(session_id, session)
                        
                        # Create updated response với task info
                        updated_content = f"{bot_response.content}\n\n🔄 **Task đang thực thi**: {execution_result.execution_id}\n\nBạn có thể theo dõi progress tại `/tasks/{execution_result.execution_id}`"
                        
                        bot_response = ChatMessage(
                            content=updated_content,
                            role="assistant", 
                            message_type="response",
                            context={
                                **bot_response.context,
                                "task_execution_id": execution_result.execution_id,
                                "task_status": "running",
                                "repository_url": repo_url
                            }
                        )
                        
                        # Update session với bot response mới
                        self.session_manager.add_message(session_id, bot_response)
                        
                        yield self._create_status_event("✅ Task đã được khởi tạo thành công!", 100)
                    else:
                        yield self._create_status_event("⚠️ Không tìm thấy repository URL", 100)
                        
                except Exception as task_error:
                    self.logger.error(f"Error executing task: {task_error}")
                    yield self._create_status_event(f"❌ Lỗi khi thực thi task: {str(task_error)}", 100)
            else:
                yield self._create_status_event("✅ Hoàn thành!", 100)
            
            await asyncio.sleep(0.1)
            
            # Create final response object với updated content
            final_session_response = ChatSessionResponse(
                session_id=session_id,
                messages=self.session_manager.get_session(session_id)['messages'],
                bot_response=bot_response,
                conversation_state=self.session_manager.get_session(session_id).get('state', 'processed')
            )
            
            # Send final complete event
            yield self._create_complete_event(final_session_response)
            
        except Exception as e:
            self.logger.error(f"Error in streaming message processing: {e}")
            error_response = ChatMessage(
                content=f"Đã xảy ra lỗi khi xử lý tin nhắn: {str(e)}",
                role="assistant",
                message_type="error"
            )
            yield self._create_status_event("❌ Đã xảy ra lỗi", 0, {"error": str(e)})
            yield self._create_message_event(error_response)


# === Q&A Conversation Endpoints ===

@app.post("/chat", response_model=ChatSessionResponse)
async def chat_conversation(request: ChatSessionRequest):
    """
    Enhanced Q&A conversation endpoint với unified chat system & LLM integration.
    """
    start_time = time.time()
    log_function_entry(app_logger, "chat_conversation")
    
    try:
        # Validate request
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Process message
        response = dialog_manager.process_message(
            session_id=request.session_id,
            user_message=request.message,
            repository_context=request.repository_context,
            user_id=request.user_id
        )
        
        duration = time.time() - start_time
        log_performance_metric(app_logger, "chat_conversation_duration", duration * 1000, "ms")
        
        log_function_exit(app_logger, "chat_conversation")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error in chat conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/chat/stream")
async def chat_conversation_stream(request: ChatSessionRequest):
    """
    Streaming chat conversation endpoint với real-time status updates.
    Sử dụng Server-Sent Events (SSE) để stream progress và response.
    """
    start_time = time.time()
    log_function_entry(app_logger, "chat_conversation_stream")
    
    try:
        # Validate request
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Create streaming generator
        async def event_stream():
            try:
                async for event in streaming_dialog_manager.process_message_stream(
                    session_id=request.session_id,
                    user_message=request.message,
                    repository_context=request.repository_context,
                    user_id=request.user_id
                ):
                    yield event
                    
            except Exception as e:
                app_logger.error(f"Error in streaming chat: {e}", exc_info=True)
                # Send error event
                error_event = {
                    "type": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_event)}\n\n"
        
        duration = time.time() - start_time
        log_performance_metric(app_logger, "chat_stream_setup_duration", duration * 1000, "ms")
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error setting up streaming chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """
    Get chat history for a specific session.
    
    Args:
        session_id: Session ID to retrieve
        
    Returns:
        Chat session data with message history
    """
    start_time = time.time()
    log_function_entry(app_logger, "get_chat_history", session_id=session_id)
    
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "get_chat_history", result="success", execution_time=execution_time)
        
        return {
            "session_id": session_id,
            "created_at": session['created_at'],
            "state": session['state'],
            "messages": session['messages'],
            "repository_url": session.get('repository_url'),
            "context": session.get('context', {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error retrieving chat history: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "get_chat_history", result="error")
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/chat/{session_id}/execute")
async def execute_task_from_chat(
    session_id: str,
    agent: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Execute a task that was defined through chat conversation.
    
    This endpoint bridges the Q&A conversation to actual task execution,
    implementing the TaskInitiation functionality from DESIGN.md.
    
    Args:
        session_id: Session ID containing the task context
        agent: Orchestrator agent dependency
        
    Returns:
        Task execution response
    """
    start_time = time.time()
    log_function_entry(app_logger, "execute_task_from_chat", session_id=session_id)
    
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session has enough information to create a task
        repository_url = session.get('repository_url')
        if not repository_url:
            raise HTTPException(
                status_code=400, 
                detail="Session does not contain repository information. Please provide repository URL through chat first."
            )
        
        # Import TaskInitiationModule for task creation
        from src.teams.interaction_tasking.task_initiation_module import TaskInitiationModule
        
        task_initiation = TaskInitiationModule()
        task_type = session.get('task_type', 'scan_project')  # Default to project scan
        
        # Create appropriate task definition based on session context
        if task_type == 'review_pr':
            pr_id = session.get('pr_id')
            pr_url = session.get('pr_url')
            if not (pr_id or pr_url):
                raise HTTPException(
                    status_code=400,
                    detail="PR review task requires PR ID or URL. Please provide this information through chat."
                )
            
            task_def = task_initiation.create_review_pr_task(
                repository_url=repository_url,
                pr_identifier=pr_id or pr_url
            )
        else:
            # Default to project scan
            task_def = task_initiation.create_scan_project_task(
                repository_url=repository_url
            )
        
        # Execute task via orchestrator
        execution_id = agent.handle_task(task_def)
        
        # Update session with execution info
        session_manager.update_session(session_id, {
            'execution_id': execution_id,
            'task_definition': task_def.__dict__,
            'execution_started_at': datetime.now()
        })
        
        # Add system message to chat
        system_message = ChatMessage(
            content=f"✅ Đã bắt đầu thực thi task: {task_def.task_type}\n\n📊 **Execution ID**: `{execution_id}`\n🔗 **Repository**: {repository_url}\n\nBạn có thể theo dõi tiến trình bằng cách hỏi về trạng thái task.",
            role="assistant",
            message_type="system_notification",
            context={"execution_id": execution_id, "task_type": str(task_def.task_type)}
        )
        session_manager.add_message(session_id, system_message)
        
        execution_time = time.time() - start_time
        log_performance_metric(
            app_logger,
            "execute_task_from_chat_duration",
            execution_time * 1000,
            "ms",
            session_id=session_id,
            execution_id=execution_id
        )
        
        log_function_exit(app_logger, "execute_task_from_chat", result="success")
        
        return {
            "status": "success",
            "execution_id": execution_id,
            "task_type": str(task_def.task_type),
            "repository_url": repository_url,
            "session_id": session_id,
            "message": "Task execution started successfully. You can ask about task status through chat."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error executing task from chat: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "execute_task_from_chat", result="error")
        raise HTTPException(status_code=500, detail=error_msg)


@app.delete("/chat/{session_id}")
async def delete_chat_session(session_id: str):
    """
    Delete a chat session and clear its data.
    
    Args:
        session_id: Session ID to delete
        
    Returns:
        Deletion confirmation
    """
    start_time = time.time()
    log_function_entry(app_logger, "delete_chat_session", session_id=session_id)
    
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Remove session from manager
        if session_id in session_manager.sessions:
            del session_manager.sessions[session_id]
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "delete_chat_session", result="success", execution_time=execution_time)
        
        return {
            "status": "success",
            "message": f"Session {session_id} deleted successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error deleting chat session: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "delete_chat_session", result="error")
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/chat/sessions")
async def list_chat_sessions():
    """
    List all active chat sessions (for development/debugging).
    
    Returns:
        List of session summaries
    """
    try:
        sessions_summary = []
        for session_id, session_data in session_manager.sessions.items():
            sessions_summary.append({
                "session_id": session_id,
                "created_at": session_data['created_at'],
                "state": session_data['state'],
                "message_count": len(session_data['messages']),
                "repository_url": session_data.get('repository_url'),
                "has_execution_id": 'execution_id' in session_data
            })
        
        return {
            "total_sessions": len(sessions_summary),
            "sessions": sessions_summary
        }
        
    except Exception as e:
        error_msg = f"Error listing chat sessions: {e}"
        app_logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


# === User Settings and API Key Management Endpoints ===

class UserSettingsResponse(BaseModel):
    """Response model for user settings."""
    user_id: str
    display_name: str
    role: str
    preferences: Dict[str, Any]
    security: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    api_keys_count: int


@app.get("/users/{user_id}/settings", response_model=UserSettingsResponse)
async def get_user_settings(user_id: str):
    """
    Get user settings and preferences.
    
    Args:
        user_id: User identifier
        
    Returns:
        User settings without sensitive data
    """
    start_time = time.time()
    log_function_entry(app_logger, "get_user_settings", user_id=user_id)
    
    try:
        settings = user_settings_service.get_user_settings(user_id)
        if not settings:
            raise HTTPException(status_code=404, detail="User settings not found")
        
        response = UserSettingsResponse(
            user_id=settings.user_id,
            display_name=settings.display_name,
            role=settings.role.value,
            preferences=settings.preferences.__dict__,
            security={
                "two_factor_enabled": settings.security.two_factor_enabled,
                "session_timeout_minutes": settings.security.session_timeout_minutes,
                "require_encryption": settings.security.require_encryption
                # Không trả về sensitive info như IP whitelist
            },
            created_at=settings.created_at,
            updated_at=settings.updated_at,
            api_keys_count=len(settings.api_keys)
        )
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "get_user_settings", result="success", execution_time=execution_time)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error getting user settings: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "get_user_settings", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=error_msg)


@app.put("/users/{user_id}/settings")
async def update_user_settings(user_id: str, request: UserSettingsRequest):
    """
    Update user preferences and settings.
    
    Args:
        user_id: User identifier
        request: Settings update request
        
    Returns:
        Success message
    """
    start_time = time.time()
    log_function_entry(app_logger, "update_user_settings", user_id=user_id)
    
    try:
        if request.preferences:
            success = user_settings_service.update_preferences(user_id, request.preferences)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to update preferences")
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "update_user_settings", result="success", execution_time=execution_time)
        
        return {"message": "Settings updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error updating user settings: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "update_user_settings", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/users/{user_id}/api-keys")
async def add_api_key(user_id: str, request: APIKeyRequest):
    """
    Add or update an API key for a user.
    
    Args:
        user_id: User identifier
        request: API key request with provider and key
        
    Returns:
        Success message
    """
    start_time = time.time()
    log_function_entry(app_logger, "add_api_key", user_id=user_id, provider=request.provider.value)
    
    try:
        success = user_settings_service.add_api_key(user_id, request)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add API key")
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "add_api_key", result="success", execution_time=execution_time)
        
        return {"message": f"API key for {request.provider.value} added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error adding API key: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "add_api_key", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/users/{user_id}/api-keys")
async def list_api_keys(user_id: str):
    """
    List all API keys for a user (metadata only).
    
    Args:
        user_id: User identifier
        
    Returns:
        List of API key metadata
    """
    start_time = time.time()
    log_function_entry(app_logger, "list_api_keys", user_id=user_id)
    
    try:
        api_keys = user_settings_service.list_api_keys(user_id)
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "list_api_keys", result="success", execution_time=execution_time)
        
        return {"api_keys": api_keys}
        
    except Exception as e:
        error_msg = f"Error listing API keys: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "list_api_keys", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=error_msg)


@app.delete("/users/{user_id}/api-keys/{provider}")
async def remove_api_key(user_id: str, provider: APIKeyProvider):
    """
    Remove an API key for a specific provider.
    
    Args:
        user_id: User identifier
        provider: API key provider to remove
        
    Returns:
        Success message
    """
    start_time = time.time()
    log_function_entry(app_logger, "remove_api_key", user_id=user_id, provider=provider.value)
    
    try:
        success = user_settings_service.remove_api_key(user_id, provider)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to remove API key")
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "remove_api_key", result="success", execution_time=execution_time)
        
        return {"message": f"API key for {provider.value} removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error removing API key: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "remove_api_key", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/users/{user_id}/api-keys/{provider}/test")
async def test_api_key(user_id: str, provider: APIKeyProvider):
    """
    Test if an API key is valid and working.
    
    Args:
        user_id: User identifier
        provider: API key provider to test
        
    Returns:
        Test result
    """
    start_time = time.time()
    log_function_entry(app_logger, "test_api_key", user_id=user_id, provider=provider.value)
    
    try:
        api_key = user_settings_service.get_api_key(user_id, provider)
        if not api_key:
            raise HTTPException(status_code=404, detail=f"No API key found for provider {provider.value}")
        
        # Test the API key based on provider
        is_valid = False
        error_message = None
        
        if provider == APIKeyProvider.OPENAI:
            # Test OpenAI API key
            try:
                import openai
                client = openai.OpenAI(api_key=api_key)
                # Simple test call
                response = client.models.list()
                is_valid = True
            except Exception as e:
                error_message = f"OpenAI API test failed: {str(e)}"
        
        elif provider == APIKeyProvider.ANTHROPIC:
            # Test Anthropic API key
            try:
                # Add Anthropic API test here when implemented
                error_message = "Anthropic API testing not implemented yet"
            except Exception as e:
                error_message = f"Anthropic API test failed: {str(e)}"
        
        else:
            error_message = f"API testing not implemented for provider {provider.value}"
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "test_api_key", result="success" if is_valid else "failed", execution_time=execution_time)
        
        return {
            "provider": provider.value,
            "is_valid": is_valid,
            "error_message": error_message,
            "tested_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error testing API key: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "test_api_key", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api-providers")
async def get_supported_providers():
    """
    Get list of supported API providers.
    
    Returns:
        List of supported providers with descriptions
    """
    providers = [
        {
            "provider": APIKeyProvider.OPENAI.value,
            "name": "OpenAI",
            "description": "OpenAI GPT models (GPT-4, GPT-3.5-turbo, etc.)",
            "website": "https://openai.com",
            "key_format": "sk-..."
        },
        {
            "provider": APIKeyProvider.ANTHROPIC.value,
            "name": "Anthropic",
            "description": "Claude AI models",
            "website": "https://anthropic.com",
            "key_format": "sk-ant-..."
        },
        {
            "provider": APIKeyProvider.GOOGLE_GENAI.value,
            "name": "Google Generative AI",
            "description": "Google Gemini models",
            "website": "https://ai.google.dev",
            "key_format": "AI..."
        },
        {
            "provider": APIKeyProvider.AZURE_OPENAI.value,
            "name": "Azure OpenAI",
            "description": "OpenAI models via Microsoft Azure",
            "website": "https://azure.microsoft.com/en-us/products/ai-services/openai-service",
            "key_format": "..."
        },
        {
            "provider": APIKeyProvider.HUGGINGFACE.value,
            "name": "Hugging Face",
            "description": "Hugging Face Inference API",
            "website": "https://huggingface.co",
            "key_format": "hf_..."
        }
    ]
    
    return {"providers": providers}


# === Memory Management Endpoints ===

def get_memory_service():
    """Helper function to get memory service với error handling."""
    # Get from dialog manager if available
    if hasattr(dialog_manager, 'memory_service') and dialog_manager.memory_service:
        return dialog_manager.memory_service
    
    # Create simple fallback memory service
    class FallbackMemoryService:
        def get_user_memories(self, user_id, limit=20):
            return []
        
        def get_memory_stats(self, user_id):
            return {
                "total_memories": 0,
                "memory_service_active": False,
                "last_memory_date": None,
                "user_id": user_id,
                "fallback_mode": True
            }
        
        def get_relevant_memories(self, user_id, current_message, limit=5):
            return []
        
        def delete_user_memories(self, user_id):
            return True
    
    return FallbackMemoryService()


@app.get("/users/{user_id}/memories")
async def get_user_memories(user_id: str, limit: int = 20):
    """
    Lấy memories của user.
    
    Args:
        user_id: ID của user
        limit: Số lượng memories tối đa (default: 20)
        
    Returns:
        List of user memories với metadata
    """
    start_time = time.time()
    log_function_entry(app_logger, "get_user_memories", user_id=user_id, limit=limit)
    
    try:
        memory_service = get_memory_service()
        
        memories = memory_service.get_user_memories(user_id=user_id, limit=limit)
        stats = memory_service.get_memory_stats(user_id=user_id)
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "get_user_memories", result="success", execution_time=execution_time)
        
        return {
            "status": "success",
            "user_id": user_id,
            "memories": memories,
            "stats": stats,
            "total_retrieved": len(memories)
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error retrieving user memories: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "get_user_memories", result="error")
        raise HTTPException(status_code=500, detail=error_msg)


@app.delete("/users/{user_id}/memories")
async def delete_user_memories(user_id: str):
    """
    Xóa tất cả memories của user.
    
    Args:
        user_id: ID của user
        
    Returns:
        Confirmation message
    """
    start_time = time.time()
    log_function_entry(app_logger, "delete_user_memories", user_id=user_id)
    
    try:
        memory_service = get_memory_service()
        
        success = memory_service.delete_user_memories(user_id=user_id)
        
        if success:
            execution_time = time.time() - start_time
            log_function_exit(app_logger, "delete_user_memories", result="success", execution_time=execution_time)
            
            return {
                "status": "success",
                "message": f"Đã xóa tất cả memories của user {user_id}",
                "user_id": user_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete user memories")
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error deleting user memories: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "delete_user_memories", result="error")
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/users/{user_id}/memories/search")
async def search_user_memories(user_id: str, query: str, limit: int = 10):
    """
    Tìm kiếm memories của user theo query.
    
    Args:
        user_id: ID của user
        query: Search query
        limit: Số lượng kết quả tối đa (default: 10)
        
    Returns:
        Relevant memories matching the query
    """
    start_time = time.time()
    log_function_entry(app_logger, "search_user_memories", user_id=user_id, query_length=len(query), limit=limit)
    
    try:
        memory_service = get_memory_service()
        
        memories = memory_service.get_relevant_memories(
            user_id=user_id,
            current_message=query,
            limit=limit
        )
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "search_user_memories", result="success", execution_time=execution_time)
        
        return {
            "status": "success",
            "user_id": user_id,
            "query": query,
            "memories": memories,
            "total_found": len(memories)
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error searching user memories: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "search_user_memories", result="error")
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/users/{user_id}/memories/stats")
async def get_user_memory_stats(user_id: str):
    """
    Lấy thống kê về memories của user.
    
    Args:
        user_id: ID của user
        
    Returns:
        Memory statistics và system info
    """
    start_time = time.time()
    log_function_entry(app_logger, "get_user_memory_stats", user_id=user_id)
    
    try:
        memory_service = get_memory_service()
        
        stats = memory_service.get_memory_stats(user_id=user_id)
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "get_user_memory_stats", result="success", execution_time=execution_time)
        
        return {
            "status": "success",
            "user_id": user_id,
            "stats": stats,
            "system_info": {
                "memory_service_available": hasattr(memory_service, 'memory') and memory_service.memory is not None,
                "fallback_mode": hasattr(memory_service, '_fallback_memory'),
                "retrieval_time_ms": execution_time * 1000
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Error getting user memory stats: {e}"
        app_logger.error(error_msg, exc_info=True)
        log_function_exit(app_logger, "get_user_memory_stats", result="error")
        raise HTTPException(status_code=500, detail=error_msg)


if __name__ == "__main__":
    # This allows running the app directly for development
    app_logger.info("Starting RepoChat in direct mode")
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 