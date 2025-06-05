"""
Task Definition Models for RepoChat v1.0

Defines the structure for tasks that the Orchestrator can execute.
Extended for Task 4.2 to support PR review functionality.
"""

from pydantic import BaseModel, HttpUrl, validator, root_validator
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    """Enum defining types of tasks that can be executed."""
    SCAN_PROJECT = "scan_project"
    REVIEW_PR = "review_pr"
    # Future task types can be added here


class TaskDefinition(BaseModel):
    """
    Definition of a task to be executed by the RepoChat system.
    
    Extended for Task 4.2 to support PR review functionality.
    Can handle both project scanning and PR review tasks.
    """
    
    repository_url: str
    """URL of the Git repository to analyze"""
    
    task_type: TaskType = TaskType.SCAN_PROJECT
    """Type of task to execute (scan_project or review_pr)"""
    
    # PR-specific fields (Task 4.2)
    pr_id: Optional[str] = None
    """Pull Request ID or number (for review_pr tasks)"""
    
    pr_url: Optional[str] = None
    """Full URL to the Pull Request (alternative to pr_id)"""
    
    # Metadata fields for task tracking
    task_id: Optional[str] = None
    """Unique identifier for this task"""
    
    created_at: Optional[datetime] = None
    """Timestamp when task was created"""
    
    # Future extensions for additional phases
    llm_config: Optional[dict] = None
    """LLM configuration for this task (future phase)"""
    
    user_preferences: Optional[dict] = None
    """User preferences and settings (future phase)"""
    
    @root_validator(skip_on_failure=True)
    def validate_pr_fields_for_review_task(cls, values):
        """Validate that PR fields are provided for review_pr tasks."""
        task_type = values.get('task_type')
        
        if task_type == TaskType.REVIEW_PR:
            pr_id = values.get('pr_id')
            pr_url = values.get('pr_url')
            
            if not pr_id and not pr_url:
                raise ValueError("Either pr_id or pr_url must be provided for review_pr tasks")
        
        return values
    
    @validator('task_type', pre=True)
    def validate_task_type(cls, v):
        """Ensure task_type is valid."""
        if isinstance(v, str):
            try:
                return TaskType(v)
            except ValueError:
                raise ValueError(f"Invalid task_type: {v}. Must be one of {list(TaskType)}")
        return v
    
    def is_pr_review_task(self) -> bool:
        """Check if this is a PR review task."""
        return self.task_type == TaskType.REVIEW_PR
    
    def is_project_scan_task(self) -> bool:
        """Check if this is a project scan task."""
        return self.task_type == TaskType.SCAN_PROJECT
    
    def get_pr_identifier(self) -> Optional[str]:
        """Get the PR identifier (pr_id or extract from pr_url)."""
        if self.pr_id:
            return self.pr_id
        
        if self.pr_url:
            # Try to extract PR number from GitHub/GitLab URLs
            import re
            # GitHub: https://github.com/owner/repo/pull/123
            # GitLab: https://gitlab.com/owner/repo/-/merge_requests/123
            github_match = re.search(r'/pull/(\d+)', self.pr_url)
            if github_match:
                return github_match.group(1)
            
            gitlab_match = re.search(r'/merge_requests/(\d+)', self.pr_url)
            if gitlab_match:
                return gitlab_match.group(1)
        
        return None
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            TaskType: lambda v: v.value
        }
        use_enum_values = True
        
    def __str__(self) -> str:
        task_type_str = self.task_type.value if hasattr(self.task_type, 'value') else str(self.task_type)
        if self.is_pr_review_task():
            pr_info = self.get_pr_identifier() or self.pr_url or "unknown"
            return f"TaskDefinition(type={task_type_str}, repo={self.repository_url}, pr={pr_info}, id={self.task_id})"
        else:
            return f"TaskDefinition(type={task_type_str}, repo={self.repository_url}, id={self.task_id})" 