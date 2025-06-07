"""
Dialog Manager Agent cho TEAM Interaction & Tasking

Agent này chịu trách nhiệm quản lý luồng hội thoại với người dùng.
Nó sẽ:
- Quyết định hành động tiếp theo dựa trên ý định người dùng
- Đặt câu hỏi làm rõ khi thiếu thông tin
- Xác nhận thông tin trước khi thực hiện tác vụ
- Duy trì ngữ cảnh hội thoại
- Sử dụng OpenAI để tạo phản hồi tự nhiên
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit
from .llm_service_client import LLMServiceClient
from .user_intent_parser_agent import UserIntent, IntentType


class DialogState(Enum):
    """Trạng thái của hội thoại"""
    INITIAL = "initial"
    GATHERING_INFO = "gathering_info"
    CONFIRMING = "confirming"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class DialogContext:
    """Ngữ cảnh hội thoại hiện tại"""
    state: DialogState
    current_intent: Optional[UserIntent]
    gathered_info: Dict[str, Any]
    last_question: Optional[str]
    conversation_history: List[Dict[str, str]]
    task_ready: bool = False
    
    def add_user_message(self, message: str):
        """Thêm tin nhắn người dùng vào lịch sử"""
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
    
    def add_assistant_message(self, message: str):
        """Thêm tin nhắn assistant vào lịch sử"""
        self.conversation_history.append({
            "role": "assistant", 
            "content": message
        })
    
    def get_recent_context(self, max_messages: int = 6) -> List[Dict[str, str]]:
        """Lấy ngữ cảnh hội thoại gần đây"""
        return self.conversation_history[-max_messages:]


@dataclass 
class DialogResponse:
    """Phản hồi từ Dialog Manager"""
    message: str
    state: DialogState
    should_execute_task: bool = False
    task_params: Optional[Dict[str, Any]] = None
    suggested_actions: List[str] = None
    
    def __post_init__(self):
        if self.suggested_actions is None:
            self.suggested_actions = []


class DialogManagerAgent:
    """
    Agent quản lý hội thoại với người dùng.
    
    Chức năng chính:
    - Quyết định hành động tiếp theo dựa trên ý định
    - Tạo câu hỏi làm rõ tự nhiên
    - Xác nhận thông tin
    - Duy trì ngữ cảnh hội thoại
    """
    
    def __init__(self):
        """Khởi tạo Dialog Manager Agent"""
        self.logger = get_logger("team.interaction.dialog_manager")
        self.llm_client = LLMServiceClient()
        
        # System prompt cho việc tạo phản hồi tự nhiên
        self.system_prompt = """
Bạn là RepoChat Assistant - một AI assistant chuyên về review code và phân tích repository.

Tính cách và phong cách:
- Thân thiện, chuyên nghiệp và hữu ích
- Trả lời bằng tiếng Việt
- Sử dụng emoji phù hợp để làm cho cuộc trò chuyện sinh động
- Giải thích rõ ràng và dễ hiểu
- Kiên nhẫn khi người dùng cung cấp thông tin

Khả năng chính:
- Quét và phân tích repository GitHub
- Review Pull Request 
- Trả lời câu hỏi về code và cấu trúc dự án
- Tạo sơ đồ class và architecture

Quy tắc trả lời:
1. Luôn thân thiện và tích cực
2. Hỏi từng thông tin một cách tự nhiên
3. Xác nhận thông tin trước khi thực hiện
4. Giải thích những gì bạn sẽ làm
5. Đưa ra gợi ý hữu ích khi có thể

Ví dụ phong cách:
- "Chào bạn! 👋 Tôi là RepoChat Assistant..."
- "Tuyệt vời! Tôi đã hiểu rồi 😊..."
- "Để tôi giúp bạn review PR này nhé 🔍..."
- "Bạn có thể cung cấp thêm thông tin..."
"""
    
    def __init_session(self) -> DialogContext:
        """Khởi tạo session hội thoại mới"""
        context = DialogContext(
            state=DialogState.INITIAL,
            current_intent=None,
            gathered_info={},
            last_question=None,
            conversation_history=[]
        )
        
        # Thêm greeting message
        welcome_msg = """Chào bạn! 👋 Tôi là RepoChat Assistant - AI trợ lý chuyên về review code và phân tích repository.

