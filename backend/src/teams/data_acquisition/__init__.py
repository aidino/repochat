"""
TEAM Data Acquisition - RepoChat v1.0

Handles data acquisition operations including:
- Git repository cloning and management
- Programming language identification and analysis
- Code file extraction and organization  
- Repository metadata collection
- File system operations
- Data context preparation and packaging
- Personal Access Token (PAT) management for private repositories

Core Components:
- GitOperationsModule: Git repository operations and cloning
- LanguageIdentifierModule: Programming language detection and analysis
- DataPreparationModule: Context packaging and data preparation
- PATHandlerModule: Personal Access Token management for private repositories
"""

# Team Data Acquisition imports
from .git_operations_module import GitOperationsModule
from .language_identifier_module import LanguageIdentifierModule
from .data_preparation_module import DataPreparationModule
from .pat_handler_module import PATHandlerModule

__all__ = [
    'GitOperationsModule',
    'LanguageIdentifierModule',
    'DataPreparationModule',
    'PATHandlerModule'
]
