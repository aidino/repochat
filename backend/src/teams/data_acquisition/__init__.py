"""
TEAM Data Acquisition - RepoChat v1.0

Handles data acquisition operations including:
- Git repository cloning and management
- Code file extraction and organization  
- Repository metadata collection
- File system operations

Core Components:
- GitOperationsModule: Git repository operations and cloning
"""

# Team Data Acquisition imports
from .git_operations_module import GitOperationsModule

__all__ = [
    'GitOperationsModule'
]
