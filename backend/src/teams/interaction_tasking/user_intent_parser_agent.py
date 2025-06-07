"""
User Intent Parser Agent cho TEAM Interaction & Tasking

Agent này chịu trách nhiệm phân tích ý định của người dùng sử dụng OpenAI LLM.
Nó sẽ:
- Hiểu yêu cầu người dùng bằng tiếng Việt và tiếng Anh
- Trích xuất thông tin cần thiết như GitHub URL, PR ID
- Phân loại loại tác vụ (scan project, review PR, Q&A)
- Xác định các thông tin thiếu cần hỏi người dùng
"""

import json
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit
from .simplified_llm_intent_parser import SimplifiedLLMIntentParser


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


class UserIntentParserAgent:
    """
    Agent phân tích ý định người dùng sử dụng OpenAI LLM.
    
    Chức năng chính:
    - Phân tích câu nói của người dùng để hiểu ý định
    - Trích xuất thông tin cần thiết (URL, ID, v.v.)
    - Xác định thông tin còn thiếu
    - Đề xuất câu hỏi làm rõ
    """
    
    def __init__(self):
        """Khởi tạo User Intent Parser Agent với LLM support"""
        self.logger = get_logger("team.interaction.intent_parser")
        self.llm_parser = SimplifiedLLMIntentParser()

    
    def parse_user_intent(self, user_text: str) -> UserIntent:
        """
        Phân tích ý định của người dùng từ text input sử dụng LLM-based approach.
        
        Args:
            user_text: Câu nói của người dùng
            
        Returns:
            UserIntent object chứa kết quả phân tích
        """
        log_function_entry(self.logger, "parse_user_intent", user_text=user_text[:100])
        
        try:
            # Delegate hoàn toàn sang SimplifiedLLMIntentParser
            user_intent = self.llm_parser.parse_user_intent(user_text)
            
            self.logger.info(f"LLM phân tích ý định thành công: {user_intent.intent_type.value}, confidence: {user_intent.confidence}")
            
            log_function_exit(self.logger, "parse_user_intent", result="success")
            return user_intent
            
        except Exception as e:
            self.logger.error(f"Lỗi khi phân tích ý định: {e}", exc_info=True)
            
            # Fallback nếu có lỗi
            return UserIntent(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                extracted_entities={},
                missing_information=[],
                suggested_questions=["Xin lỗi, có lỗi xảy ra khi phân tích yêu cầu của bạn. Vui lòng thử lại."],
                original_text=user_text
            )
    

    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response từ LLM"""
        try:
            # Tìm JSON trong response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Nếu không tìm thấy JSON, parse toàn bộ response
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            self.logger.warning(f"Không thể parse JSON từ LLM response: {e}")
            self.logger.debug(f"LLM response: {response}")
            
            # Fallback parsing
            return self._fallback_parse_response(response)
    
    def _fallback_parse_response(self, response: str) -> Dict[str, Any]:
        """Fallback parsing khi JSON parsing thất bại"""
        # Cố gắng phân tích bằng regex
        intent_data = {
            "intent_type": "unknown",
            "confidence": 0.5,
            "extracted_entities": {},
            "missing_information": ["Không thể phân tích ý định"],
            "suggested_questions": ["Bạn có thể nói rõ hơn về điều bạn muốn làm không?"]
        }
        
        # Tìm GitHub URL
        github_patterns = [
            r'https?://github\.com/([^/\s]+)/([^/\s]+)',
            r'github\.com/([^/\s]+)/([^/\s]+)',
            r'([^/\s]+)/([^/\s]+)'  # user/repo format
        ]
        
        for pattern in github_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    user, repo = match.groups()[:2]
                    intent_data["extracted_entities"]["github_url"] = f"https://github.com/{user}/{repo}"
                    break
        
        return intent_data
    
    def _create_user_intent(self, original_text: str, intent_data: Dict[str, Any]) -> UserIntent:
        """Tạo UserIntent object từ data đã parse"""
        try:
            intent_type = IntentType(intent_data.get("intent_type", "unknown"))
        except ValueError:
            intent_type = IntentType.UNKNOWN
        
        return UserIntent(
            intent_type=intent_type,
            confidence=float(intent_data.get("confidence", 0.5)),
            extracted_entities=intent_data.get("extracted_entities", {}),
            missing_information=intent_data.get("missing_information", []),
            suggested_questions=intent_data.get("suggested_questions", []),
            original_text=original_text
        )
    
    def _post_process_intent(self, user_intent: UserIntent) -> UserIntent:
        """Post-process để cải thiện kết quả phân tích"""
        
        # Normalize GitHub URL
        github_url = user_intent.extracted_entities.get('github_url')
        if github_url:
            normalized_url = self._normalize_github_url(github_url)
            user_intent.extracted_entities['github_url'] = normalized_url
        
        # Validate và clean up extracted entities
        user_intent.extracted_entities = self._validate_entities(user_intent.extracted_entities)
        
        # Cập nhật missing information dựa trên intent type
        user_intent.missing_information = self._update_missing_information(user_intent)
        
        return user_intent
    
    def _normalize_github_url(self, url: str) -> str:
        """Chuẩn hóa GitHub URL về format đầy đủ"""
        url = url.strip()
        
        # Nếu đã là URL đầy đủ
        if url.startswith('https://github.com/'):
            return url
        
        # Nếu thiếu https://
        if url.startswith('github.com/'):
            return f"https://{url}"
        
        # Nếu chỉ có user/repo
        if '/' in url and not url.startswith('http') and '.' not in url.split('/')[0]:
            return f"https://github.com/{url}"
        
        return url
    
    def _validate_entities(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Validate và clean up extracted entities"""
        validated = {}
        
        # Validate GitHub URL
        github_url = entities.get('github_url')
        if github_url and self._is_valid_github_url(github_url):
            validated['github_url'] = github_url
        
        # Validate PR identifier
        pr_id = entities.get('pr_identifier')
        if pr_id:
            validated['pr_identifier'] = str(pr_id)
        
        # Copy các entities khác
        for key, value in entities.items():
            if key not in ['github_url', 'pr_identifier'] and value:
                validated[key] = value
        
        return validated
    
    def _is_valid_github_url(self, url: str) -> bool:
        """Kiểm tra xem URL có phải là GitHub URL hợp lệ không"""
        github_pattern = r'^https://github\.com/[^/\s]+/[^/\s]+/?$'
        return bool(re.match(github_pattern, url))
    
    def _update_missing_information(self, user_intent: UserIntent) -> List[str]:
        """Cập nhật danh sách thông tin thiếu dựa trên intent type"""
        missing = []
        
        if user_intent.intent_type == IntentType.SCAN_PROJECT:
            if not user_intent.get_github_url():
                missing.append("github_url")
        
        elif user_intent.intent_type == IntentType.REVIEW_PR:
            if not user_intent.get_github_url():
                missing.append("github_url")
            if not user_intent.get_pr_identifier():
                missing.append("pr_identifier")
        
        elif user_intent.intent_type == IntentType.REQUEST_DIAGRAM:
            if not user_intent.get_github_url():
                missing.append("github_url")
            if 'diagram_type' not in user_intent.extracted_entities:
                missing.append("diagram_type")
        
        return missing
    
    def _create_enhanced_fallback_intent(self, user_text: str) -> UserIntent:
        """Tạo intent mặc định khi phân tích thất bại"""
        
        # Cố gắng phân tích đơn giản bằng keyword matching
        text_lower = user_text.lower()
        
        intent_type = IntentType.UNKNOWN
        entities = {}
        missing_info = []
        questions = ["Bạn có thể nói rõ hơn về điều bạn muốn làm không?"]
        
        # Detect intent dựa trên keywords - ưu tiên SCAN_PROJECT cho review code chung
        if any(word in text_lower for word in ['review code', 'review source', 'review dự án', 'review project', 'phân tích code', 'phân tích dự án', 'quét dự án', 'quét project', 'review toàn bộ']):
            intent_type = IntentType.SCAN_PROJECT
            missing_info = ["github_url"]
            questions = ["Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"]
        
        elif any(word in text_lower for word in ['scan', 'quét', 'phân tích', 'analyze']) and 'pr' not in text_lower:
            intent_type = IntentType.SCAN_PROJECT
            missing_info = ["github_url"]
            questions = ["Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"]
        
        # Tìm PR với số cụ thể
        elif any(pattern in text_lower for pattern in ['pr #', 'pull request #', 'review pr']) or re.search(r'pull request \d+|pr \d+', text_lower):
            intent_type = IntentType.REVIEW_PR  
            missing_info = ["github_url", "pr_identifier"]
            questions = ["Để review Pull Request, vui lòng cung cấp:\n• URL repository\n• ID hoặc URL của Pull Request\n\nVí dụ: Review PR #123 trong repository https://github.com/user/repo"]
        
        elif any(word in text_lower for word in ['hỏi', 'gì', 'như thế nào', 'tại sao']):
            intent_type = IntentType.ASK_QUESTION
        
        elif any(word in text_lower for word in ['xin chào', 'hello', 'hi', 'chào']):
            intent_type = IntentType.GREETING
            questions = ["Chào bạn! Tôi có thể giúp gì cho bạn? Bạn muốn quét project hay review PR?"]
        
        # Fallback cho "review" chung chung -> SCAN_PROJECT
        elif 'review' in text_lower and 'pr' not in text_lower and '#' not in text_lower:
            intent_type = IntentType.SCAN_PROJECT
            missing_info = ["github_url"]
            questions = ["Chào bạn! source code của bạn được lưa ở đâu, hiện nay chúng tôi chỉ có chức năng review code tại github repository"]
        
        # Tìm GitHub URL bằng regex
        github_patterns = [
            r'https?://github\.com/([^/\s]+)/([^/\s]+)',
            r'github\.com/([^/\s]+)/([^/\s]+)',
        ]
        
        for pattern in github_patterns:
            match = re.search(pattern, user_text, re.IGNORECASE)
            if match:
                entities['github_url'] = self._normalize_github_url(match.group(0))
                if 'github_url' in missing_info:
                    missing_info.remove('github_url')
                break
        
        return UserIntent(
            intent_type=intent_type,
            confidence=0.6,  # Confidence thấp hơn cho fallback
            extracted_entities=entities,
            missing_information=missing_info,
            suggested_questions=questions,
            original_text=user_text
        ) 