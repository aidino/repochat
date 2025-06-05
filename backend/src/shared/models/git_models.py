"""
Git operations result models for RepoChat v1.0
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class CloneResult(BaseModel):
    """
    Result of a git clone operation.
    """
    success: bool
    local_path: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        frozen = True


class GitMetadata(BaseModel):
    """
    Git repository metadata.
    """
    repository_url: str
    default_branch: str
    commit_hash: str
    commit_message: str
    size_mb: float
    
    class Config:
        frozen = True