Tôi có thể giúp bạn:
🔍 Quét và phân tích toàn bộ dự án GitHub
📝 Review Pull Request chi tiết  
❓ Trả lời câu hỏi về code và cấu trúc
📊 Tạo sơ đồ class và architecture

Bạn muốn làm gì hôm nay? 😊"""
        
        context.add_assistant_message(welcome_msg)
        
        self.logger.info("Khởi tạo session hội thoại mới")
        return context
    
    def process_user_input(self, user_input: str, context: DialogContext, 
                          parsed_intent: UserIntent) -> DialogResponse:
        """
        Xử lý input từ người dùng và quyết định hành động tiếp theo.
        
        Args:
            user_input: Tin nhắn từ người dùng
            context: Ngữ cảnh hội thoại hiện tại
            parsed_intent: Ý định đã được phân tích
            
        Returns:
            DialogResponse chứa phản hồi và hành động tiếp theo
        """
        log_function_entry(self.logger, "process_user_input", 
                          user_input=user_input[:100], 
                          intent_type=parsed_intent.intent_type.value)
        
        try:
            # Thêm tin nhắn người dùng vào context
            context.add_user_message(user_input)
            context.current_intent = parsed_intent
            
            # Quyết định hành động dựa trên intent type và state
            response = self._determine_next_action(context, parsed_intent)
            
            # Thêm phản hồi vào context
            context.add_assistant_message(response.message)
            context.state = response.state
            
            self.logger.info(f"Xử lý input thành công: {response.state.value}")
            log_function_exit(self.logger, "process_user_input", result="success")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Lỗi khi xử lý user input: {e}", exc_info=True)
            
            error_response = DialogResponse(
                message="Xin lỗi, tôi gặp chút vấn đề khi xử lý yêu cầu của bạn. Bạn có thể thử lại không? 😅",
                state=DialogState.ERROR
            )
            
            context.add_assistant_message(error_response.message)
            context.state = DialogState.ERROR
            
            log_function_exit(self.logger, "process_user_input", result="error")
            return error_response
    
    def _determine_next_action(self, context: DialogContext, 
                              intent: UserIntent) -> DialogResponse:
        """Quyết định hành động tiếp theo dựa trên intent và context"""
        
        # Xử lý greeting
        if intent.intent_type == IntentType.GREETING:
            return self._handle_greeting()
        
        # Xử lý help
        if intent.intent_type == IntentType.HELP:
            return self._handle_help_request()
        
        # Xử lý unknown intent
        if intent.intent_type == IntentType.UNKNOWN:
            return self._handle_unknown_intent(intent)
        
        # Xử lý các intent cần thông tin
        if intent.intent_type in [IntentType.SCAN_PROJECT, IntentType.REVIEW_PR]:
            return self._handle_task_intent(context, intent)
        
        # Xử lý Q&A
        if intent.intent_type == IntentType.ASK_QUESTION:
            return self._handle_question_intent(intent)
        
        # Xử lý request diagram
        if intent.intent_type == IntentType.REQUEST_DIAGRAM:
            return self._handle_diagram_request(intent)
        
        # Default case
        return DialogResponse(
            message="Tôi hiểu ý định của bạn nhưng chưa thể xử lý ngay. Bạn có thể thử lại với cách nói khác không? 🤔",
            state=DialogState.INITIAL
        )
    
    def _handle_greeting(self) -> DialogResponse:
        """Xử lý greeting từ người dùng"""
        greetings = [
            "Chào bạn! 😊 Rất vui được gặp bạn. Tôi có thể giúp gì cho bạn hôm nay?",
            "Xin chào! 👋 Tôi sẵn sàng hỗ trợ bạn review code. Bạn muốn làm gì?",
            "Hello! 😄 Bạn muốn quét project hay review PR nào đó không?"
        ]
        
        import random
        message = random.choice(greetings)
        
        return DialogResponse(
            message=message,
            state=DialogState.INITIAL,
            suggested_actions=[
                "Quét toàn bộ dự án",
                "Review Pull Request", 
                "Hỏi về code"
            ]
        )
    
    def _handle_help_request(self) -> DialogResponse:
        """Xử lý yêu cầu trợ giúp"""
        help_message = """Tôi có thể giúp bạn những việc sau:

