"""
Mock Data Acquisition Models for Full Workflow Demo

Simple implementations to demonstrate integration between 
Phase 1 (Data Acquisition) and Phase 2 (CKG Operations)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ProjectDataContext(BaseModel):
    """
    Project data context from TEAM Data Acquisition.
    
    Contains information about cloned repository and detected languages
    for use by TEAM CKG Operations.
    """
    
    project_name: str
    cloned_code_path: str
    detected_languages: List[str]
    repository_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True 