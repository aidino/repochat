"""
TEAM Data Acquisition - RepoChat v1.0

Handles data acquisition operations including:
- Git repository cloning and management
- Programming language identification and analysis
- Code file extraction and organization  
- Repository metadata collection
- File system operations

Core Components:
- GitOperationsModule: Git repository operations and cloning
- LanguageIdentifierModule: Programming language detection and analysis
"""

# Team Data Acquisition imports
from .git_operations_module import GitOperationsModule
from .language_identifier_module import LanguageIdentifierModule

__all__ = [
    'GitOperationsModule',
    'LanguageIdentifierModule'
]
