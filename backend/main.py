"""
RepoChat v1.0 - Main FastAPI Application

Entry point for the RepoChat backend service with comprehensive logging
and health monitoring for Docker development environment.
"""

import os
import sys
import time
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.shared.utils.logging_config import (
    get_logger, 
    log_function_entry, 
    log_function_exit,
    log_performance_metric
)
from src.shared.models.task_definition import TaskDefinition
from src.orchestrator.orchestrator_agent import OrchestratorAgent


# Global variables for application state
app_logger = get_logger("main", extra_context={'service': 'fastapi'})
orchestrator: OrchestratorAgent = None
app_start_time = datetime.now()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager with comprehensive logging.
    Handles startup and shutdown procedures.
    """
    global orchestrator
    startup_time = time.time()
    
    app_logger.info("Starting RepoChat FastAPI application", extra={
        'extra_data': {
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'log_level': os.getenv('LOG_LEVEL', 'DEBUG'),
            'neo4j_uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            'startup_time': datetime.now().isoformat()
        }
    })
    
    try:
        # Initialize Orchestrator Agent
        app_logger.info("Initializing Orchestrator Agent...")
        orchestrator = OrchestratorAgent()
        
        startup_duration = time.time() - startup_time
        log_performance_metric(
            app_logger,
            "application_startup_time",
            startup_duration * 1000,
            "ms",
            environment=os.getenv('ENVIRONMENT', 'development')
        )
        
        app_logger.info("RepoChat application started successfully", extra={
            'extra_data': {
                'startup_duration_ms': startup_duration * 1000,
                'orchestrator_id': orchestrator.agent_id,
                'status': 'ready'
            }
        })
        
        yield
        
    except Exception as e:
        app_logger.error(f"Failed to start application: {e}", exc_info=True)
        raise
    finally:
        # Shutdown procedures
        shutdown_time = time.time()
        app_logger.info("Shutting down RepoChat application...")
        
        if orchestrator:
            try:
                orchestrator.shutdown()
                app_logger.info("Orchestrator Agent shutdown completed")
            except Exception as e:
                app_logger.error(f"Error during orchestrator shutdown: {e}", exc_info=True)
        
        shutdown_duration = time.time() - shutdown_time
        app_logger.info("Application shutdown completed", extra={
            'extra_data': {
                'shutdown_duration_ms': shutdown_duration * 1000,
                'total_uptime_seconds': (datetime.now() - app_start_time).total_seconds()
            }
        })


# Create FastAPI application
app = FastAPI(
    title="RepoChat API",
    description="AI-powered repository analysis and code review assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_orchestrator() -> OrchestratorAgent:
    """
    Dependency to get the orchestrator agent instance.
    
    Returns:
        OrchestratorAgent: The global orchestrator instance
        
    Raises:
        HTTPException: If orchestrator is not available
    """
    if orchestrator is None:
        app_logger.error("Orchestrator agent is not available")
        raise HTTPException(
            status_code=503, 
            detail="Orchestrator service is not available"
        )
    return orchestrator


@app.get("/")
async def root():
    """
    Root endpoint with basic service information.
    """
    start_time = time.time()
    log_function_entry(app_logger, "root")
    
    uptime = datetime.now() - app_start_time
    
    response = {
        "service": "RepoChat API",
        "version": "1.0.0",
        "status": "healthy",
        "uptime_seconds": uptime.total_seconds(),
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }
    
    execution_time = time.time() - start_time
    log_function_exit(app_logger, "root", result="success", execution_time=execution_time)
    
    return response


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint for Docker monitoring.
    """
    start_time = time.time()
    log_function_entry(app_logger, "health_check")
    
    try:
        # Check orchestrator health
        orchestrator_healthy = False
        orchestrator_info = {}
        
        if orchestrator:
            orchestrator_info = orchestrator.get_agent_stats()
            orchestrator_healthy = orchestrator_info.get('is_initialized', False)
        
        # System health info
        health_data = {
            "status": "healthy" if orchestrator_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - app_start_time).total_seconds(),
            "checks": {
                "orchestrator": {
                    "status": "healthy" if orchestrator_healthy else "unhealthy",
                    "details": orchestrator_info
                },
                "environment": {
                    "log_level": os.getenv("LOG_LEVEL", "DEBUG"),
                    "neo4j_uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                    "environment": os.getenv("ENVIRONMENT", "development")
                }
            }
        }
        
        status_code = 200 if orchestrator_healthy else 503
        
        execution_time = time.time() - start_time
        log_function_exit(
            app_logger, 
            "health_check", 
            result=f"status_{status_code}", 
            execution_time=execution_time
        )
        
        return JSONResponse(content=health_data, status_code=status_code)
        
    except Exception as e:
        app_logger.error(f"Health check failed: {e}", exc_info=True)
        
        error_response = {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        
        log_function_exit(app_logger, "health_check", result="error", execution_time=time.time() - start_time)
        return JSONResponse(content=error_response, status_code=503)


@app.post("/tasks")
async def create_task(
    task_definition: TaskDefinition,
    agent: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Create a new task for repository analysis.
    
    Args:
        task_definition: Task definition containing repository information
        agent: Orchestrator agent dependency
        
    Returns:
        Task creation response with execution ID
    """
    start_time = time.time()
    log_function_entry(
        app_logger, 
        "create_task",
        repository_url=task_definition.repository_url
    )
    
    try:
        app_logger.info(f"Creating new task for repository: {task_definition.repository_url}")
        
        # Handle task with orchestrator
        execution_id = agent.handle_task(task_definition)
        
        response = {
            "execution_id": execution_id,
            "status": "created",
            "task_definition": {
                "repository_url": task_definition.repository_url,
                "task_id": task_definition.task_id,
                "created_at": task_definition.created_at.isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
        execution_time = time.time() - start_time
        log_performance_metric(
            app_logger,
            "task_creation_time",
            execution_time * 1000,
            "ms",
            repository_url=task_definition.repository_url,
            execution_id=execution_id
        )
        
        app_logger.info(f"Task created successfully: {execution_id}", extra={
            'extra_data': {
                'execution_id': execution_id,
                'repository_url': task_definition.repository_url,
                'execution_time_ms': execution_time * 1000
            }
        })
        
        log_function_exit(app_logger, "create_task", result=execution_id, execution_time=execution_time)
        return response
        
    except Exception as e:
        app_logger.error(f"Failed to create task: {e}", exc_info=True, extra={
            'extra_data': {
                'repository_url': task_definition.repository_url,
                'error_type': type(e).__name__
            }
        })
        
        log_function_exit(app_logger, "create_task", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@app.get("/tasks/{execution_id}")
async def get_task_status(
    execution_id: str,
    agent: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Get the status of a specific task.
    
    Args:
        execution_id: Task execution ID
        agent: Orchestrator agent dependency
        
    Returns:
        Task status information
    """
    start_time = time.time()
    log_function_entry(app_logger, "get_task_status", execution_id=execution_id)
    
    try:
        task_info = agent.get_task_status(execution_id)
        
        if task_info is None:
            app_logger.warning(f"Task not found: {execution_id}")
            log_function_exit(app_logger, "get_task_status", result="not_found", execution_time=time.time() - start_time)
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Prepare response
        response = {
            "execution_id": execution_id,
            "status": task_info['status'],
            "created_at": task_info['created_at'].isoformat(),
            "steps_completed": task_info.get('steps_completed', []),
            "errors": task_info.get('errors', []),
            "repository_url": task_info['definition'].repository_url,
            "timestamp": datetime.now().isoformat()
        }
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "get_task_status", result="found", execution_time=execution_time)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Failed to get task status: {e}", exc_info=True)
        log_function_exit(app_logger, "get_task_status", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@app.get("/stats")
async def get_stats(agent: OrchestratorAgent = Depends(get_orchestrator)):
    """
    Get comprehensive system statistics.
    
    Args:
        agent: Orchestrator agent dependency
        
    Returns:
        System and agent statistics
    """
    start_time = time.time()
    log_function_entry(app_logger, "get_stats")
    
    try:
        orchestrator_stats = agent.get_agent_stats()
        
        stats = {
            "system": {
                "uptime_seconds": (datetime.now() - app_start_time).total_seconds(),
                "environment": os.getenv("ENVIRONMENT", "development"),
                "log_level": os.getenv("LOG_LEVEL", "DEBUG"),
                "timestamp": datetime.now().isoformat()
            },
            "orchestrator": orchestrator_stats
        }
        
        execution_time = time.time() - start_time
        log_function_exit(app_logger, "get_stats", result="success", execution_time=execution_time)
        
        return stats
        
    except Exception as e:
        app_logger.error(f"Failed to get stats: {e}", exc_info=True)
        log_function_exit(app_logger, "get_stats", result="error", execution_time=time.time() - start_time)
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


if __name__ == "__main__":
    # This allows running the app directly for development
    app_logger.info("Starting RepoChat in direct mode")
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 