🔍 **Quét dự án**: Phân tích toàn bộ repository GitHub
   Ví dụ: "Quét project https://github.com/user/repo"

📝 **Review PR**: Đánh giá Pull Request chi tiết
   Ví dụ: "Review PR #123 trong repo https://github.com/user/repo"

❓ **Trả lời câu hỏi**: Về code, cấu trúc, logic
   Ví dụ: "Class UserService làm gì?"

📊 **Tạo sơ đồ**: Class diagram, architecture
   Ví dụ: "Tạo sơ đồ class cho UserController"

Bạn muốn thử tính năng nào? 😊"""
        
        return DialogResponse(
            message=help_message,
            state=DialogState.INITIAL
        )
    
    def _handle_unknown_intent(self, intent: UserIntent) -> DialogResponse:
        """Xử lý intent không rõ ràng"""
        
        # Sử dụng LLM để tạo phản hồi tự nhiên
        conversation_context = f"""
Người dùng nói: "{intent.original_text}"

Tôi không hiểu rõ ý định. Hãy trả lời một cách thân thiện và gợi ý những gì tôi có thể làm.
"""
        
        try:
            response = self._generate_natural_response(conversation_context)
            return DialogResponse(
                message=response,
                state=DialogState.INITIAL,
                suggested_actions=[
                    "Quét dự án GitHub",
                    "Review Pull Request",
                    "Hỏi về code"
                ]
            )
        except Exception as e:
            self.logger.warning(f"Không thể tạo phản hồi từ LLM: {e}")
            
            return DialogResponse(
                message="Tôi chưa hiểu rõ yêu cầu của bạn. Bạn có thể nói cụ thể hơn được không? 🤔\n\nVí dụ:\n- 'Quét project ABC'\n- 'Review PR #123'\n- 'Hỏi về class X'",
                state=DialogState.INITIAL
            )
    
    def _handle_task_intent(self, context: DialogContext, 
                           intent: UserIntent) -> DialogResponse:
        """Xử lý intent cần thực hiện task (scan project, review PR)"""
        
        # Cập nhật gathered_info với thông tin đã có
        for key, value in intent.extracted_entities.items():
            context.gathered_info[key] = value
        
        # Kiểm tra xem có đủ thông tin chưa
        if intent.is_complete():
            return self._confirm_task_execution(context, intent)
        else:
            return self._ask_for_missing_info(context, intent)
    
    def _ask_for_missing_info(self, context: DialogContext, 
                             intent: UserIntent) -> DialogResponse:
        """Hỏi thông tin thiếu một cách tự nhiên"""
        
        missing_info = intent.missing_information
        
        if "github_url" in missing_info:
            question = self._create_github_url_question(intent.intent_type)
        elif "pr_identifier" in missing_info:
            question = self._create_pr_question()
        elif "diagram_type" in missing_info:
            question = "Bạn muốn tạo loại sơ đồ nào? Ví dụ: class diagram, architecture diagram? 📊"
        else:
            # Sử dụng suggested questions từ intent nếu có
            if intent.suggested_questions:
                question = intent.suggested_questions[0]
            else:
                question = "Bạn có thể cung cấp thêm thông tin không? 🤔"
        
        context.last_question = question
        
        return DialogResponse(
            message=question,
            state=DialogState.GATHERING_INFO
        )
    
    def _create_github_url_question(self, intent_type: IntentType) -> str:
        """Tạo câu hỏi về GitHub URL phù hợp với intent"""
        
        if intent_type == IntentType.SCAN_PROJECT:
            return """Tuyệt vời! Bạn muốn quét repository nào? 🔍

Vui lòng cung cấp GitHub URL, ví dụ:
• https://github.com/user/repo
• github.com/user/repo  
• user/repo"""
        
        elif intent_type == IntentType.REVIEW_PR:
            return """Được rồi! Bạn muốn review PR trong repository nào? 📝

