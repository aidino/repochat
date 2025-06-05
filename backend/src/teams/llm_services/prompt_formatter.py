"""
PromptFormatterModule for Task 3.4 (F3.4)

Cung cấp formatting prompts với template system cho TEAM LLM Services.
Hỗ trợ load templates từ markdown files và khả năng mở rộng.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .models import PromptTemplate
from .template_loader import TemplateLoader, create_template_loader

logger = logging.getLogger(__name__)

class TemplateType(Enum):
    """Enum cho các loại template được hỗ trợ."""
    EXPLAIN_CODE = "explain_code"
    ANALYZE_FUNCTION = "analyze_function"
    REVIEW_CHANGES = "review_changes"
    FIND_ISSUES = "find_issues"
    SUGGEST_IMPROVEMENTS = "suggest_improvements"
    DOCUMENTATION = "documentation"

@dataclass
class FormattingError:
    """Lớp đại diện cho lỗi formatting."""
    error_type: str
    message: str
    template_id: Optional[str] = None
    missing_variables: List[str] = field(default_factory=list)
    extra_variables: List[str] = field(default_factory=list)

@dataclass
class FormattingResult:
    """Kết quả của quá trình formatting."""
    success: bool
    formatted_prompt: Optional[str] = None
    error: Optional[FormattingError] = None
    template_used: Optional[str] = None
    variables_used: Dict[str, Any] = field(default_factory=dict)

class PromptFormatterModule:
    """
    Module format prompt templates với context data.
    
    Features:
    - Load templates từ markdown files
    - Format templates với context data
    - Validate input data và template variables
    - Template versioning và management
    """
    
    def __init__(self, templates_directory: Optional[str] = None):
        """
        Khởi tạo PromptFormatterModule với template loader.
        
        Args:
            templates_directory: Optional path to templates directory
        """
        logger.info("Initializing PromptFormatterModule...")
        
        # Initialize template loader
        self.template_loader = create_template_loader(templates_directory)
        
        # Load templates from files
        self._templates: Dict[str, PromptTemplate] = {}
        self._load_templates_from_files()
        
        logger.info(f"PromptFormatterModule initialized with {len(self._templates)} templates")
    
    def _load_templates_from_files(self) -> None:
        """Load all templates từ markdown files."""
        try:
            result = self.template_loader.load_all_templates()
            
            if result.success and result.templates_loaded:
                # Store templates in dictionary for quick access
                for template in result.templates_loaded:
                    self._templates[template.template_id] = template
                    logger.debug(f"Loaded template: {template.template_id}")
                
                logger.info(f"Successfully loaded {len(result.templates_loaded)} templates from files")
            else:
                logger.warning("No templates loaded from files, falling back to hardcoded templates")
                self._initialize_fallback_templates()
                
            # Log any loading errors
            if result.errors:
                for error in result.errors:
                    logger.error(f"Template loading error in {error.file_path}: {error.message}")
                    
        except Exception as e:
            logger.error(f"Error loading templates from files: {str(e)}")
            logger.info("Falling back to hardcoded templates")
            self._initialize_fallback_templates()
    
    def _initialize_fallback_templates(self) -> None:
        """Initialize fallback hardcoded templates if file loading fails."""
        logger.info("Initializing fallback hardcoded templates...")
        
        # Fallback explain_code template
        explain_code_template = PromptTemplate(
            template_id="explain_code",
            name="Giải thích Code (Fallback)",
            description="Fallback template để giải thích chức năng của đoạn code",
            template_text="""Hãy giải thích chức năng của đoạn code sau một cách chi tiết và dễ hiểu:

```{language}
{code_snippet}
```

Vui lòng bao gồm:
1. Tổng quan về chức năng chính
2. Giải thích từng phần quan trọng
3. Input và output (nếu có)
4. Các logic xử lý đặc biệt
5. Potential issues hoặc considerations

