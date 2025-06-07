"""
Simplified LLM Intent Parser sử dụng OpenAI trực tiếp

Version đơn giản hóa để tránh dependency issues và sử dụng OpenAI trực tiếp
thay vì thông qua rule-based approach.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

# Try import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit
from services.llm_service_integration import UserLLMService
from shared.models.user_settings import APIKeyProvider


class IntentType(Enum):
    """Các loại ý định người dùng có thể có"""
    SCAN_PROJECT = "scan_project"
    REVIEW_PR = "review_pr"
    ASK_QUESTION = "ask_question"
    REQUEST_DIAGRAM = "request_diagram"
    CONFIGURE_SETTINGS = "configure_settings"
    UNKNOWN = "unknown"
    GREETING = "greeting"
    HELP = "help"


@dataclass
class UserIntent:
    """Thông tin ý định đã được phân tích"""
    intent_type: IntentType
    confidence: float  # 0.0 - 1.0
    extracted_entities: Dict[str, Any]
    missing_information: List[str]
    suggested_questions: List[str]
    original_text: str
    
    def is_complete(self) -> bool:
        """Kiểm tra xem ý định có đủ thông tin để thực hiện không"""
        return len(self.missing_information) == 0
    
    def get_github_url(self) -> Optional[str]:
        """Lấy GitHub URL từ entities đã trích xuất"""
        return self.extracted_entities.get('github_url')
    
    def get_pr_identifier(self) -> Optional[str]:
        """Lấy PR identifier từ entities đã trích xuất"""
        return self.extracted_entities.get('pr_identifier')


class SimplifiedLLMIntentParser:
    """
    Simplified intent parser sử dụng OpenAI trực tiếp.
    """
    
    def __init__(self, user_id: str = "user123"):
        """Initialize parser with user context."""
        self.logger = get_logger("team.interaction.simplified_llm_parser")
        self.user_id = user_id
        self.openai_client = None
        self.user_llm_service = UserLLMService()
        self._setup_openai()
        
        # Thiết lập logging cho OpenAI requests/responses
        self._setup_llm_logging()
        
        # Thiết kế prompt system chuyên nghiệp
        self.system_prompt = """Bạn là AI Assistant chuyên nghiệp phân tích ý định người dùng cho RepoChat - hệ thống review code tự động bằng tiếng Việt.

## NHIỆM VỤ CỐT LÕI
Phân tích chính xác ý định người dùng và đưa ra response phù hợp theo ngữ cảnh conversation tự nhiên.

## PHÂN LOẠI Ý ĐỊNH

### 1. SCAN_PROJECT (Quét toàn bộ dự án)
**Mô tả**: Người dùng muốn review/phân tích toàn bộ source code của một dự án
**Keywords**: "review code", "review dự án", "phân tích project", "quét source code", "review toàn bộ"
**Ví dụ user input**: 
- "tôi muốn review code của dự án"
- "review toàn bộ source code"
- "phân tích dự án này"

**Response chuẩn khi thiếu GitHub URL**:
"Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"

### 2. REVIEW_PR (Review Pull Request cụ thể)  
**Mô tả**: Người dùng muốn review một Pull Request cụ thể (PHẢI có PR ID/số)
**Keywords**: "PR #123", "pull request 456", "review PR"
**Response chuẩn**:
"Để review Pull Request, vui lòng cung cấp:
• URL repository
• ID hoặc URL của Pull Request

Ví dụ: Review PR #123 trong repository https://github.com/user/repo"

### 3. ASK_QUESTION, REQUEST_DIAGRAM, CONFIGURE_SETTINGS, GREETING, HELP, UNKNOWN
Các intent khác xử lý theo context thông thường.

## QUY TẮC PHÂN TÍCH QUAN TRỌNG

