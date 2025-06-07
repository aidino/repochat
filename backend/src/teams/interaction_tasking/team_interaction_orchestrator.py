"""
Team Interaction & Tasking Orchestrator

Orchestrator chính cho TEAM Interaction & Tasking, tích hợp tất cả các agent:
- UserIntentParserAgent: Phân tích ý định người dùng
- DialogManagerAgent: Quản lý hội thoại
- ConfigurationManagementAgent: Quản lý cấu hình LLM
- TaskInitiationModule: Tạo TaskDefinition
- PresentationModule: Hiển thị kết quả

Đây là giao diện chính để tương tác với TEAM này.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit
from .user_intent_parser_agent import UserIntentParserAgent, UserIntent
from .dialog_manager_agent import DialogManagerAgent, DialogContext, DialogResponse, DialogState
from .configuration_management_agent import ConfigurationManagementAgent
from .task_initiation_module import TaskInitiationModule
from .presentation_module import PresentationModule


@dataclass
class InteractionSession:
    """Session tương tác với người dùng"""
    session_id: str
    user_id: str
    dialog_context: DialogContext
    is_active: bool = True
    
    def get_conversation_history(self) -> str:
        """Lấy lịch sử hội thoại dưới dạng text"""
        history = []
        for msg in self.dialog_context.conversation_history:
            role = "👤 User" if msg["role"] == "user" else "🤖 Assistant"
            history.append(f"{role}: {msg['content']}")
        return "\n\n".join(history)


class TeamInteractionOrchestrator:
    """
    Orchestrator chính cho TEAM Interaction & Tasking.
    
    Chức năng chính:
    - Điều phối tất cả các agent trong TEAM
    - Quản lý session tương tác người dùng
    - Xử lý end-to-end flow từ input đến output
    - Tích hợp với các TEAM khác thông qua TaskDefinition
    """
    
    def __init__(self):
        """Khởi tạo Team Interaction Orchestrator"""
        self.logger = get_logger("team.interaction.orchestrator")
        
        # Khởi tạo các agent
        self.intent_parser = UserIntentParserAgent()
        self.dialog_manager = DialogManagerAgent()
        self.config_manager = ConfigurationManagementAgent()
        self.task_initiator = TaskInitiationModule()
        self.presentation = PresentationModule()
        
        # Quản lý sessions
        self._active_sessions: Dict[str, InteractionSession] = {}
        
        self.logger.info("Khởi tạo TeamInteractionOrchestrator thành công")
    
    def start_new_session(self, user_id: str, session_id: Optional[str] = None) -> InteractionSession:
        """
        Bắt đầu session tương tác mới với người dùng.
        
        Args:
            user_id: ID của người dùng
            session_id: ID session (tự động tạo nếu không cung cấp)
            
        Returns:
            InteractionSession mới
        """
        log_function_entry(self.logger, "start_new_session", user_id=user_id, session_id=session_id)
        
        try:
            # Tạo session ID nếu chưa có
            if not session_id:
                import uuid
                session_id = str(uuid.uuid4())
            
            # Khởi tạo dialog context
            dialog_context = self.dialog_manager.__init_session()
            
            # Tạo session
            session = InteractionSession(
                session_id=session_id,
                user_id=user_id,
                dialog_context=dialog_context,
                is_active=True
            )
            
            # Lưu vào active sessions
            self._active_sessions[session_id] = session
            
            self.logger.info(f"Tạo session mới thành công: {session_id} cho user {user_id}")
            log_function_exit(self.logger, "start_new_session", result="success")
            
            return session
            
        except Exception as e:
            self.logger.error(f"Lỗi khi tạo session mới: {e}", exc_info=True)
            log_function_exit(self.logger, "start_new_session", result="error")
            raise
    
    def process_user_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Xử lý tin nhắn từ người dùng trong một session.
        
        Args:
            session_id: ID của session
            user_message: Tin nhắn từ người dùng
            
        Returns:
            Dict chứa phản hồi và thông tin trạng thái
        """
        log_function_entry(self.logger, "process_user_message", 
                          session_id=session_id, user_message=user_message[:100])
        
        try:
            # Lấy session
            session = self._get_session(session_id)
            if not session:
                return self._create_error_response("Session không tồn tại hoặc đã hết hạn")
            
            # 1. Phân tích ý định người dùng
            user_intent = self.intent_parser.parse_user_intent(user_message)
            
            self.logger.info(f"Intent phân tích: {user_intent.intent_type.value}, confidence: {user_intent.confidence}")
            
            # 2. Xử lý với Dialog Manager
            dialog_response = self.dialog_manager.process_user_input(
                user_message, 
                session.dialog_context, 
                user_intent
            )
            
            # 3. Kiểm tra xem có cần thực hiện task không
            task_definition = None
            if dialog_response.should_execute_task and dialog_response.task_params:
                # Lấy cấu hình LLM cho user
                user_config = self.config_manager.get_user_configuration(session.user_id)
                
                # Tạo TaskDefinition với cấu hình LLM
                task_definition = self._create_task_definition(
                    dialog_response.task_params,
                    user_config.llm_configs
                )
            
            # 4. Định dạng phản hồi cuối cùng
            formatted_response = self.presentation.format_dialog_response(dialog_response)
            
            # 5. Chuẩn bị response
            response = {
                "session_id": session_id,
                "message": formatted_response,
                "state": dialog_response.state.value,
                "intent_type": user_intent.intent_type.value,
                "intent_confidence": user_intent.confidence,
                "suggested_actions": dialog_response.suggested_actions,
                "task_ready": dialog_response.should_execute_task,
                "task_definition": task_definition.to_dict() if task_definition else None,
                "conversation_length": len(session.dialog_context.conversation_history)
            }
            
            self.logger.info(f"Xử lý tin nhắn thành công, state: {dialog_response.state.value}")
            log_function_exit(self.logger, "process_user_message", result="success")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Lỗi khi xử lý tin nhắn người dùng: {e}", exc_info=True)
            log_function_exit(self.logger, "process_user_message", result="error")
            return self._create_error_response(f"Đã xảy ra lỗi: {str(e)}")
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin session.
        
        Args:
            session_id: ID của session
            
        Returns:
            Thông tin session hoặc None nếu không tồn tại
        """
        session = self._get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "is_active": session.is_active,
            "state": session.dialog_context.state.value,
            "conversation_length": len(session.dialog_context.conversation_history),
            "last_question": session.dialog_context.last_question,
            "gathered_info": session.dialog_context.gathered_info
        }
    
    def get_conversation_history(self, session_id: str) -> Optional[str]:
        """
        Lấy lịch sử hội thoại của session.
        
        Args:
            session_id: ID của session
            
        Returns:
            Lịch sử hội thoại dưới dạng text
        """
        session = self._get_session(session_id)
        if not session:
            return None
        
        return session.get_conversation_history()
    
    def end_session(self, session_id: str) -> bool:
        """
        Kết thúc session.
        
        Args:
            session_id: ID của session
            
        Returns:
            True nếu thành công
        """
        log_function_entry(self.logger, "end_session", session_id=session_id)
        
        try:
            if session_id in self._active_sessions:
                session = self._active_sessions[session_id]
                session.is_active = False
                del self._active_sessions[session_id]
                
                self.logger.info(f"Kết thúc session thành công: {session_id}")
                log_function_exit(self.logger, "end_session", result="success")
                return True
            else:
                self.logger.warning(f"Session không tồn tại: {session_id}")
                log_function_exit(self.logger, "end_session", result="not_found")
                return False
                
        except Exception as e:
            self.logger.error(f"Lỗi khi kết thúc session: {e}", exc_info=True)
            log_function_exit(self.logger, "end_session", result="error")
            return False
    
    def update_user_llm_config(self, user_id: str, team_name: str, 
                              provider: str, model_name: str, 
                              **kwargs) -> bool:
        """
        Cập nhật cấu hình LLM cho user.
        
        Args:
            user_id: ID người dùng
            team_name: Tên TEAM
            provider: Nhà cung cấp LLM
            model_name: Tên model
            **kwargs: Các tham số khác (temperature, max_tokens, etc.)
            
        Returns:
            True nếu cập nhật thành công
        """
        log_function_entry(self.logger, "update_user_llm_config", 
                          user_id=user_id, team_name=team_name, 
                          provider=provider, model_name=model_name)
        
        try:
            from .configuration_management_agent import LLMConfiguration, LLMProvider
            
            # Tạo LLM configuration
            llm_config = LLMConfiguration(
                provider=LLMProvider(provider),
                model_name=model_name,
                temperature=kwargs.get('temperature', 0.1),
                max_tokens=kwargs.get('max_tokens', 1000),
                timeout=kwargs.get('timeout', 30),
                api_key_env=kwargs.get('api_key_env', 'OPENAI_API_KEY'),
                base_url=kwargs.get('base_url')
            )
            
            # Cập nhật
            success = self.config_manager.update_llm_configuration(
                user_id, team_name, llm_config
            )
            
            if success:
                self.logger.info(f"Cập nhật cấu hình LLM thành công cho user {user_id}, team {team_name}")
            else:
                self.logger.error(f"Cập nhật cấu hình LLM thất bại")
            
            log_function_exit(self.logger, "update_user_llm_config", result="success" if success else "error")
            return success
            
        except Exception as e:
            self.logger.error(f"Lỗi khi cập nhật cấu hình LLM: {e}", exc_info=True)
            log_function_exit(self.logger, "update_user_llm_config", result="error")
            return False
    
    def get_user_llm_configs(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy tất cả cấu hình LLM của user.
        
        Args:
            user_id: ID người dùng
            
        Returns:
            Dict chứa cấu hình LLM cho từng TEAM
        """
        try:
            user_config = self.config_manager.get_user_configuration(user_id)
            return user_config.llm_configs.to_dict()
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy cấu hình LLM: {e}")
            return None
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        Lấy danh sách model LLM có sẵn.
        
        Returns:
            Dict chứa các model theo provider
        """
        return self.config_manager.get_available_models()
    
    def _get_session(self, session_id: str) -> Optional[InteractionSession]:
        """Lấy session theo ID"""
        return self._active_sessions.get(session_id)
    
    def _create_task_definition(self, task_params: Dict[str, Any], 
                               llm_configs) -> 'TaskDefinition':
        """Tạo TaskDefinition từ task params và LLM configs"""
        
        task_type = task_params.get("task_type")
        
        if task_type == "scan_project":
            return self.task_initiator.create_scan_project_task(
                repository_url=task_params["repository_url"],
                llm_configs=llm_configs
            )
        elif task_type == "review_pr":
            return self.task_initiator.create_review_pr_task(
                repository_url=task_params["repository_url"],
                pr_identifier=task_params["pr_identifier"],
                llm_configs=llm_configs
            )
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Tạo error response"""
        return {
            "session_id": None,
            "message": f"❌ {error_message}",
            "state": "error",
            "intent_type": "unknown",
            "intent_confidence": 0.0,
            "suggested_actions": ["Thử lại", "Tạo session mới"],
            "task_ready": False,
            "task_definition": None,
            "conversation_length": 0
        }
    
    def get_active_sessions_count(self) -> int:
        """Lấy số lượng session đang hoạt động"""
        return len(self._active_sessions)
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """Dọn dẹp các session không hoạt động"""
        # TODO: Implement session expiry logic
        pass 