Trả lời bằng tiếng Việt.""",
            required_variables=["code_snippet"],
            optional_variables=["language"],
            default_values={"language": "python"}
        )
        
        self._templates[explain_code_template.template_id] = explain_code_template
        logger.info("Fallback templates initialized")

    def format_prompt(self, template_id: str, context_data: Dict[str, Any]) -> FormattingResult:
        """
        Format một template với context data.
        
        Args:
            template_id: ID của template cần format
            context_data: Dictionary chứa data để điền vào template
            
        Returns:
            FormattingResult: Kết quả formatting
        """
        logger.debug(f"Formatting prompt with template_id='{template_id}', context_data keys={list(context_data.keys())}")
        
        try:
            # Validate template exists
            if template_id not in self._templates:
                error = FormattingError(
                    error_type="TEMPLATE_NOT_FOUND",
                    message=f"Template '{template_id}' not found",
                    template_id=template_id
                )
                logger.error(f"Template not found: {template_id}")
                return FormattingResult(success=False, error=error)
            
            template = self._templates[template_id]
            
            # Validate required variables
            missing_vars = []
            for var in template.required_variables:
                if var not in context_data:
                    missing_vars.append(var)
            
            if missing_vars:
                error = FormattingError(
                    error_type="MISSING_VARIABLES",
                    message=f"Missing required variables: {missing_vars}",
                    template_id=template_id,
                    missing_variables=missing_vars
                )
                logger.error(f"Missing variables for template {template_id}: {missing_vars}")
                return FormattingResult(success=False, error=error)
            
            # Prepare data with defaults
            format_data = context_data.copy()
            
            # Add default values for missing optional variables
            if template.default_values:
                for var, default_value in template.default_values.items():
                    if var not in format_data:
                        format_data[var] = default_value
                        logger.debug(f"Using default value for '{var}': {default_value}")
            
            # Check for extra variables (warning only)
            all_expected_vars = set(template.required_variables + template.optional_variables)
            extra_vars = [var for var in format_data.keys() if var not in all_expected_vars]
            if extra_vars:
                logger.warning(f"Extra variables provided for template {template_id}: {extra_vars}")
            
            # Format template
            try:
                formatted_prompt = template.template_text.format(**format_data)
                
                result = FormattingResult(
                    success=True,
                    formatted_prompt=formatted_prompt,
                    template_used=template_id,
                    variables_used=format_data
                )
                
                logger.info(f"Successfully formatted template '{template_id}' (length: {len(formatted_prompt)})")
                return result
                
            except KeyError as e:
                error = FormattingError(
                    error_type="FORMATTING_ERROR",
                    message=f"Template formatting failed: missing variable {str(e)}",
                    template_id=template_id
                )
                logger.error(f"Template formatting failed for {template_id}: {str(e)}")
                return FormattingResult(success=False, error=error)
                
            except Exception as e:
                error = FormattingError(
                    error_type="UNEXPECTED_ERROR",
                    message=f"Unexpected formatting error: {str(e)}",
                    template_id=template_id
                )
                logger.error(f"Unexpected error formatting template {template_id}: {str(e)}")
                return FormattingResult(success=False, error=error)
        
        except Exception as e:
            error = FormattingError(
                error_type="SYSTEM_ERROR",
                message=f"System error during formatting: {str(e)}",
                template_id=template_id
            )
            logger.error(f"System error in format_prompt: {str(e)}")
            return FormattingResult(success=False, error=error)
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        Lấy template theo ID.
        
        Args:
            template_id: ID của template
            
        Returns:
            PromptTemplate hoặc None nếu không tìm thấy
        """
        return self._templates.get(template_id)
    
    def list_templates(self) -> List[PromptTemplate]:
        """
        Lấy danh sách tất cả templates.
        
        Returns:
            List[PromptTemplate]: Danh sách templates
        """
        return list(self._templates.values())
    
    def reload_templates(self) -> bool:
        """
        Reload tất cả templates từ files.
        
        Returns:
            bool: True nếu reload thành công
        """
        logger.info("Reloading all templates from files...")
        try:
            old_count = len(self._templates)
            self._templates.clear()
            self._load_templates_from_files()
            new_count = len(self._templates)
            
            logger.info(f"Templates reloaded: {old_count} -> {new_count}")
            return True
        except Exception as e:
            logger.error(f"Error reloading templates: {str(e)}")
            return False
    
    def reload_template(self, template_id: str) -> bool:
        """
        Reload một template cụ thể từ file.
        
        Args:
            template_id: ID của template cần reload
            
        Returns:
            bool: True nếu reload thành công
        """
        try:
            template = self.template_loader.reload_template(template_id)
            if template:
                self._templates[template_id] = template
                logger.info(f"Template '{template_id}' reloaded successfully")
                return True
            else:
                logger.warning(f"Template '{template_id}' not found for reload")
                return False
        except Exception as e:
            logger.error(f"Error reloading template '{template_id}': {str(e)}")
            return False

    def add_template(self, template: PromptTemplate) -> bool:
        """
        Thêm template mới.
        
        Args:
            template: PromptTemplate object
            
        Returns:
            bool: True nếu thêm thành công
        """
        try:
            if template.template_id in self._templates:
                logger.warning(f"Template '{template.template_id}' already exists, will be replaced")
            
            self._templates[template.template_id] = template
            logger.info(f"Template '{template.template_id}' added successfully")
            return True
        except Exception as e:
            logger.error(f"Error adding template: {str(e)}")
            return False
    
    def remove_template(self, template_id: str) -> bool:
        """
        Xóa template.
        
        Args:
            template_id: ID của template cần xóa
            
        Returns:
            bool: True nếu xóa thành công
        """
        try:
            if template_id in self._templates:
                del self._templates[template_id]
                logger.info(f"Template '{template_id}' removed successfully")
                return True
            else:
                logger.warning(f"Template '{template_id}' not found for removal")
                return False
        except Exception as e:
            logger.error(f"Error removing template '{template_id}': {str(e)}")
            return False
    
    def validate_context_data(self, template_id: str, context_data: Dict[str, Any]) -> FormattingResult:
        """
        Validate context data cho một template mà không format.
        
        Args:
            template_id: ID của template
            context_data: Data cần validate
            
        Returns:
            FormattingResult: Kết quả validation
        """
        if template_id not in self._templates:
            error = FormattingError(
                error_type="TEMPLATE_NOT_FOUND",
                message=f"Template '{template_id}' not found",
                template_id=template_id
            )
            return FormattingResult(success=False, error=error)
        
        template = self._templates[template_id]
        
        # Check required variables
        missing_vars = [var for var in template.required_variables if var not in context_data]
        if missing_vars:
            error = FormattingError(
                error_type="MISSING_VARIABLES",
                message=f"Missing required variables: {missing_vars}",
                template_id=template_id,
                missing_variables=missing_vars
            )
            return FormattingResult(success=False, error=error)
        
        # Check for extra variables
        all_expected_vars = set(template.required_variables + template.optional_variables)
        extra_vars = [var for var in context_data.keys() if var not in all_expected_vars]
        
        return FormattingResult(
            success=True,
            template_used=template_id,
            variables_used=context_data,
            error=FormattingError(
                error_type="WARNING",
                message=f"Extra variables: {extra_vars}",
                template_id=template_id,
                extra_variables=extra_vars
            ) if extra_vars else None
        )
    
    def get_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin chi tiết về template.
        
        Args:
            template_id: ID của template
            
        Returns:
            Dict chứa thông tin template hoặc None
        """
        if template_id not in self._templates:
            return None
        
        template = self._templates[template_id]
        return {
            "template_id": template.template_id,
            "name": template.name,
            "description": template.description,
            "version": template.version,
            "category": template.category,
            "required_variables": template.required_variables,
            "optional_variables": template.optional_variables,
            "default_values": template.default_values,
            "template_length": len(template.template_text),
            "tags": template.tags,
            "created_at": template.created_at.isoformat() if hasattr(template, 'created_at') and template.created_at else None
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê về templates.
        
        Returns:
            Dict chứa thống kê
        """
        templates = list(self._templates.values())
        
        # Count by category
        categories = {}
        for template in templates:
            category = getattr(template, 'category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_templates": len(templates),
            "valid_templates": len([t for t in templates if hasattr(t, 'template_text') and t.template_text]),
            "categories": categories,
            "template_ids": [t.template_id for t in templates],
            "loader_info": self.template_loader.get_template_info() if self.template_loader else None
        }

# Convenience functions
def create_prompt_formatter(templates_directory: Optional[str] = None) -> PromptFormatterModule:
    """
    Tạo instance của PromptFormatterModule.
    
    Args:
        templates_directory: Optional path to templates directory
        
    Returns:
        PromptFormatterModule instance
    """
    return PromptFormatterModule(templates_directory)

def format_explain_code_prompt(code_snippet: str, language: str = "python") -> FormattingResult:
    """
    Convenience function để format explain_code prompt.
    
    Args:
        code_snippet: Code để giải thích
        language: Programming language
        
    Returns:
        FormattingResult
    """
    formatter = create_prompt_formatter()
    return formatter.format_prompt("explain_code", {
        "code_snippet": code_snippet,
        "language": language
    })

def get_available_templates() -> List[str]:
    """
    Lấy danh sách template IDs có sẵn.
    
    Returns:
        List[str]: Danh sách template IDs
    """
    formatter = create_prompt_formatter()
    return [template.template_id for template in formatter.list_templates()] 