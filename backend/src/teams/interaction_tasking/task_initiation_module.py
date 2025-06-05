"""
Task Initiation Module for TEAM Interaction & Tasking

Responsible for creating TaskDefinition objects from user input.
Updated for Task 4.2 to support PR review functionality.
"""

from typing import Optional
import uuid
from datetime import datetime

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit
from shared.models.task_definition import TaskDefinition, TaskType


class TaskInitiationModule:
    """
    Module responsible for creating TaskDefinition objects from user input.
    
    Updated for Task 4.2 to support both project scanning and PR review tasks.
    
    Supported task types:
    - scan_project: Basic repository analysis
    - review_pr: Pull Request review and analysis
    
    Future phases will add:
    - LLM configuration integration
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
        if not self.validate_repository_url(repository_url):
            error_msg = f"Invalid repository URL format: {repository_url}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Generate task ID if not provided
        if not task_id:
            task_id = f"scan-project-{str(uuid.uuid4())[:8]}"
        
        # Create TaskDefinition for project scanning
        task_definition = TaskDefinition(
            repository_url=repository_url,
            task_type=TaskType.SCAN_PROJECT,
            task_id=task_id,
            created_at=datetime.now()
        )
        
        self.logger.info("Scan project task created successfully", extra={
            'extra_data': {
                'task_id': task_definition.task_id,
                'task_type': task_definition.task_type.value if hasattr(task_definition.task_type, 'value') else str(task_definition.task_type),
                'repository_url': task_definition.repository_url,
                'created_at': task_definition.created_at.isoformat() if task_definition.created_at else None
            }
        })
        
        log_function_exit(self.logger, "create_scan_project_task", result="success")
        return task_definition
    
    def create_review_pr_task(self, repository_url: str, pr_identifier: str, task_id: Optional[str] = None) -> TaskDefinition:
        """
        Create a TaskDefinition for reviewing a Pull Request.
        
        Updated for Task 4.2 with real PR review functionality.
        
        Args:
            repository_url: URL of the Git repository
            pr_identifier: Pull Request ID/number or full PR URL
            task_id: Optional custom task ID
            
        Returns:
            TaskDefinition: Configured task definition for PR review
            
        Raises:
            ValueError: If inputs are invalid
        """
        log_function_entry(self.logger, "create_review_pr_task", 
                          repository_url=repository_url, pr_identifier=pr_identifier, task_id=task_id)
        
        # Validate inputs
        if not repository_url or not repository_url.strip():
            error_msg = "Repository URL cannot be empty"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not pr_identifier or not pr_identifier.strip():
            error_msg = "PR identifier cannot be empty"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Clean inputs
        repository_url = repository_url.strip()
        pr_identifier = pr_identifier.strip()
        
        # Validate repository URL
        if not self.validate_repository_url(repository_url):
            error_msg = f"Invalid repository URL format: {repository_url}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Generate task ID if not provided
        if not task_id:
            task_id = f"review-pr-{str(uuid.uuid4())[:8]}"
        
        # Determine if pr_identifier is a URL or just an ID/number
        pr_id = None
        pr_url = None
        
        if self._is_pr_url(pr_identifier):
            pr_url = pr_identifier
            # The TaskDefinition will extract the ID from URL
        else:
            pr_id = pr_identifier
        
        # Create TaskDefinition for PR review
        task_definition = TaskDefinition(
            repository_url=repository_url,
            task_type=TaskType.REVIEW_PR,
            pr_id=pr_id,
            pr_url=pr_url,
            task_id=task_id,
            created_at=datetime.now()
        )
        
        self.logger.info("PR review task created successfully", extra={
            'extra_data': {
                'task_id': task_definition.task_id,
                'task_type': task_definition.task_type.value if hasattr(task_definition.task_type, 'value') else str(task_definition.task_type),
                'repository_url': task_definition.repository_url,
                'pr_id': task_definition.pr_id,
                'pr_url': task_definition.pr_url,
                'pr_identifier_extracted': task_definition.get_pr_identifier(),
                'created_at': task_definition.created_at.isoformat() if task_definition.created_at else None
            }
        })
        
        log_function_exit(self.logger, "create_review_pr_task", result="success")
        return task_definition
    
    def _is_pr_url(self, identifier: str) -> bool:
        """Check if the identifier is a PR URL rather than just an ID."""
        return identifier.startswith(('http://', 'https://')) and ('pull/' in identifier or 'merge_requests/' in identifier)
    
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
    
    def validate_pr_identifier(self, pr_identifier: str) -> bool:
        """
        Validate if PR identifier is acceptable (ID number or URL).
        
        Args:
            pr_identifier: PR ID or URL to validate
            
        Returns:
            bool: True if identifier format is valid
        """
        if not pr_identifier or not pr_identifier.strip():
            return False
        
        identifier = pr_identifier.strip()
        
        # Check if it's a URL
        if self._is_pr_url(identifier):
            return True
        
        # Check if it's a numeric ID
        try:
            int(identifier)
            return True
        except ValueError:
            return False
    
    def get_module_stats(self) -> dict:
        """
        Get statistics about this module's usage.
        
        Returns:
            dict: Module statistics
        """
        return {
            'module': 'TaskInitiationModule',
            'version': '1.0.1',  # Updated for Task 4.2
            'supported_tasks': ['scan_project', 'review_pr'],
            'features': {
                'url_validation': True,
                'task_id_generation': True,
                'pr_url_parsing': True,  # New in Task 4.2
                'pr_id_extraction': True,  # New in Task 4.2
                'llm_config_integration': False  # Future phase
            },
            'task_types': [task_type.value for task_type in TaskType]
        } 