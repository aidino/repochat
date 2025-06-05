"""
Task Initiation Module for TEAM Interaction & Tasking

Responsible for creating TaskDefinition objects from user input.
For Task 4.1 (F4.3), this module converts CLI input into standardized TaskDefinition.
"""

from typing import Optional
import uuid
from datetime import datetime

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit
from shared.models.task_definition import TaskDefinition


class TaskInitiationModule:
    """
    Module responsible for creating TaskDefinition objects from user input.
    
    For v1.0, this module handles basic repository URL input and creates
    TaskDefinition objects with default LLM configuration.
    
    Future phases will add:
    - LLM configuration integration
    - PR-specific task creation  
    - User preference loading
    """
    
    def __init__(self):
        """Initialize TaskInitiationModule with logging."""
        self.logger = get_logger("task_initiation.module")
        self.logger.info("TaskInitiationModule initialized")
    
    def create_scan_project_task(self, repository_url: str, task_id: Optional[str] = None) -> TaskDefinition:
        """
        Create a TaskDefinition for scanning a project repository.
        
        Args:
            repository_url: URL of the Git repository to scan
            task_id: Optional custom task ID, will generate UUID if not provided
            
        Returns:
            TaskDefinition: Configured task definition for project scanning
            
        Raises:
            ValueError: If repository_url is invalid or empty
        """
        log_function_entry(self.logger, "create_scan_project_task", 
                          repository_url=repository_url, task_id=task_id)
        
        # Validate input
        if not repository_url or not repository_url.strip():
            error_msg = "Repository URL cannot be empty"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Clean URL
        repository_url = repository_url.strip()
        
        # Basic URL validation
        if not (repository_url.startswith('http://') or 
                repository_url.startswith('https://') or 
                repository_url.startswith('git@')):
            error_msg = f"Invalid repository URL format: {repository_url}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Generate task ID if not provided
        if not task_id:
            task_id = f"scan-project-{str(uuid.uuid4())[:8]}"
        
        # Create TaskDefinition
        task_definition = TaskDefinition(
            repository_url=repository_url,
            task_id=task_id,
            created_at=datetime.now()
        )
        
        self.logger.info("Scan project task created successfully", extra={
            'extra_data': {
                'task_id': task_definition.task_id,
                'repository_url': task_definition.repository_url,
                'created_at': task_definition.created_at.isoformat() if task_definition.created_at else None
            }
        })
        
        log_function_exit(self.logger, "create_scan_project_task", result="success")
        return task_definition
    
    def create_review_pr_task(self, repository_url: str, pr_id: str, task_id: Optional[str] = None) -> TaskDefinition:
        """
        Create a TaskDefinition for reviewing a Pull Request.
        
        This is a placeholder for Task 4.2. In v1.0, TaskDefinition doesn't have PR fields yet.
        
        Args:
            repository_url: URL of the Git repository
            pr_id: Pull Request ID or URL
            task_id: Optional custom task ID
            
        Returns:
            TaskDefinition: Configured task definition for PR review
            
        Note:
            For v1.0, this creates a basic TaskDefinition. Future phases will add
            PR-specific fields to the TaskDefinition model.
        """
        log_function_entry(self.logger, "create_review_pr_task", 
                          repository_url=repository_url, pr_id=pr_id, task_id=task_id)
        
        # Validate inputs
        if not repository_url or not repository_url.strip():
            raise ValueError("Repository URL cannot be empty")
        
        if not pr_id or not pr_id.strip():
            raise ValueError("PR ID cannot be empty")
        
        # Generate task ID if not provided
        if not task_id:
            task_id = f"review-pr-{str(uuid.uuid4())[:8]}"
        
        # For v1.0, we'll store PR info in task_id or use repository_url
        # Future phases will add pr_id field to TaskDefinition
        self.logger.warning("PR review task creation is placeholder for v1.0", extra={
            'extra_data': {
                'pr_id': pr_id,
                'repository_url': repository_url,
                'note': 'TaskDefinition model needs PR fields in future phases'
            }
        })
        
        task_definition = TaskDefinition(
            repository_url=repository_url,
            task_id=task_id,
            created_at=datetime.now()
        )
        
        self.logger.info("PR review task created (placeholder)", extra={
            'extra_data': {
                'task_id': task_definition.task_id,
                'repository_url': task_definition.repository_url,
                'pr_id': pr_id
            }
        })
        
        log_function_exit(self.logger, "create_review_pr_task", result="placeholder_success")
        return task_definition
    
    def validate_repository_url(self, repository_url: str) -> bool:
        """
        Validate if repository URL format is acceptable.
        
        Args:
            repository_url: URL to validate
            
        Returns:
            bool: True if URL format is valid
        """
        if not repository_url or not repository_url.strip():
            return False
        
        url = repository_url.strip()
        
        # Check for supported URL formats
        return (url.startswith('http://') or 
                url.startswith('https://') or 
                url.startswith('git@'))
    
    def get_module_stats(self) -> dict:
        """
        Get statistics about this module's usage.
        
        Returns:
            dict: Module statistics
        """
        return {
            'module': 'TaskInitiationModule',
            'version': '1.0.0',
            'supported_tasks': ['scan_project', 'review_pr_placeholder'],
            'features': {
                'url_validation': True,
                'task_id_generation': True,
                'llm_config_integration': False  # Future phase
            }
        } 