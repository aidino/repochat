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
                    'status': 'initialized'
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
            
            # Placeholder for future TEAM coordination with detailed logging:
            self.logger.debug("Future workflow steps:", extra={
                'extra_data': {
                    'planned_steps': [
                        "TEAM Data Acquisition -> clone repo, identify language",
                        "TEAM CKG Operations -> build knowledge graph",
                        "TEAM Code Analysis -> analyze code structure", 
                        "TEAM Synthesis & Reporting -> generate reports"
                    ],
                    'current_phase': "Task 1.1 - Basic setup only"
                }
            })
            
            # For Task 1.1, we just simulate successful task setup
            self.logger.info(f"Task {execution_id} setup completed successfully")
            
            # Update final task status
            self._active_tasks[execution_id]['status'] = 'setup_complete'
            self._active_tasks[execution_id]['steps_completed'].append({
                'step': 'task_setup_complete',
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
                    'final_status': 'setup_complete',
                    'steps_completed': len(self._active_tasks[execution_id]['steps_completed'])
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
        
        # Log any active tasks
        if self._active_tasks:
            self.logger.info(f"Active tasks during shutdown: {len(self._active_tasks)}")
            for task_id, task_info in self._active_tasks.items():
                self.logger.info(f"  Task {task_id}: {task_info['status']}")
        
        self._is_initialized = False
        self.logger.info("Orchestrator Agent shutdown completed")
    
    def __str__(self) -> str:
        return f"OrchestratorAgent(id={self.agent_id[:8]}, initialized={self._is_initialized})" 