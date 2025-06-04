"""
Task Definition Models for RepoChat v1.0

Defines the structure for tasks that the Orchestrator can execute.
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class TaskDefinition(BaseModel):
    """
    Definition of a task to be executed by the RepoChat system.
    
    For v1.0, starts with basic repository URL.
    Will be extended in future phases to include PR information, 
    LLM configuration, and other task parameters.
    """
    
    repository_url: str
    """URL of the Git repository to analyze"""
    
    # Metadata fields for task tracking
    task_id: Optional[str] = None
    """Unique identifier for this task"""
    
    created_at: Optional[datetime] = None
    """Timestamp when task was created"""
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    def __str__(self) -> str:
        return f"TaskDefinition(repo={self.repository_url}, id={self.task_id})" 