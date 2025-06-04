"""
Data Preparation Module for RepoChat v1.0

Encapsulates results from GitOperationsModule and LanguageIdentifierModule
into a standardized ProjectDataContext for use by subsequent TEAM agents.
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

from shared.models.project_data_context import ProjectDataContext
from shared.utils.logging_config import get_logger


class DataPreparationModule:
    """
    Module responsible for preparing and packaging project data context.
    
    Takes results from GitOperationsModule and LanguageIdentifierModule and
    creates a standardized ProjectDataContext that can be used by other TEAM agents.
    """
    
    def __init__(self):
        """Initialize the DataPreparationModule with logging."""
        self.logger = get_logger(__name__)
        # Create unique module ID with timestamp and random suffix for uniqueness
        timestamp = int(time.time() * 1000)  # milliseconds for better resolution
        random_suffix = random.randint(1000, 9999)
        self.module_id = f"data_prep_{timestamp}_{random_suffix}"
        
        # Statistics tracking
        self.contexts_created = 0
        self.total_preparation_time = 0.0
        
        self.logger.info(
            "DataPreparationModule initialized",
            extra={
                "module_id": self.module_id,
                "component": "DataPreparationModule",
                "action": "initialize"
            }
        )
    
    def create_project_context(
        self,
        cloned_code_path: str,
        detected_languages: List[str],
        repository_url: Optional[str] = None,
        repository_stats: Optional[Dict[str, Any]] = None,
        language_statistics: Optional[Dict[str, Any]] = None
    ) -> ProjectDataContext:
        """
        Create a ProjectDataContext from Git and Language analysis results.
        
        Args:
            cloned_code_path: Absolute path to the cloned repository directory
            detected_languages: List of programming languages detected
            repository_url: Original repository URL (optional)
            repository_stats: Repository statistics from GitOperationsModule (optional)
            language_statistics: Language analysis statistics from LanguageIdentifierModule (optional)
        
        Returns:
            ProjectDataContext: Standardized context object containing all data
            
        Raises:
            ValueError: If required parameters are invalid
            Exception: For other unexpected errors during context creation
        """
        start_time = time.time()
        
        self.logger.info(
            "Creating project data context",
            extra={
                "module_id": self.module_id,
                "component": "DataPreparationModule",
                "action": "create_context_start",
                "cloned_path": cloned_code_path,
                "language_count": len(detected_languages) if detected_languages else 0,
                "languages": detected_languages[:5] if detected_languages else [],  # Limit for log size
                "repository_url": repository_url
            }
        )
        
        try:
            # Validate inputs
            if not cloned_code_path or not isinstance(cloned_code_path, str):
                raise ValueError("cloned_code_path must be a non-empty string")
            
            if not isinstance(detected_languages, list):
                raise ValueError("detected_languages must be a list")
            
            # Create the context with current timestamp
            context = ProjectDataContext(
                cloned_code_path=cloned_code_path,
                detected_languages=detected_languages,
                repository_url=repository_url,
                repository_stats=repository_stats or {},
                language_statistics=language_statistics or {},
                analysis_timestamp=datetime.now()
            )
            
            # Calculate preparation duration
            duration_ms = (time.time() - start_time) * 1000
            context.acquisition_duration_ms = duration_ms
            
            # Update statistics
            self.contexts_created += 1
            self.total_preparation_time += duration_ms
            
            self.logger.info(
                "Project data context created successfully",
                extra={
                    "module_id": self.module_id,
                    "component": "DataPreparationModule",
                    "action": "create_context_success",
                    "context_summary": context.get_summary(),
                    "duration_ms": duration_ms,
                    "validation_passed": True
                }
            )
            
            # Debug log with detailed context information
            self.logger.debug(
                "Project context details",
                extra={
                    "module_id": self.module_id,
                    "context_repr": repr(context),
                    "has_languages": context.has_languages,
                    "primary_language": context.primary_language,
                    "language_count": context.language_count
                }
            )
            
            return context
            
        except ValueError as ve:
            self.logger.error(
                "Validation error creating project context",
                extra={
                    "module_id": self.module_id,
                    "component": "DataPreparationModule",
                    "action": "create_context_error",
                    "error_type": "ValidationError",
                    "error_message": str(ve),
                    "cloned_path": cloned_code_path,
                    "languages": detected_languages
                },
                exc_info=True
            )
            raise
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Unexpected error creating project context",
                extra={
                    "module_id": self.module_id,
                    "component": "DataPreparationModule",
                    "action": "create_context_error",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": duration_ms
                },
                exc_info=True
            )
            raise
    
    def create_context_from_modules(
        self,
        git_operations_result: Dict[str, Any],
        language_identifier_result: Dict[str, Any]
    ) -> ProjectDataContext:
        """
        Create ProjectDataContext from structured results of GitOperationsModule and LanguageIdentifierModule.
        
        This is a convenience method that extracts the relevant data from module results
        and calls create_project_context with the appropriate parameters.
        
        Args:
            git_operations_result: Result dict from GitOperationsModule.clone_repository
            language_identifier_result: Result dict from LanguageIdentifierModule analysis
        
        Returns:
            ProjectDataContext: Created context object
            
        Raises:
            ValueError: If required fields are missing from module results
            KeyError: If expected keys are not found in results
        """
        self.logger.info(
            "Creating context from module results",
            extra={
                "module_id": self.module_id,
                "component": "DataPreparationModule",
                "action": "create_from_modules_start"
            }
        )
        
        try:
            # Extract Git operations data
            if isinstance(git_operations_result, str):
                # Simple case: result is just the path
                cloned_path = git_operations_result
                repository_stats = {}
                repository_url = None
            elif isinstance(git_operations_result, dict):
                # Complex case: result is a dict with details
                cloned_path = git_operations_result.get("path") or git_operations_result.get("cloned_path")
                repository_stats = git_operations_result.get("stats", {})
                repository_url = git_operations_result.get("repository_url")
            else:
                raise ValueError("git_operations_result must be a string (path) or dict")
            
            if not cloned_path:
                raise ValueError("Cannot extract cloned_path from git_operations_result")
            
            # Extract Language identifier data
            if isinstance(language_identifier_result, list):
                # Simple case: result is just the language list
                detected_languages = language_identifier_result
                language_statistics = {}
            elif isinstance(language_identifier_result, dict):
                # Complex case: result is a dict with details
                detected_languages = language_identifier_result.get("languages", [])
                language_statistics = language_identifier_result.get("statistics", {})
            else:
                raise ValueError("language_identifier_result must be a list (languages) or dict")
            
            self.logger.debug(
                "Extracted data from modules",
                extra={
                    "module_id": self.module_id,
                    "cloned_path": cloned_path,
                    "detected_languages": detected_languages,
                    "repository_url": repository_url,
                    "has_repo_stats": bool(repository_stats),
                    "has_lang_stats": bool(language_statistics)
                }
            )
            
            # Create the context
            return self.create_project_context(
                cloned_code_path=cloned_path,
                detected_languages=detected_languages,
                repository_url=repository_url,
                repository_stats=repository_stats,
                language_statistics=language_statistics
            )
            
        except (ValueError, KeyError) as e:
            self.logger.error(
                "Error extracting data from module results",
                extra={
                    "module_id": self.module_id,
                    "component": "DataPreparationModule",
                    "action": "create_from_modules_error",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "git_result_type": type(git_operations_result).__name__,
                    "lang_result_type": type(language_identifier_result).__name__
                },
                exc_info=True
            )
            raise
    
    def get_module_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the DataPreparationModule's performance.
        
        Returns:
            Dict containing module statistics
        """
        avg_preparation_time = (
            self.total_preparation_time / self.contexts_created
            if self.contexts_created > 0 else 0.0
        )
        
        stats = {
            "module_id": self.module_id,
            "contexts_created": self.contexts_created,
            "total_preparation_time_ms": self.total_preparation_time,
            "average_preparation_time_ms": avg_preparation_time,
            "uptime_seconds": time.time() - int(self.module_id.split("_")[-1])
        }
        
        self.logger.debug(
            "Module statistics retrieved",
            extra={
                "module_id": self.module_id,
                "component": "DataPreparationModule",
                "action": "get_stats",
                "stats": stats
            }
        )
        
        return stats
    
    def validate_context(self, context: ProjectDataContext) -> bool:
        """
        Validate a ProjectDataContext object.
        
        Args:
            context: ProjectDataContext to validate
            
        Returns:
            bool: True if context is valid, False otherwise
        """
        try:
            # Basic type check
            if not isinstance(context, ProjectDataContext):
                self.logger.warning(
                    "Context validation failed: not a ProjectDataContext",
                    extra={
                        "module_id": self.module_id,
                        "component": "DataPreparationModule",
                        "action": "validate_context",
                        "context_type": type(context).__name__
                    }
                )
                return False
            
            # Check required fields
            if not context.cloned_code_path:
                self.logger.warning(
                    "Context validation failed: missing cloned_code_path",
                    extra={
                        "module_id": self.module_id,
                        "component": "DataPreparationModule",
                        "action": "validate_context"
                    }
                )
                return False
            
            # Check languages list
            if not isinstance(context.detected_languages, list):
                self.logger.warning(
                    "Context validation failed: detected_languages is not a list",
                    extra={
                        "module_id": self.module_id,
                        "component": "DataPreparationModule",
                        "action": "validate_context",
                        "languages_type": type(context.detected_languages).__name__
                    }
                )
                return False
            
            self.logger.debug(
                "Context validation passed",
                extra={
                    "module_id": self.module_id,
                    "component": "DataPreparationModule",
                    "action": "validate_context",
                    "context_summary": context.get_summary()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Error during context validation",
                extra={
                    "module_id": self.module_id,
                    "component": "DataPreparationModule",
                    "action": "validate_context_error",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                },
                exc_info=True
            )
            return False 