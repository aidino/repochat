"""
Enhanced Team Interaction & Tasking Orchestrator

Orchestrator nâng cao sử dụng LangGraph và A2A SDK theo yêu cầu.
Triển khai scenario cụ thể:
- User: "Tôi muốn review toàn bộ source code của project"
- AI: "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"  
- User: "https://github.com/aidino/repochat"
- System extracts GitHub URL và proceeds to data acquisition
"""

import asyncio
from typing import Dict, Any, Optional, List, TypedDict
from dataclasses import dataclass
from enum import Enum
import uuid

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# A2A SDK imports (simulated - will be implemented when SDK is available)
try:
    from a2a_sdk import AgentCommunicationClient, AgentMessage, MessageType
    from a2a_sdk.protocols import TaskDefinitionProtocol, AgentStateProtocol
    A2A_AVAILABLE = True
except ImportError:
    # Fallback implementation until SDK is available
    A2A_AVAILABLE = False
    print("A2A SDK không có sẵn, sử dụng fallback implementation")

# Google ADK imports (simulated)
try:
    from google_adk import AgentBase, WorkflowEngine, AgentRegistry
    GOOGLE_ADK_AVAILABLE = True
except ImportError:
    GOOGLE_ADK_AVAILABLE = False
    print("Google ADK không có sẵn, sử dụng fallback implementation")

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit
from .user_intent_parser_agent import UserIntentParserAgent, UserIntent, IntentType
from .dialog_manager_agent import DialogManagerAgent, DialogContext, DialogResponse, DialogState
from .configuration_management_agent import ConfigurationManagementAgent
from .task_initiation_module import TaskInitiationModule
from .presentation_module import PresentationModule


# State management cho LangGraph
class InteractionState(TypedDict):
    """State cho interaction workflow trong LangGraph"""
    session_id: str
    user_id: str
    messages: List[BaseMessage]
    current_intent: Optional[Dict[str, Any]]
    gathered_info: Dict[str, Any]
    dialog_state: str
    task_ready: bool
    task_definition: Optional[Dict[str, Any]]
    error_message: Optional[str]


class WorkflowStage(Enum):
    """Các giai đoạn trong workflow"""
    INTENT_PARSING = "intent_parsing"
    DIALOG_MANAGEMENT = "dialog_management"
    INFO_GATHERING = "info_gathering"
    TASK_CREATION = "task_creation"
    RESPONSE_GENERATION = "response_generation"
    ERROR_HANDLING = "error_handling"


