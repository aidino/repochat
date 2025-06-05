"""
Project Data Context Models for RepoChat v1.0

Defines the data structure that encapsulates the result of data acquisition phase,
containing cloned repository path and detected programming languages.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
import os


@dataclass
class PRDiffInfo:
    """
    Information về PR diff cho Task 3.7.
    
    Chứa thông tin về changes trong một Pull Request,
    bao gồm file changes và function/method changes.
    """
    pr_id: Optional[str] = None
    """PR ID hoặc number"""
    
    pr_url: Optional[str] = None
    """URL của PR (nếu có)"""
    
    base_branch: Optional[str] = None
    """Branch base của PR"""
    
    head_branch: Optional[str] = None  
    """Branch head của PR"""
    
    raw_diff: Optional[str] = None
    """Raw diff content từ git"""
    
    changed_files: List[str] = None
    """List các file paths đã thay đổi"""
    
    file_changes: Dict[str, Dict[str, Any]] = None
    """Detailed changes per file: {file_path: {added_lines, deleted_lines, chunks}}"""
    
    function_changes: List[Dict[str, Any]] = None
    """List các function/method changes: [{file, function_name, change_type, line_start, line_end}]"""
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.changed_files is None:
            self.changed_files = []
        if self.file_changes is None:
            self.file_changes = {}
        if self.function_changes is None:
            self.function_changes = []


class ProjectDataContext(BaseModel):
    """
    Context data for a project after data acquisition phase completion.
    
    Encapsulates the results from GitOperationsModule and LanguageIdentifierModule,
    providing a standardized way to pass data between TEAM agents.
    """
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    cloned_code_path: str = Field(
        ...,
        description="Absolute path to the cloned repository directory",
        min_length=1
    )
    """Absolute path to the cloned repository directory"""
    
    detected_languages: List[str] = Field(
        default_factory=list,
        description="List of programming languages detected in the repository"
    )
    """List of programming languages detected in the repository"""
    
    # Additional metadata fields for context
    repository_url: Optional[str] = None
    """Original repository URL that was cloned"""
    
    repository_stats: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Repository statistics from GitOperationsModule"
    )
    """Repository statistics (size, commit info, etc.)"""
    
    language_statistics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Detailed language analysis statistics"
    )
    """Detailed language analysis statistics from LanguageIdentifierModule"""
    
    analysis_timestamp: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Timestamp when the analysis was completed"
    )
    """Timestamp when the data acquisition analysis was completed"""
    
    acquisition_duration_ms: Optional[float] = None
    """Duration of the data acquisition phase in milliseconds"""
    
    # Task 3.7: PR Diff Information
    pr_diff_info: Optional[PRDiffInfo] = None
    """PR diff information for impact analysis (Task 3.7)"""
    
    @field_validator('cloned_code_path')
    @classmethod
    def validate_cloned_path(cls, v):
        """Validate that the cloned code path exists and is a directory"""
        if not v or not isinstance(v, str):
            raise ValueError("cloned_code_path must be a non-empty string")
        
        # Note: We validate path format but not existence since path might be
        # cleaned up by the time we validate this object in some scenarios
        if not os.path.isabs(v):
            raise ValueError("cloned_code_path must be an absolute path")
            
        return v
    
    @field_validator('detected_languages')
    @classmethod
    def validate_languages(cls, v):
        """Validate detected languages list"""
        if not isinstance(v, list):
            raise ValueError("detected_languages must be a list")
        
        # Normalize languages to lowercase for consistency
        normalized = [lang.lower().strip() for lang in v if lang and isinstance(lang, str)]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_languages = []
        for lang in normalized:
            if lang not in seen:
                seen.add(lang)
                unique_languages.append(lang)
        
        return unique_languages
    
    @property
    def has_languages(self) -> bool:
        """Check if any languages were detected"""
        return len(self.detected_languages) > 0
    
    @property
    def primary_language(self) -> Optional[str]:
        """Get the primary (first detected) language"""
        return self.detected_languages[0] if self.detected_languages else None
    
    @property
    def language_count(self) -> int:
        """Get the number of detected languages"""
        return len(self.detected_languages)
    
    def has_language(self, language: str) -> bool:
        """Check if a specific language was detected"""
        return language.lower().strip() in self.detected_languages
    
    def has_pr_diff(self) -> bool:
        """Check if PR diff information is available"""
        return self.pr_diff_info is not None
    
    def get_changed_files(self) -> List[str]:
        """Get list of changed files from PR diff"""
        if self.pr_diff_info:
            return self.pr_diff_info.changed_files
        return []
    
    def get_function_changes(self) -> List[Dict[str, Any]]:
        """Get list of function changes from PR diff"""
        if self.pr_diff_info:
            return self.pr_diff_info.function_changes
        return []
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the project data context"""
        return {
            "repository_url": self.repository_url,
            "cloned_path": self.cloned_code_path,
            "detected_languages": self.detected_languages,
            "language_count": self.language_count,
            "primary_language": self.primary_language,
            "has_languages": self.has_languages,
            "analysis_timestamp": self.analysis_timestamp.isoformat() if self.analysis_timestamp else None,
            "acquisition_duration_ms": self.acquisition_duration_ms
        }
        
    def __str__(self) -> str:
        lang_summary = f"{self.language_count} languages" if self.language_count > 1 else (
            self.primary_language if self.primary_language else "no languages"
        )
        return f"ProjectDataContext(path={os.path.basename(self.cloned_code_path)}, {lang_summary})"
    
    def __repr__(self) -> str:
        return (f"ProjectDataContext(cloned_code_path='{self.cloned_code_path}', "
                f"detected_languages={self.detected_languages}, "
                f"repository_url='{self.repository_url}')") 