1. **Ưu tiên SCAN_PROJECT**: Nếu user nói về "review code" mà KHÔNG đề cập PR cụ thể → chọn scan_project
2. **Chỉ chọn REVIEW_PR**: Khi có đề cập RÕ RÀNG PR ID, số PR, hoặc "pull request" với số
3. **Response tự nhiên**: Đưa ra câu trả lời conversation như con người, không phải JSON
4. **Tiếng Việt thuần túy**: Tất cả response phải bằng tiếng Việt tự nhiên

## FORMAT TRẢ LỜI YÊU CẦU
Trả lời JSON với cấu trúc:
{
    "intent_type": "scan_project|review_pr|ask_question|request_diagram|configure_settings|greeting|help|unknown",
    "confidence": 0.95,
    "extracted_entities": {
        "github_url": "URL nếu có",
        "pr_identifier": "PR ID nếu có", 
        "project_name": "tên project nếu có"
    },
    "missing_information": ["github_url"],
    "suggested_questions": ["Response tự nhiên bằng tiếng Việt theo template trên"]
}

## EXAMPLES

Input: "tôi muốn review code của dự án"
→ intent_type: "scan_project"
→ suggested_questions: ["Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"]

Input: "review PR #123"  
→ intent_type: "review_pr"
→ suggested_questions: ["Để review Pull Request, vui lòng cung cấp:\\n• URL repository\\n• ID hoặc URL của Pull Request\\n\\nVí dụ: Review PR #123 trong repository https://github.com/user/repo"]"""
    
    def _setup_llm_logging(self):
        """Thiết lập logging để ghi OpenAI requests/responses vào file."""
        # Đường dẫn tuyệt đối từ backend root
        backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        logs_dir = os.path.join(backend_root, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # File log riêng cho LLM interactions
        self.llm_log_file = os.path.join(logs_dir, "llm_interactions.log")
        
        # Logger riêng cho LLM interactions
        self.llm_logger = get_logger("llm.interactions")
        
        # Tạo file nếu chưa có và ghi header
        if not os.path.exists(self.llm_log_file):
            try:
                with open(self.llm_log_file, "w", encoding="utf-8") as f:
                    f.write(f"LLM INTERACTIONS LOG - Created: {datetime.now().isoformat()}\n")
                    f.write("="*80 + "\n\n")
            except Exception as e:
                self.logger.error(f"Failed to create LLM log file: {e}")
        
        self.logger.info(f"LLM logging initialized. Log file: {self.llm_log_file}")
        self.logger.info(f"Logs dir: {logs_dir}, exists: {os.path.exists(logs_dir)}")
    
    def _log_llm_interaction(self, 
                            user_input: str, 
                            system_prompt: str, 
                            user_prompt: str, 
                            llm_response: str, 
                            parsed_result: Optional[Dict] = None,
                            error: Optional[str] = None):
        """
        Log chi tiết interaction với LLM vào file.
        
        Args:
            user_input: Input từ user
            system_prompt: System prompt gửi lên LLM
            user_prompt: User prompt gửi lên LLM  
            llm_response: Response từ LLM
            parsed_result: Kết quả đã parse (nếu có)
            error: Lỗi nếu có
        """
        timestamp = datetime.now().isoformat()
        
        interaction_data = {
            "timestamp": timestamp,
            "user_input": user_input,
            "prompts": {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt
            },
            "llm_response": llm_response,
            "parsed_result": parsed_result,
            "error": error,
            "success": error is None
        }
        
        # Log ra console
        self.llm_logger.info(f"LLM Interaction - User: {user_input[:100]}... | Success: {error is None}")
        if error:
            self.llm_logger.error(f"LLM Error: {error}")
        
        # Ghi vào file
        try:
            with open(self.llm_log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                f.write(f"{'='*80}\n")
                f.write(f"USER INPUT:\n{user_input}\n")
                f.write(f"\n{'-'*40} SYSTEM PROMPT {'-'*40}\n")
                f.write(f"{system_prompt}\n")
                f.write(f"\n{'-'*40} USER PROMPT {'-'*40}\n")
                f.write(f"{user_prompt}\n")
                f.write(f"\n{'-'*40} LLM RESPONSE {'-'*40}\n")
                f.write(f"{llm_response}\n")
                if parsed_result:
                    f.write(f"\n{'-'*40} PARSED RESULT {'-'*40}\n")
                    f.write(f"{json.dumps(parsed_result, ensure_ascii=False, indent=2)}\n")
                if error:
                    f.write(f"\n{'-'*40} ERROR {'-'*40}\n")
                    f.write(f"{error}\n")
                f.write(f"{'='*80}\n\n")
        except Exception as e:
            self.logger.error(f"Failed to write LLM interaction to file: {e}")
    
    def _setup_openai(self):
        """Setup OpenAI client using user's API key."""
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI library not available")
            return
        
        try:
            # Try to get user's OpenAI provider first
            user_provider = self.user_llm_service.create_openai_provider(self.user_id)
            if user_provider and user_provider.client:
                self.openai_client = user_provider.client
                self.user_model = user_provider.config.model
                self.user_temperature = user_provider.config.temperature
                self.user_max_tokens = user_provider.config.max_tokens
                self.logger.info(f"Using user's OpenAI API key with model: {self.user_model}")
                return
            
            # Fallback to environment variable for system default
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.user_model = "gpt-4o-mini"  # Default model
                self.user_temperature = 0.1
                self.user_max_tokens = 500
                self.logger.info("Using system OpenAI API key (fallback)")
            else:
                self.logger.warning(f"No OpenAI API key found for user {self.user_id} or in environment")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def parse_user_intent(self, user_text: str) -> UserIntent:
        """
        Parse user intent sử dụng OpenAI LLM hoặc fallback logic.
        
        Args:
            user_text: Câu nói của người dùng
            
        Returns:
            UserIntent object
        """
        log_function_entry(self.logger, "parse_user_intent", user_text=user_text[:100])
        
        try:
            # Thử gọi OpenAI trước
            if self.openai_client:
                intent = self._parse_with_openai(user_text)
                if intent:
                    log_function_exit(self.logger, "parse_user_intent", result="openai_success")
                    return intent
            
            # Fallback với logic cải thiện
            self.logger.info("Using enhanced fallback logic")
            intent = self._enhanced_fallback_parse(user_text)
            
            log_function_exit(self.logger, "parse_user_intent", result="fallback_success")
            return intent
            
        except Exception as e:
            self.logger.error(f"Error in parse_user_intent: {e}", exc_info=True)
            return self._create_error_intent(user_text)
    
    def _parse_with_openai(self, user_text: str) -> Optional[UserIntent]:
        """Parse intent với OpenAI."""
        user_prompt = f"""Phân tích ý định người dùng sau đây và trả lời theo format JSON đã chỉ định:

User Input: "{user_text}"

Yêu cầu: Trả về JSON chính xác theo format đã định, đặc biệt chú ý:
- Nếu user nói về "review code/dự án" mà KHÔNG đề cập PR cụ thể → chọn "scan_project" 
- Response phải tự nhiên và phù hợp context conversation tiếng Việt"""

        try:
            response = self.openai_client.chat.completions.create(
                model=getattr(self, 'user_model', "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=getattr(self, 'user_temperature', 0.1),
                max_tokens=getattr(self, 'user_max_tokens', 500)
            )
            
            if response.choices and len(response.choices) > 0:
                llm_response = response.choices[0].message.content
                
                # Parse response
                parsed_result = self._parse_llm_response(user_text, llm_response)
                
                # Log interaction
                parsed_dict = None
                if parsed_result:
                    parsed_dict = {
                        "intent_type": parsed_result.intent_type.value if parsed_result.intent_type else None,
                        "confidence": parsed_result.confidence,
                        "extracted_entities": parsed_result.extracted_entities,
                        "missing_information": parsed_result.missing_information,
                        "suggested_questions": parsed_result.suggested_questions,
                        "original_text": parsed_result.original_text
                    }
                
                self._log_llm_interaction(
                    user_input=user_text,
                    system_prompt=self.system_prompt,
                    user_prompt=user_prompt,
                    llm_response=llm_response,
                    parsed_result=parsed_dict
                )
                
                return parsed_result
            else:
                error_msg = "No response choices from OpenAI"
                self._log_llm_interaction(
                    user_input=user_text,
                    system_prompt=self.system_prompt,
                    user_prompt=user_prompt,
                    llm_response="",
                    error=error_msg
                )
                return None
            
        except Exception as e:
            error_msg = f"OpenAI request failed: {e}"
            self.logger.error(error_msg)
            
            # Log failed interaction
            self._log_llm_interaction(
                user_input=user_text,
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                llm_response="",
                error=error_msg
            )
            return None
    
    def _parse_llm_response(self, original_text: str, llm_response: str) -> Optional[UserIntent]:
        """Parse LLM response thành UserIntent."""
        try:
            # Tìm JSON trong response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                data = json.loads(llm_response)
            
            # Tạo UserIntent
            intent_type = IntentType(data.get("intent_type", "unknown"))
            
            return UserIntent(
                intent_type=intent_type,
                confidence=float(data.get("confidence", 0.8)),
                extracted_entities=data.get("extracted_entities", {}),
                missing_information=data.get("missing_information", []),
                suggested_questions=data.get("suggested_questions", []),
                original_text=original_text
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            return None
    
    def _enhanced_fallback_parse(self, user_text: str) -> UserIntent:
        """Enhanced fallback parsing logic."""
        text_lower = user_text.lower()
        
        # Logic giống như đã test thành công
        if any(word in text_lower for word in ['review code', 'review dự án', 'phân tích dự án', 'review toàn bộ']):
            return UserIntent(
                intent_type=IntentType.SCAN_PROJECT,
                confidence=0.85,
                extracted_entities={},
                missing_information=["github_url"],
                suggested_questions=["Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"],
                original_text=user_text
            )
        elif any(pattern in text_lower for pattern in ['pr #', 'pull request #', 'review pr']) or re.search(r'pull request \d+|pr \d+', text_lower):
            return UserIntent(
                intent_type=IntentType.REVIEW_PR,
                confidence=0.85,
                extracted_entities={},
                missing_information=["github_url", "pr_identifier"],
                suggested_questions=["Để review Pull Request, vui lòng cung cấp:\n• URL repository\n• ID hoặc URL của Pull Request\n\nVí dụ: Review PR #123 trong repository https://github.com/user/repo"],
                original_text=user_text
            )
        elif any(word in text_lower for word in ['xin chào', 'hello', 'hi', 'chào']):
            return UserIntent(
                intent_type=IntentType.GREETING,
                confidence=0.9,
                extracted_entities={},
                missing_information=[],
                suggested_questions=["Chào bạn! Tôi có thể giúp gì cho bạn? Bạn muốn quét project hay review PR?"],
                original_text=user_text
            )
        else:
            return UserIntent(
                intent_type=IntentType.UNKNOWN,
                confidence=0.5,
                extracted_entities={},
                missing_information=[],
                suggested_questions=["Bạn có thể nói rõ hơn về điều bạn muốn làm không?"],
                original_text=user_text
            )
    
    def _create_error_intent(self, user_text: str) -> UserIntent:
        """Tạo intent khi có lỗi."""
        return UserIntent(
            intent_type=IntentType.UNKNOWN,
            confidence=0.0,
            extracted_entities={},
            missing_information=[],
            suggested_questions=["Xin lỗi, có lỗi xảy ra khi phân tích yêu cầu của bạn. Vui lòng thử lại."],
            original_text=user_text
        )
    
    def is_available(self) -> bool:
        """Kiểm tra parser có sẵn sàng không."""
        return True  # Luôn sẵn sàng với fallback logic 