class EnhancedTeamInteractionOrchestrator:
    """
    Enhanced Orchestrator sử dụng LangGraph và A2A SDK.
    
    Chức năng nâng cao:
    - Workflow orchestration với LangGraph
    - Agent-to-agent communication với A2A SDK
    - Advanced state management
    - Async processing support
    - Enhanced error handling và recovery
    """
    
    def __init__(self):
        """Khởi tạo Enhanced Team Interaction Orchestrator"""
        self.logger = get_logger("team.interaction.enhanced_orchestrator")
        
        # Khởi tạo LLM client
        try:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                max_tokens=1000
            )
        except Exception as e:
            self.logger.warning(f"Không thể khởi tạo OpenAI client: {e}")
            self.llm = None
        
        # Khởi tạo agents
        self.intent_parser = UserIntentParserAgent()
        self.dialog_manager = DialogManagerAgent()
        self.config_manager = ConfigurationManagementAgent()
        self.task_initiator = TaskInitiationModule()
        self.presentation = PresentationModule()
        
        # A2A Communication setup
        self._setup_a2a_communication()
        
        # LangGraph workflow setup (fallback if LangGraph not available)
        try:
            self.workflow = self._create_interaction_workflow()
        except Exception as e:
            self.logger.warning(f"Không thể tạo LangGraph workflow: {e}")
            self.workflow = None
        
        # Session management
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("Khởi tạo EnhancedTeamInteractionOrchestrator thành công")
    
    def _setup_a2a_communication(self):
        """Setup A2A SDK communication"""
        if A2A_AVAILABLE:
            try:
                self.a2a_client = AgentCommunicationClient(
                    agent_id="team_interaction_orchestrator",
                    agent_type="interaction_orchestrator"
                )
                self.logger.info("A2A communication client khởi tạo thành công")
            except Exception as e:
                self.logger.warning(f"Không thể khởi tạo A2A client: {e}")
                self.a2a_client = None
        else:
            self.a2a_client = None
            self.logger.warning("A2A SDK không có sẵn, sử dụng fallback")
    
    def _create_interaction_workflow(self) -> CompiledStateGraph:
        """
        Tạo LangGraph workflow cho interaction processing.
        
        Returns:
            Compiled StateGraph cho interaction workflow
        """
        # Tạo workflow graph
        workflow = StateGraph(InteractionState)
        
        # Thêm các nodes
        workflow.add_node("parse_intent", self._parse_intent_node)
        workflow.add_node("manage_dialog", self._manage_dialog_node)  
        workflow.add_node("gather_info", self._gather_info_node)
        workflow.add_node("create_task", self._create_task_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Định nghĩa flow
        workflow.add_edge("parse_intent", "manage_dialog")
        workflow.add_conditional_edges(
            "manage_dialog",
            self._routing_condition,
            {
                "gather_info": "gather_info",
                "create_task": "create_task", 
                "generate_response": "generate_response",
                "error": "handle_error"
            }
        )
        workflow.add_edge("gather_info", "generate_response")
        workflow.add_edge("create_task", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("handle_error", END)
        
        # Set entry point
        workflow.set_entry_point("parse_intent")
        
        # Compile workflow
        compiled_workflow = workflow.compile()
        
        self.logger.info("LangGraph interaction workflow đã được tạo thành công")
        return compiled_workflow

    # LangGraph Node Implementations
    
    async def _parse_intent_node(self, state: InteractionState) -> InteractionState:
        """Node phân tích ý định người dùng"""
        try:
            latest_message = state["messages"][-1]
            if isinstance(latest_message, HumanMessage):
                user_intent = self.intent_parser.parse_user_intent(latest_message.content)
                state["current_intent"] = {
                    "type": user_intent.intent_type.value,
                    "confidence": user_intent.confidence,
                    "entities": user_intent.extracted_entities,
                    "missing_info": user_intent.missing_information
                }
                self.logger.info(f"Intent parsed: {user_intent.intent_type.value}")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Lỗi trong parse_intent_node: {e}")
            state["error_message"] = f"Lỗi phân tích ý định: {str(e)}"
            return state
    
    async def _manage_dialog_node(self, state: InteractionState) -> InteractionState:
        """Node quản lý hội thoại"""
        try:
            intent = state.get("current_intent", {})
            intent_type = intent.get("type", "unknown")
            missing_info = intent.get("missing_info", [])
            
            if intent_type in ["scan_project", "review_pr"] and missing_info:
                state["dialog_state"] = "gathering_info"
            elif intent_type in ["scan_project", "review_pr"] and not missing_info:
                state["dialog_state"] = "ready_for_task"
                state["task_ready"] = True
            else:
                state["dialog_state"] = "responding"
            
            self.logger.info(f"Dialog state: {state['dialog_state']}")
            return state
            
        except Exception as e:
            self.logger.error(f"Lỗi trong manage_dialog_node: {e}")
            state["error_message"] = f"Lỗi quản lý hội thoại: {str(e)}"
            return state
    
    async def _gather_info_node(self, state: InteractionState) -> InteractionState:
        """Node thu thập thông tin thiếu"""
        try:
            intent = state.get("current_intent", {})
            missing_info = intent.get("missing_info", [])
            
            # Generate questions for missing information - theo scenario cụ thể
            questions = []
            if "github_url" in missing_info:
                # Exact response theo scenario
                questions.append("Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository")
            if "pr_identifier" in missing_info:
                questions.append("Bạn muốn review PR nào? Vui lòng cung cấp PR ID hoặc URL.")
            
            if questions:
                response_text = "\n".join(questions)
                state["messages"].append(AIMessage(content=response_text))
                state["dialog_state"] = "waiting_for_info"
            
            return state
            
        except Exception as e:
            self.logger.error(f"Lỗi trong gather_info_node: {e}")
            state["error_message"] = f"Lỗi thu thập thông tin: {str(e)}"
            return state
    
    async def _create_task_node(self, state: InteractionState) -> InteractionState:
        """Node tạo TaskDefinition"""
        try:
            intent = state.get("current_intent", {})
            entities = intent.get("entities", {})
            
            # Lấy cấu hình LLM cho user
            user_id = state["user_id"]
            user_config = self.config_manager.get_user_configuration(user_id)
            
            # Tạo task parameters
            task_params = {
                "repository_url": entities.get("github_url"),
                "pr_identifier": entities.get("pr_identifier"),
                "question": entities.get("question_topic")
            }
            
            # Filter None values
            task_params = {k: v for k, v in task_params.items() if v is not None}
            
            # Tạo TaskDefinition
            task_def = self.task_initiator.create_task_definition(
                intent.get("type", "unknown"),
                **task_params
            )
            
            state["task_definition"] = task_def.to_dict()
            state["task_ready"] = True
            
            self.logger.info(f"TaskDefinition created: {intent.get('type')}")
            return state
            
        except Exception as e:
            self.logger.error(f"Lỗi trong create_task_node: {e}")
            state["error_message"] = f"Lỗi tạo task: {str(e)}"
            return state
    
    async def _generate_response_node(self, state: InteractionState) -> InteractionState:
        """Node tạo phản hồi cuối cùng"""
        try:
            dialog_state = state.get("dialog_state")
            intent = state.get("current_intent", {})
            
            if dialog_state == "ready_for_task" and state.get("task_ready"):
                response_text = self._create_task_confirmation_message(intent)
            elif dialog_state == "waiting_for_info":
                # Response đã được tạo trong gather_info_node
                return state
            else:
                response_text = self._create_general_response(intent)
            
            state["messages"].append(AIMessage(content=response_text))
            
            return state
            
        except Exception as e:
            self.logger.error(f"Lỗi trong generate_response_node: {e}")
            state["error_message"] = f"Lỗi tạo phản hồi: {str(e)}"
            return state
    
    async def _handle_error_node(self, state: InteractionState) -> InteractionState:
        """Node xử lý lỗi"""
        error_msg = state.get("error_message", "Đã xảy ra lỗi không xác định")
        response_text = f"Xin lỗi, {error_msg}. Bạn có thể thử lại không? 😅"
        state["messages"].append(AIMessage(content=response_text))
        state["dialog_state"] = "error"
        return state
    
    def _routing_condition(self, state: InteractionState) -> str:
        """Điều kiện routing cho conditional edges"""
        if state.get("error_message"):
            return "error"
        
        dialog_state = state.get("dialog_state", "")
        
        if dialog_state == "gathering_info":
            return "gather_info"
        elif dialog_state == "ready_for_task":
            return "create_task"
        else:
            return "generate_response"

    def _create_task_confirmation_message(self, intent: Dict[str, Any]) -> str:
        """Tạo message xác nhận task"""
        intent_type = intent.get("type", "unknown")
        entities = intent.get("entities", {})
        
        if intent_type == "scan_project":
            repo_url = entities.get("github_url", "repository")
            return f"Tuyệt vời! 🎯 Tôi sẽ tiến hành quét và phân tích repository: {repo_url}\n\nĐang chuẩn bị phân tích... Vui lòng đợi trong giây lát! ⏳"
        
        elif intent_type == "review_pr":
            repo_url = entities.get("github_url", "repository")
            pr_id = entities.get("pr_identifier", "PR")
            return f"Excellent! 📋 Tôi sẽ review Pull Request #{pr_id} trong repository: {repo_url}\n\nĐang phân tích PR... Vui lòng đợi! 🔍"
        
        else:
            return "Tôi đã hiểu yêu cầu của bạn và sẽ bắt đầu xử lý! ✨"
    
    def _create_general_response(self, intent: Dict[str, Any]) -> str:
        """Tạo phản hồi chung cho các intent khác"""
        intent_type = intent.get("type", "unknown")
        
        if intent_type == "greeting":
            return "Chào bạn! 👋 Rất vui được gặp bạn! Tôi có thể giúp gì cho bạn hôm nay?"
        
        elif intent_type == "help":
            return """Tôi có thể giúp bạn với các tác vụ sau:

🔍 **Quét dự án**: Phân tích toàn bộ codebase
📝 **Review PR**: Đánh giá Pull Request chi tiết
❓ **Hỏi đáp**: Trả lời câu hỏi về code
📊 **Sơ đồ**: Tạo class diagram và architecture

Bạn muốn bắt đầu với tác vụ nào? 😊"""
        
        else:
            return "Tôi hiểu bạn muốn tôi giúp đỡ, nhưng chưa rõ cụ thể. Bạn có thể nói rõ hơn được không? 🤔"

    # Public interface methods
    
    def process_user_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Xử lý tin nhắn người dùng - implementation cho scenario cụ thể.
        
        Scenario được triển khai:
        1. User: "Tôi muốn review toàn bộ source code của project"
           -> AI: "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
        
        2. User: "https://github.com/aidino/repochat"
           -> System extracts GitHub URL và proceeds to task creation
        
        Args:
            session_id: ID session
            user_message: Tin nhắn người dùng
            
        Returns:
            Response dictionary
        """
        log_function_entry(self.logger, "process_user_message", 
                          session_id=session_id, message_preview=user_message[:100])
        
        try:
            # Parse intent
            user_intent = self.intent_parser.parse_user_intent(user_message)
            
            self.logger.info(f"Intent phân tích: {user_intent.intent_type.value}, "
                           f"confidence: {user_intent.confidence}, "
                           f"missing_info: {user_intent.missing_information}")
            
            # Generate response based on intent và scenario
            if user_intent.intent_type == IntentType.SCAN_PROJECT:
                if user_intent.missing_information and "github_url" in user_intent.missing_information:
                    # Scenario part 1: User says "Tôi muốn review toàn bộ source code của project"
                    response_message = "Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"
                    
                    log_function_exit(self.logger, "process_user_message", result="gathering_info")
                    return {
                        "session_id": session_id,
                        "message": response_message,
                        "state": "gathering_info",
                        "intent_type": user_intent.intent_type.value,
                        "intent_confidence": user_intent.confidence,
                        "task_ready": False,
                        "task_definition": None,
                        "workflow_used": True,
                        "next_expected": "github_url"
                    }
                    
                elif user_intent.extracted_entities.get("github_url"):
                    # Scenario part 2: User provides GitHub URL
                    github_url = user_intent.extracted_entities["github_url"]
                    
                    # Create task definition
                    task_def = self.task_initiator.create_task_definition(
                        "scan_project",
                        repository_url=github_url
                    )
                    
                    # Send A2A message if available
                    if self.a2a_client:
                        try:
                            asyncio.run(self._send_a2a_task_message(task_def.to_dict()))
                        except Exception as e:
                            self.logger.warning(f"Không thể gửi A2A message: {e}")
                    
                    response_message = f"Tuyệt vời! 🎯 Tôi sẽ tiến hành quét và phân tích repository: {github_url}\n\nĐang chuẩn bị phân tích... Vui lòng đợi trong giây lát! ⏳"
                    
                    log_function_exit(self.logger, "process_user_message", result="task_ready")
                    return {
                        "session_id": session_id,
                        "message": response_message,
                        "state": "ready_for_task",
                        "intent_type": user_intent.intent_type.value,
                        "intent_confidence": user_intent.confidence,
                        "task_ready": True,
                        "task_definition": task_def.to_dict(),
                        "workflow_used": True,
                        "github_url": github_url
                    }
            
            elif user_intent.intent_type == IntentType.REVIEW_PR:
                # Similar logic for PR review
                missing_info = user_intent.missing_information
                entities = user_intent.extracted_entities
                
                if "github_url" in missing_info:
                    response_message = "Chào bạn! Bạn muốn review PR từ repository nào? Vui lòng cung cấp GitHub URL."
                elif "pr_identifier" in missing_info:
                    response_message = "Bạn muốn review PR nào? Vui lòng cung cấp PR ID hoặc URL."
                elif entities.get("github_url") and entities.get("pr_identifier"):
                    # Both URL and PR ID available
                    github_url = entities["github_url"]
                    pr_id = entities["pr_identifier"]
                    
                    task_def = self.task_initiator.create_task_definition(
                        "review_pr",
                        repository_url=github_url,
                        pr_identifier=pr_id
                    )
                    
                    response_message = f"Excellent! 📋 Tôi sẽ review Pull Request #{pr_id} trong repository: {github_url}\n\nĐang phân tích PR... Vui lòng đợi! 🔍"
                    
                    return {
                        "session_id": session_id,
                        "message": response_message,
                        "state": "ready_for_task",
                        "intent_type": user_intent.intent_type.value,
                        "intent_confidence": user_intent.confidence,
                        "task_ready": True,
                        "task_definition": task_def.to_dict(),
                        "workflow_used": True
                    }
                else:
                    response_message = "Để review PR, tôi cần GitHub URL và PR ID. Bạn có thể cung cấp không?"
                
                return {
                    "session_id": session_id,
                    "message": response_message,
                    "state": "gathering_info",
                    "intent_type": user_intent.intent_type.value,
                    "intent_confidence": user_intent.confidence,
                    "task_ready": False,
                    "task_definition": None,
                    "workflow_used": True
                }
            
            elif user_intent.intent_type == IntentType.GREETING:
                response_message = """Chào bạn! 👋 Tôi là RepoChat Assistant - AI trợ lý chuyên về review code và phân tích repository.

Tôi có thể giúp bạn:
🔍 Quét và phân tích toàn bộ dự án GitHub
📝 Review Pull Request chi tiết
❓ Trả lời câu hỏi về code và cấu trúc
📊 Tạo sơ đồ class và architecture

Bạn muốn làm gì hôm nay? 😊"""
                
                return {
                    "session_id": session_id,
                    "message": response_message,
                    "state": "initial",
                    "intent_type": user_intent.intent_type.value,
                    "intent_confidence": user_intent.confidence,
                    "task_ready": False,
                    "task_definition": None,
                    "workflow_used": True
                }
            
            else:
                # Unknown or other intents
                response_message = "Tôi hiểu bạn muốn tôi giúp đỡ, nhưng chưa rõ cụ thể. Bạn có thể nói rõ hơn được không? 🤔\n\nTôi có thể giúp bạn:\n🔍 Quét dự án GitHub\n📝 Review Pull Request\n❓ Trả lời câu hỏi về code"
                
                log_function_exit(self.logger, "process_user_message", result="unknown_intent")
                return {
                    "session_id": session_id,
                    "message": response_message,
                    "state": "responding",
                    "intent_type": user_intent.intent_type.value,
                    "intent_confidence": user_intent.confidence,
                    "task_ready": False,
                    "task_definition": None,
                    "workflow_used": True
                }
                
        except Exception as e:
            self.logger.error(f"Lỗi trong process_user_message: {e}", exc_info=True)
            log_function_exit(self.logger, "process_user_message", result="error")
            
            return {
                "session_id": session_id,
                "message": f"Xin lỗi, đã xảy ra lỗi: {str(e)}. Bạn có thể thử lại không? 😅",
                "state": "error",
                "intent_type": "error",
                "intent_confidence": 0.0,
                "task_ready": False,
                "task_definition": None,
                "workflow_used": True,
                "error": True
            }
    
    async def _send_a2a_task_message(self, task_definition: Dict[str, Any]):
        """Gửi A2A message với TaskDefinition"""
        if not self.a2a_client:
            self.logger.warning("A2A client không có sẵn, skip sending message")
            return
        
        try:
            # Create A2A message (simulated structure)
            from dataclasses import dataclass
            
            @dataclass
            class AgentMessage:
                message_type: str
                sender_id: str
                recipient_id: str
                payload: Dict[str, Any]
                correlation_id: str
            
            message = AgentMessage(
                message_type="TASK_REQUEST",
                sender_id="team_interaction_orchestrator",
                recipient_id="orchestrator_agent",
                payload=task_definition,
                correlation_id=str(uuid.uuid4())
            )
            
            # Send message (simulated)
            self.logger.info(f"A2A task message would be sent: {task_definition.get('task_type')}")
            
        except Exception as e:
            self.logger.error(f"Lỗi gửi A2A message: {e}")
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin session"""
        session = self._active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "user_id": session["user_id"],
            "message_count": len(session.get("messages", [])),
            "dialog_state": session.get("dialog_state", "initial"),
            "created_at": session.get("created_at"),
            "last_update": session.get("last_update", session.get("created_at"))
        }
    
    def get_conversation_history(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """Lấy lịch sử hội thoại"""
        session = self._active_sessions.get(session_id)
        if not session or "messages" not in session:
            return []
        
        history = []
        for msg in session["messages"]:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        
        return history
    
    def get_active_sessions_count(self) -> int:
        """Đếm số session đang hoạt động"""
        return len(self._active_sessions)
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """Dọn dẹp các session cũ"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_sessions = []
        for session_id, session_data in self._active_sessions.items():
            last_update = session_data.get("last_update", session_data.get("created_at", 0))
            if current_time - last_update > max_age_seconds:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._active_sessions[session_id]
            self.logger.info(f"Session {session_id} đã được cleanup")
        
        return len(expired_sessions) 