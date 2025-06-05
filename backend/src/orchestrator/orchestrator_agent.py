"""
Orchestrator Agent - Central Coordination Component for RepoChat v1.0

The Orchestrator Agent is the central hub that coordinates workflow execution,
manages tasks, and ensures smooth interaction between all TEAM agents.

Enhanced with comprehensive logging for debugging and monitoring.
"""

from typing import Optional, Dict, Any
import uuid
import time
from datetime import datetime

from shared.utils.logging_config import (
    get_logger, 
    log_function_entry, 
    log_function_exit, 
    log_performance_metric
)
from shared.models.task_definition import TaskDefinition
from shared.models.project_data_context import ProjectDataContext
from teams.data_acquisition import GitOperationsModule, LanguageIdentifierModule, DataPreparationModule, PATHandlerModule
from teams.ckg_operations import TeamCKGOperationsFacade, CKGOperationResult


class OrchestratorAgent:
    """
    Central orchestrator agent that manages the overall workflow
    and coordinates between different TEAM agents.
    
    This is the enhanced implementation for Task 1.1, focusing on:
    - Basic initialization with comprehensive logging
    - Task handling structure with detailed debugging
    - Foundation for future workflow management
    - Performance monitoring and error tracking
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        """
        Initialize the Orchestrator Agent with comprehensive logging.
        
        Args:
            agent_id: Optional unique identifier for this agent instance
        """
        start_time = time.time()
        
        # Generate agent ID and setup logging
        self.agent_id = agent_id or str(uuid.uuid4())
        self.logger = get_logger(
            f"orchestrator.{self.agent_id[:8]}", 
            extra_context={'agent_id': self.agent_id}
        )
        
        log_function_entry(self.logger, "__init__", agent_id=agent_id)
        
        self.logger.info(f"Creating Orchestrator Agent with ID: {self.agent_id}")
        
        # Agent state with detailed logging
        self._is_initialized = False
        self._active_tasks: Dict[str, Dict[str, Any]] = {}
        self._initialization_time = None
        self._stats = {
            'total_tasks_handled': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'start_time': datetime.now()
        }
        
        self.logger.debug("Agent state initialized", extra={
            'extra_data': {
                'initial_state': {
                    'is_initialized': self._is_initialized,
                    'active_tasks_count': len(self._active_tasks),
                    'stats': self._stats
                }
            }
        })
        
        # Initialize the agent
        try:
            self._initialize()
            init_time = time.time() - start_time
            log_performance_metric(
                self.logger, 
                "agent_initialization_time", 
                init_time * 1000, 
                "ms",
                agent_id=self.agent_id
            )
            log_function_exit(self.logger, "__init__", result="success", execution_time=init_time)
        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {e}", exc_info=True)
            log_function_exit(self.logger, "__init__", result="error", execution_time=time.time() - start_time)
            raise
    
    def _initialize(self) -> None:
        """Initialize the orchestrator agent and its components with detailed logging."""
        start_time = time.time()
        log_function_entry(self.logger, "_initialize")
        
        self.logger.info(f"Starting initialization of Orchestrator Agent {self.agent_id}")
        
        try:
            self.logger.debug("Setting up core components...")
            
            # Initialize TEAM Data Acquisition components
            self.logger.debug("Initializing TEAM Data Acquisition...")
            self.git_operations = GitOperationsModule()
            self.language_identifier = LanguageIdentifierModule()
            self.data_preparation = DataPreparationModule()
            self.pat_handler = PATHandlerModule()
            self.logger.info("TEAM Data Acquisition components initialized successfully", extra={
                'extra_data': {
                    'components': [
                        'GitOperationsModule',
                        'LanguageIdentifierModule', 
                        'DataPreparationModule',
                        'PATHandlerModule'
                    ]
                }
            })
            
            # Initialize TEAM CKG Operations (Task 2.9)
            self.logger.debug("Initializing TEAM CKG Operations...")
            self.ckg_operations = TeamCKGOperationsFacade()
            self.logger.info("TEAM CKG Operations initialized successfully", extra={
                'extra_data': {
                    'ckg_operations_ready': self.ckg_operations.is_ready(),
                    'component': 'TeamCKGOperationsFacade'
                }
            })
            
            # Future phases will add:
            # - LangGraph workflow engine setup
            # - A2A protocol initialization  
            # - TEAM agent connection setup
            
            self.logger.debug("Core components setup completed")
            
            # Mark as initialized
            self._is_initialized = True
            self._initialization_time = datetime.now()
            
            self.logger.info("Orchestrator Agent initialization completed successfully", extra={
                'extra_data': {
                    'initialization_time': self._initialization_time.isoformat(),
                    'agent_id': self.agent_id,
                    'status': 'initialized',
                    'components_initialized': [
                        'GitOperationsModule',
                        'LanguageIdentifierModule',
                        'DataPreparationModule',
                        'PATHandlerModule',
                        'TeamCKGOperationsFacade'
                    ]
                }
            })
            
            init_time = time.time() - start_time
            log_performance_metric(
                self.logger, 
                "initialization_duration", 
                init_time * 1000, 
                "ms",
                agent_id=self.agent_id
            )
            log_function_exit(self.logger, "_initialize", result="success", execution_time=init_time)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Orchestrator Agent: {e}", exc_info=True, extra={
                'extra_data': {
                    'agent_id': self.agent_id,
                    'error_type': type(e).__name__,
                    'initialization_failed': True
                }
            })
            log_function_exit(self.logger, "_initialize", result="error", execution_time=time.time() - start_time)
            raise
    
    def handle_task(self, task_definition: TaskDefinition) -> str:
        """
        Handle a task defined by TaskDefinition with comprehensive logging.
        
        This is an enhanced implementation for Task 1.1. Future phases will add:
        - Workflow orchestration using LangGraph
        - TEAM agent coordination
        - State management
        - Error handling and recovery
        
        Args:
            task_definition: The task to be executed
            
        Returns:
            Task execution ID
            
        Raises:
            RuntimeError: If orchestrator is not initialized
        """
        start_time = time.time()
        log_function_entry(
            self.logger, 
            "handle_task", 
            task_definition=str(task_definition),
            repository_url=task_definition.repository_url
        )
        
        self.logger.info(f"Received new task request", extra={
            'extra_data': {
                'task_definition': {
                    'repository_url': task_definition.repository_url,
                    'task_id': task_definition.task_id,
                    'created_at': task_definition.created_at.isoformat() if task_definition.created_at else None
                },
                'current_active_tasks': len(self._active_tasks)
            }
        })
        
        # Validation with detailed logging
        if not self._is_initialized:
            error_msg = "Orchestrator Agent is not initialized"
            self.logger.error(error_msg, extra={
                'extra_data': {
                    'agent_state': 'not_initialized',
                    'agent_id': self.agent_id,
                    'error_type': 'initialization_error'
                }
            })
            log_function_exit(self.logger, "handle_task", result="error")
            raise RuntimeError(error_msg)
        
        # Generate task execution ID
        execution_id = str(uuid.uuid4())
        self.logger.debug(f"Generated execution ID: {execution_id}")
        
        # Set task metadata with logging
        if task_definition.task_id is None:
            task_definition.task_id = execution_id
            self.logger.debug(f"Assigned task_id: {execution_id}")
        if task_definition.created_at is None:
            task_definition.created_at = datetime.now()
            self.logger.debug(f"Set created_at: {task_definition.created_at}")
        
        self.logger.info(f"Processing task with execution ID: {execution_id}", extra={
            'extra_data': {
                'execution_id': execution_id,
                'repository_url': task_definition.repository_url,
                'task_metadata': {
                    'task_id': task_definition.task_id,
                    'created_at': task_definition.created_at.isoformat()
                }
            }
        })
        
        # Initialize task tracking
        task_info = {
            'definition': task_definition,
            'status': 'pending',
            'created_at': datetime.now(),
            'execution_id': execution_id,
            'start_time': start_time,
            'steps_completed': [],
            'errors': []
        }
        
        self._active_tasks[execution_id] = task_info
        self._stats['total_tasks_handled'] += 1
        
        self.logger.debug(f"Task {execution_id} added to active tasks", extra={
            'extra_data': {
                'active_tasks_count': len(self._active_tasks),
                'total_tasks_handled': self._stats['total_tasks_handled']
            }
        })
        
        try:
            self.logger.info(f"Starting task processing: {task_definition.repository_url}")
            
            # Update task status
            self._active_tasks[execution_id]['status'] = 'in_progress'
            self._active_tasks[execution_id]['steps_completed'].append({
                'step': 'task_setup',
                'timestamp': datetime.now(),
                'duration_ms': (time.time() - start_time) * 1000
            })
            
            self.logger.info(f"Task {execution_id} is now in progress", extra={
                'extra_data': {
                    'execution_id': execution_id,
                    'status': 'in_progress',
                    'repository_url': task_definition.repository_url
                }
            })
            
            # TEAM Data Acquisition - Clone Repository (Task 1.2 Integration)
            self.logger.info(f"Starting TEAM Data Acquisition: cloning repository")
            clone_start_time = time.time()
            
            try:
                repository_path = self.git_operations.clone_repository(
                    repository_url=task_definition.repository_url
                )
                
                clone_duration = time.time() - clone_start_time
                
                self._active_tasks[execution_id]['steps_completed'].append({
                    'step': 'repository_cloned',
                    'timestamp': datetime.now(),
                    'duration_ms': clone_duration * 1000,
                    'repository_path': repository_path
                })
                
                self.logger.info(f"Repository cloned successfully", extra={
                    'extra_data': {
                        'execution_id': execution_id,
                        'repository_path': repository_path,
                        'clone_duration_ms': clone_duration * 1000
                    }
                })
                
                # Store repository path in task info for future use
                self._active_tasks[execution_id]['repository_path'] = repository_path
                
            except Exception as clone_error:
                self.logger.error(f"Failed to clone repository: {clone_error}", exc_info=True)
                self._active_tasks[execution_id]['errors'].append({
                    'error': f"Clone failed: {clone_error}",
                    'timestamp': datetime.now(),
                    'error_type': 'clone_error'
                })
                # Continue processing - don't fail the entire task yet
                self._active_tasks[execution_id]['repository_path'] = None
            
            # TEAM Data Acquisition - Language Identification (Task 1.3 Integration)
            detected_languages = []
            if self._active_tasks[execution_id].get('repository_path'):
                self.logger.info(f"Starting language identification")
                lang_start_time = time.time()
                
                try:
                    detected_languages = self.language_identifier.identify_languages(
                        repository_path=self._active_tasks[execution_id]['repository_path']
                    )
                    
                    lang_duration = time.time() - lang_start_time
                    
                    self._active_tasks[execution_id]['steps_completed'].append({
                        'step': 'languages_identified',
                        'timestamp': datetime.now(),
                        'duration_ms': lang_duration * 1000,
                        'detected_languages': detected_languages
                    })
                    
                    self.logger.info(f"Languages identified successfully", extra={
                        'extra_data': {
                            'execution_id': execution_id,
                            'detected_languages': detected_languages,
                            'identification_duration_ms': lang_duration * 1000
                        }
                    })
                    
                    # Store detected languages in task info
                    self._active_tasks[execution_id]['detected_languages'] = detected_languages
                    
                except Exception as lang_error:
                    self.logger.error(f"Failed to identify languages: {lang_error}", exc_info=True)
                    self._active_tasks[execution_id]['errors'].append({
                        'error': f"Language identification failed: {lang_error}",
                        'timestamp': datetime.now(),
                        'error_type': 'language_identification_error'
                    })
                    # Continue processing - don't fail the entire task
                    self._active_tasks[execution_id]['detected_languages'] = []
            else:
                self.logger.warning("Skipping language identification - no repository path available")
                self._active_tasks[execution_id]['detected_languages'] = []
            
            # Future workflow steps with detailed logging:
            self.logger.debug("Future workflow steps:", extra={
                'extra_data': {
                    'completed_steps': [
                        "TEAM Data Acquisition -> clone repo (IMPLEMENTED)",
                        "TEAM Data Acquisition -> identify languages (IMPLEMENTED)"
                    ],
                    'planned_steps': [
                        "TEAM Data Acquisition -> identify language",
                        "TEAM CKG Operations -> build knowledge graph",
                        "TEAM Code Analysis -> analyze code structure", 
                        "TEAM Synthesis & Reporting -> generate reports"
                    ],
                    'current_phase': "Task 1.3 - LanguageIdentifierModule integrated"
                }
            })
            
            # Task completed successfully
            self.logger.info(f"Task {execution_id} processing completed successfully")
            
            # Update final task status
            self._active_tasks[execution_id]['status'] = 'completed'
            self._active_tasks[execution_id]['steps_completed'].append({
                'step': 'task_processing_complete',
                'timestamp': datetime.now(),
                'duration_ms': (time.time() - start_time) * 1000
            })
            self._stats['successful_tasks'] += 1
            
            execution_time = time.time() - start_time
            log_performance_metric(
                self.logger,
                "task_handling_time",
                execution_time * 1000,
                "ms",
                execution_id=execution_id,
                repository_url=task_definition.repository_url
            )
            
            self.logger.info(f"Task {execution_id} completed successfully", extra={
                'extra_data': {
                    'execution_id': execution_id,
                    'execution_time_ms': execution_time * 1000,
                    'final_status': 'completed',
                    'steps_completed': len(self._active_tasks[execution_id]['steps_completed']),
                    'repository_cloned': self._active_tasks[execution_id].get('repository_path') is not None
                }
            })
            
            log_function_exit(self.logger, "handle_task", result=execution_id, execution_time=execution_time)
            
        except Exception as e:
            self.logger.error(f"Error processing task {execution_id}: {e}", exc_info=True, extra={
                'extra_data': {
                    'execution_id': execution_id,
                    'error_type': type(e).__name__,
                    'repository_url': task_definition.repository_url,
                    'execution_time_ms': (time.time() - start_time) * 1000
                }
            })
            
            # Update task status for error
            self._active_tasks[execution_id]['status'] = 'failed'
            self._active_tasks[execution_id]['errors'].append({
                'error': str(e),
                'timestamp': datetime.now(),
                'error_type': type(e).__name__
            })
            raise
        
        return execution_id
    
    def handle_scan_project_task(self, task_definition: TaskDefinition) -> ProjectDataContext:
        """
        Handle scan project task according to Task 1.5 requirements.
        
        This method implements Task 1.5 (F1.5) DoD:
        - Takes TaskDefinition containing repository_url
        - Calls GitOperationsModule and LanguageIdentifierModule sequentially
        - Integrates PATHandlerModule for private repository support
        - Uses DataPreparationModule to create ProjectDataContext
        - Logs ProjectDataContext result
        
        Args:
            task_definition: TaskDefinition with repository_url
            
        Returns:
            ProjectDataContext with cloned repository path and detected languages
            
        Raises:
            RuntimeError: If orchestrator is not initialized
            Exception: If any step in the workflow fails
        """
        start_time = time.time()
        log_function_entry(
            self.logger,
            "handle_scan_project_task",
            repository_url=task_definition.repository_url,
            task_id=task_definition.task_id
        )
        
        self.logger.info(f"Starting scan project task for: {task_definition.repository_url}")
        
        # Update statistics tracking
        self._stats['total_tasks_handled'] += 1
        
        # Validation
        if not self._is_initialized:
            error_msg = "Orchestrator Agent is not initialized"
            self.logger.error(error_msg)
            log_function_exit(self.logger, "handle_scan_project_task", result="not_initialized")
            raise RuntimeError(error_msg)
        
        try:
            # Step 1: Check if PAT is needed and request if necessary
            self.logger.info("Step 1: Checking PAT requirements")
            step1_start = time.time()
            
            pat = self.pat_handler.request_pat_if_needed(task_definition.repository_url)
            pat_message = "PAT obtained from user" if pat else "No PAT needed/provided"
            
            step1_duration = time.time() - step1_start
            self.logger.info(f"Step 1 completed: {pat_message}", extra={
                'extra_data': {
                    'step': 'pat_check',
                    'duration_ms': step1_duration * 1000,
                    'has_pat': pat is not None
                }
            })
            
            # Step 2: Clone repository using GitOperationsModule (with PAT if available)
            self.logger.info("Step 2: Cloning repository")
            step2_start = time.time()
            
            repository_path = self.git_operations.clone_repository(
                repository_url=task_definition.repository_url,
                pat=pat
            )
            
            step2_duration = time.time() - step2_start
            self.logger.info(f"Step 2 completed: Repository cloned to {repository_path}", extra={
                'extra_data': {
                    'step': 'repository_clone',
                    'duration_ms': step2_duration * 1000,
                    'repository_path': repository_path,
                    'used_pat': pat is not None
                }
            })
            
            # Step 3: Identify languages using LanguageIdentifierModule
            self.logger.info("Step 3: Identifying programming languages")
            step3_start = time.time()
            
            detected_languages = self.language_identifier.identify_languages(
                repository_path=repository_path
            )
            
            step3_duration = time.time() - step3_start
            self.logger.info(f"Step 3 completed: Languages detected: {detected_languages}", extra={
                'extra_data': {
                    'step': 'language_identification',
                    'duration_ms': step3_duration * 1000,
                    'detected_languages': detected_languages,
                    'language_count': len(detected_languages)
                }
            })
            
            # Step 4: Create ProjectDataContext using DataPreparationModule
            self.logger.info("Step 4: Creating ProjectDataContext")
            step4_start = time.time()
            
            project_data_context = self.data_preparation.create_project_context(
                cloned_code_path=repository_path,
                detected_languages=detected_languages,
                repository_url=task_definition.repository_url
            )
            
            step4_duration = time.time() - step4_start
            
            # Log ProjectDataContext as required by DoD
            self.logger.info("ProjectDataContext created successfully:", extra={
                'extra_data': {
                    'step': 'data_context_creation',
                    'duration_ms': step4_duration * 1000,
                    'project_data_context': {
                        'cloned_code_path': project_data_context.cloned_code_path,
                        'detected_languages': project_data_context.detected_languages,
                        'repository_url': project_data_context.repository_url,
                        'language_count': project_data_context.language_count,
                        'has_languages': project_data_context.has_languages,
                        'primary_language': project_data_context.primary_language
                    }
                }
            })
            
            # Clear PAT from memory for security
            if pat:
                self.pat_handler.clear_pat_cache()
                pat = None  # Clear local reference
                self.logger.debug("PAT cleared from memory for security")
            
            total_duration = time.time() - start_time
            
            self.logger.info("Scan project task completed successfully", extra={
                'extra_data': {
                    'repository_url': task_definition.repository_url,
                    'total_duration_ms': total_duration * 1000,
                    'steps_completed': 4,
                    'final_result': {
                        'repository_path': repository_path,
                        'languages': detected_languages,
                        'context_created': True
                    }
                }
            })
            
            # Update successful task counter
            self._stats['successful_tasks'] += 1
            
            log_performance_metric(
                self.logger,
                "scan_project_task_duration",
                total_duration * 1000,
                "ms",
                repository_url=task_definition.repository_url,
                language_count=len(detected_languages)
            )
            
            log_function_exit(
                self.logger,
                "handle_scan_project_task",
                result="success",
                execution_time=total_duration
            )
            
            return project_data_context
            
        except Exception as e:
            # Clear PAT on error for security
            if 'pat' in locals() and pat:
                self.pat_handler.clear_pat_cache()
                
            # Update failed task counter
            self._stats['failed_tasks'] += 1
                
            error_msg = f"Error in scan project task: {e}"
            self.logger.error(error_msg, exc_info=True, extra={
                'extra_data': {
                    'repository_url': task_definition.repository_url,
                    'error_type': type(e).__name__,
                    'execution_time_ms': (time.time() - start_time) * 1000
                }
            })
            
            log_function_exit(
                self.logger,
                "handle_scan_project_task",
                result="error",
                execution_time=time.time() - start_time
            )
            raise
    
    def handle_scan_project_with_ckg_task(self, task_definition: TaskDefinition) -> tuple[ProjectDataContext, CKGOperationResult]:
        """
        Handle scan project task with CKG building according to Task 2.9 requirements.
        
        This method implements the complete workflow:
        1. Execute data acquisition (existing handle_scan_project_task)
        2. Pass ProjectDataContext to TEAM CKG Operations
        3. Build Code Knowledge Graph
        4. Return both data context and CKG operation results
        
        Args:
            task_definition: TaskDefinition with repository_url
            
        Returns:
            Tuple of (ProjectDataContext, CKGOperationResult)
            
        Raises:
            RuntimeError: If orchestrator is not initialized
            Exception: If any step in the workflow fails
        """
        start_time = time.time()
        log_function_entry(
            self.logger,
            "handle_scan_project_with_ckg_task",
            repository_url=task_definition.repository_url,
            task_id=task_definition.task_id
        )
        
        self.logger.info(f"Starting full scan + CKG workflow for: {task_definition.repository_url}")
        
        try:
            # Step 1: Execute data acquisition workflow
            self.logger.info("Phase 1: Data Acquisition")
            project_data_context = self.handle_scan_project_task(task_definition)
            
            self.logger.info("Data acquisition completed successfully", extra={
                'extra_data': {
                    'cloned_path': project_data_context.cloned_code_path,
                    'detected_languages': project_data_context.detected_languages,
                    'language_count': project_data_context.language_count
                }
            })
            
            # Step 2: Execute CKG operations workflow (Task 2.9)
            self.logger.info("Phase 2: CKG Operations")
            ckg_start_time = time.time()
            
            # Generate project name from repository
            import os
            project_name = os.path.basename(project_data_context.cloned_code_path)
            
            # Process with TEAM CKG Operations
            ckg_result = self.ckg_operations.process_project_data_context(
                project_data_context,
                project_name
            )
            
            ckg_duration = time.time() - ckg_start_time
            
            if ckg_result.success:
                self.logger.info("CKG Operations completed successfully", extra={
                    'extra_data': {
                        'ckg_duration_ms': ckg_duration * 1000,
                        'nodes_created': ckg_result.nodes_created,
                        'relationships_created': ckg_result.relationships_created,
                        'files_processed': ckg_result.files_processed
                    }
                })
            else:
                self.logger.warning("CKG Operations completed with errors", extra={
                    'extra_data': {
                        'ckg_duration_ms': ckg_duration * 1000,
                        'errors': ckg_result.errors,
                        'warnings': ckg_result.warnings
                    }
                })
            
            total_duration = time.time() - start_time
            
            self.logger.info("Complete scan + CKG workflow finished", extra={
                'extra_data': {
                    'repository_url': task_definition.repository_url,
                    'total_duration_ms': total_duration * 1000,
                    'data_acquisition_success': True,
                    'ckg_operations_success': ckg_result.success,
                    'overall_success': ckg_result.success,
                    'final_statistics': {
                        'languages_detected': len(project_data_context.detected_languages),
                        'files_parsed': ckg_result.files_parsed,
                        'entities_found': ckg_result.entities_found,
                        'nodes_created': ckg_result.nodes_created,
                        'relationships_created': ckg_result.relationships_created
                    }
                }
            })
            
            log_performance_metric(
                self.logger,
                "full_scan_ckg_workflow_duration",
                total_duration * 1000,
                "ms",
                repository_url=task_definition.repository_url,
                ckg_success=ckg_result.success
            )
            
            log_function_exit(
                self.logger,
                "handle_scan_project_with_ckg_task",
                result="success",
                execution_time=total_duration
            )
            
            return project_data_context, ckg_result
            
        except Exception as e:
            total_duration = time.time() - start_time
            error_msg = f"Error in full scan + CKG workflow: {e}"
            self.logger.error(error_msg, exc_info=True, extra={
                'extra_data': {
                    'repository_url': task_definition.repository_url,
                    'error_type': type(e).__name__,
                    'execution_time_ms': total_duration * 1000
                }
            })
            
            log_function_exit(
                self.logger,
                "handle_scan_project_with_ckg_task",
                result="error",
                execution_time=total_duration
            )
            raise
    
    def get_task_status(self, execution_id: str) -> Optional[dict]:
        """
        Get the status of a task execution.
        
        Args:
            execution_id: ID of the task execution
            
        Returns:
            Task status information or None if not found
        """
        task_info = self._active_tasks.get(execution_id)
        if task_info:
            self.logger.info(f"Status for task {execution_id}: {task_info['status']}")
        else:
            self.logger.info(f"Task {execution_id} not found")
        
        return task_info
    
    def get_agent_stats(self) -> dict:
        """
        Get comprehensive statistics about the orchestrator agent.
        
        Returns:
            Dictionary containing agent statistics and status
        """
        start_time = time.time()
        log_function_entry(self.logger, "get_agent_stats")
        
        stats = {
            'agent_id': self.agent_id,
            'is_initialized': self._is_initialized,
            'created_at': self._initialization_time.isoformat() if self._initialization_time else None,
            'uptime_seconds': (datetime.now() - self._initialization_time).total_seconds() if self._initialization_time else 0,
            'active_tasks_count': len(self._active_tasks),
            'statistics': dict(self._stats),
            'active_tasks': {
                task_id: {
                    'status': task_info['status'],
                    'created_at': task_info['created_at'].isoformat(),
                    'repository_url': task_info['definition'].repository_url,
                    'steps_completed': len(task_info['steps_completed']),
                    'errors_count': len(task_info['errors'])
                }
                for task_id, task_info in self._active_tasks.items()
            }
        }
        
        execution_time = time.time() - start_time
        log_function_exit(self.logger, "get_agent_stats", result="success", execution_time=execution_time)
        
        return stats
    
    def shutdown(self) -> None:
        """Gracefully shutdown the orchestrator agent."""
        self.logger.info(f"Shutting down Orchestrator Agent {self.agent_id}")
        
        # Shutdown TEAM CKG Operations (Task 2.9)
        try:
            if hasattr(self, 'ckg_operations') and self.ckg_operations:
                self.logger.debug("Shutting down TEAM CKG Operations")
                self.ckg_operations.shutdown()
                self.logger.info("TEAM CKG Operations shutdown completed")
        except Exception as e:
            self.logger.warning(f"Error shutting down CKG Operations: {e}")
        
        # Log any active tasks
        if self._active_tasks:
            self.logger.info(f"Active tasks during shutdown: {len(self._active_tasks)}")
            for task_id, task_info in self._active_tasks.items():
                self.logger.info(f"  Task {task_id}: {task_info['status']}")
        
        self._is_initialized = False
        self.logger.info("Orchestrator Agent shutdown completed")
    
    def __str__(self) -> str:
        return f"OrchestratorAgent(id={self.agent_id[:8]}, initialized={self._is_initialized})" 