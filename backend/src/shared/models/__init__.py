"""
Shared Models Package for RepoChat v1.0

Contains data models and schemas used across the application.
"""

from .task_definition import TaskDefinition
from .project_data_context import ProjectDataContext

__all__ = ["TaskDefinition", "ProjectDataContext"]

from .git_models import CloneResult, GitMetadata