Vui lòng cung cấp GitHub URL trước:
• https://github.com/user/repo
• github.com/user/repo
• user/repo"""
        
        else:
            return "Bạn có thể cung cấp GitHub URL của repository không? 🔗"
    
    def _create_pr_question(self) -> str:
        """Tạo câu hỏi về PR identifier"""
        return """Bạn muốn review PR nào? 🎯

Vui lòng cho tôi biết:
• PR number (ví dụ: #123, 123)
• Hoặc PR URL đầy đủ"""
    
    def _confirm_task_execution(self, context: DialogContext, 
                               intent: UserIntent) -> DialogResponse:
        """Xác nhận thông tin trước khi thực hiện task"""
        
        # Tạo thông điệp xác nhận
        if intent.intent_type == IntentType.SCAN_PROJECT:
            github_url = intent.get_github_url()
            confirmation_msg = f"""Được rồi! Tôi sẽ quét dự án cho bạn 🚀

📂 **Repository**: {github_url}
🔍 **Công việc**: Phân tích toàn bộ codebase

Tôi sẽ thực hiện:
✅ Clone repository
✅ Phát hiện ngôn ngữ lập trình  
✅ Xây dựng Code Knowledge Graph
✅ Phân tích kiến trúc và chất lượng code

Bạn có muốn tôi bắt đầu không? 😊"""
            
            task_params = {
                "task_type": "scan_project",
                "repository_url": github_url
            }
        
        elif intent.intent_type == IntentType.REVIEW_PR:
            github_url = intent.get_github_url()
            pr_id = intent.get_pr_identifier()
            confirmation_msg = f"""Tuyệt vời! Tôi sẽ review PR cho bạn 📝

📂 **Repository**: {github_url}
🎯 **Pull Request**: #{pr_id}

Tôi sẽ thực hiện:
✅ Phân tích thay đổi trong PR
✅ Kiểm tra tác động đến hệ thống
✅ Đánh giá chất lượng code
✅ Đưa ra nhận xét và gợi ý

Bạn có muốn tôi bắt đầu review không? 🔍"""
            
            task_params = {
                "task_type": "review_pr", 
                "repository_url": github_url,
                "pr_identifier": pr_id
            }
        
        else:
            confirmation_msg = "Tôi đã hiểu yêu cầu của bạn. Bạn có muốn tôi thực hiện không? ✨"
            task_params = {}
        
        return DialogResponse(
            message=confirmation_msg,
            state=DialogState.CONFIRMING,
            should_execute_task=True,
            task_params=task_params
        )
    
    def _handle_question_intent(self, intent: UserIntent) -> DialogResponse:
        """Xử lý câu hỏi từ người dùng"""
        return DialogResponse(
            message="Tôi hiểu bạn có câu hỏi! 💡 Tuy nhiên, để trả lời chính xác, tôi cần biết bạn đang hỏi về repository nào. Bạn có thể quét project trước rồi hỏi được không? 😊",
            state=DialogState.INITIAL,
            suggested_actions=["Quét project trước", "Cung cấp context"]
        )
    
    def _handle_diagram_request(self, intent: UserIntent) -> DialogResponse:
        """Xử lý yêu cầu tạo sơ đồ"""
        if not intent.get_github_url():
            return DialogResponse(
                message="Để tạo sơ đồ, tôi cần biết repository nào bạn muốn phân tích. Bạn có thể cung cấp GitHub URL không? 📊",
                state=DialogState.GATHERING_INFO
            )
        
        return DialogResponse(
            message="Tính năng tạo sơ đồ sẽ sớm có trong các phiên bản tiếp theo! 🎨 Hiện tại bạn có thể quét project để phân tích cấu trúc.",
            state=DialogState.INITIAL
        )
    
    def _generate_natural_response(self, context: str) -> str:
        """Tạo phản hồi tự nhiên bằng LLM"""
        
        prompt = f"""
Dựa trên ngữ cảnh sau, hãy tạo một phản hồi thân thiện và hữu ích:

{context}

Hãy trả lời một cách tự nhiên, thân thiện và đưa ra gợi ý cụ thể.
"""
        
        response = self.llm_client.call_openai(
            prompt=prompt,
            system_prompt=self.system_prompt,
            model="gpt-4o-mini",
            max_tokens=200,
            temperature=0.7
        )
        
        return response 