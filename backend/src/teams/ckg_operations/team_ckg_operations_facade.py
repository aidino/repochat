"""
TEAM CKG Operations Facade for Orchestrator Integration

This facade provides a simplified interface for the Orchestrator Agent to interact
with the TEAM CKG Operations components. It coordinates the workflow from parsing
to CKG building and provides status reporting.

Implements Task 2.9 (F2.9) requirements:
- Receives ProjectDataContext from Orchestrator
- Coordinates parsing and CKG building workflow
- Reports status (success/failure) back to Orchestrator
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from shared.models.project_data_context import ProjectDataContext
from shared.utils.logging_config import (
    get_logger, 
    log_function_entry, 
    log_function_exit, 
    log_performance_metric
)

from .code_parser_coordinator_module import CodeParserCoordinatorModule
from .neo4j_connection_module import Neo4jConnectionModule
from .ast_to_ckg_builder_module import ASTtoCKGBuilderModule, CKGBuildResult
from .models import CoordinatorParseResult


@dataclass
class CKGOperationResult:
    """Result of TEAM CKG Operations workflow."""
    success: bool
    project_name: str
    operation_duration_ms: float = 0.0
    
    # Parsing statistics
    files_parsed: int = 0
    entities_found: int = 0
    relationships_found: int = 0
    languages_processed: list = None
    
    # CKG building statistics  
    nodes_created: int = 0
    relationships_created: int = 0
    files_processed: int = 0
    ckg_build_duration_ms: float = 0.0
    
    # Error information
    errors: list = None
    warnings: list = None
    
    def __post_init__(self):
        if self.languages_processed is None:
            self.languages_processed = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class TeamCKGOperationsFacade:
    """
    Facade for TEAM CKG Operations that coordinates the complete workflow
    from code parsing to CKG building.
    
    This facade simplifies the interaction between Orchestrator and the
    various CKG Operations modules.
    """
    
    def __init__(self, neo4j_connection: Optional[Neo4jConnectionModule] = None):
        """
        Initialize TEAM CKG Operations facade.
        
        Args:
            neo4j_connection: Optional Neo4j connection. If None, creates new one.
        """
        self.logger = get_logger("team.ckg_operations.facade")
        
        # Initialize core components
        self.parser_coordinator = CodeParserCoordinatorModule()
        self.neo4j_connection = neo4j_connection or Neo4jConnectionModule()
        self.ckg_builder = ASTtoCKGBuilderModule(self.neo4j_connection)
        
        # Operation statistics
        self._operation_count = 0
        self._total_processing_time = 0.0
        
        self.logger.info("TEAM CKG Operations Facade initialized", extra={
            'extra_data': {
                'components_initialized': [
                    'CodeParserCoordinatorModule',
                    'Neo4jConnectionModule', 
                    'ASTtoCKGBuilderModule'
                ]
            }
        })
    
    def process_project_data_context(
        self, 
        project_data_context: ProjectDataContext,
        project_name: Optional[str] = None
    ) -> CKGOperationResult:
        """
        Process ProjectDataContext to build Code Knowledge Graph.
        
        This is the main entry point for TEAM CKG Operations workflow:
        1. Coordinate parsing of source code
        2. Build CKG from parsed results
        3. Report status and statistics
        
        Args:
            project_data_context: Data context from TEAM Data Acquisition
            project_name: Optional project name for graph organization
            
        Returns:
            CKGOperationResult with detailed status and statistics
        """
        start_time = time.time()
        
        # Generate project name if not provided
        if not project_name:
            import os
            project_name = os.path.basename(project_data_context.cloned_code_path)
        
        log_function_entry(
            self.logger,
            "process_project_data_context",
            project_name=project_name,
            repository_url=project_data_context.repository_url,
            detected_languages=project_data_context.detected_languages
        )
        
        self.logger.info(f"Starting CKG Operations for project: {project_name}", extra={
            'extra_data': {
                'project_name': project_name,
                'repository_url': project_data_context.repository_url,
                'cloned_path': project_data_context.cloned_code_path,
                'detected_languages': project_data_context.detected_languages,
                'language_count': project_data_context.language_count
            }
        })
        
        # Initialize result
        result = CKGOperationResult(
            success=False,
            project_name=project_name,
            languages_processed=project_data_context.detected_languages.copy()
        )
        
        try:
            # Step 1: Coordinate parsing
            self.logger.info("Step 1: Coordinating code parsing")
            parsing_start = time.time()
            
            coordinator_result = self.parser_coordinator.coordinate_parsing(
                project_data_context
            )
            
            parsing_duration = time.time() - parsing_start
            self.logger.info("Code parsing completed", extra={
                'extra_data': {
                    'parsing_duration_ms': parsing_duration * 1000,
                    'files_parsed': coordinator_result.total_files_parsed,
                    'entities_found': coordinator_result.total_entities_found,
                    'relationships_found': coordinator_result.total_relationships_found,
                    'languages_processed': coordinator_result.languages_processed
                }
            })
            
            # Update result with parsing statistics
            result.files_parsed = coordinator_result.total_files_parsed
            result.entities_found = coordinator_result.total_entities_found
            result.relationships_found = coordinator_result.total_relationships_found
            
            # Step 2: Build CKG
            self.logger.info("Step 2: Building Code Knowledge Graph")
            ckg_start = time.time()
            
            # Ensure Neo4j connection
            if not self.neo4j_connection.is_connected():
                self.logger.info("Establishing Neo4j connection")
                if not self.neo4j_connection.connect():
                    raise RuntimeError("Failed to connect to Neo4j database")
            
            ckg_build_result = self.ckg_builder.build_ckg_from_coordinator_result(
                coordinator_result,
                project_name
            )
            
            ckg_duration = time.time() - ckg_start
            
            if ckg_build_result.success:
                self.logger.info("CKG building completed successfully", extra={
                    'extra_data': {
                        'ckg_build_duration_ms': ckg_duration * 1000,
                        'nodes_created': ckg_build_result.nodes_created,
                        'relationships_created': ckg_build_result.relationships_created,
                        'files_processed': ckg_build_result.files_processed
                    }
                })
                
                # Update result with CKG statistics
                result.nodes_created = ckg_build_result.nodes_created
                result.relationships_created = ckg_build_result.relationships_created
                result.files_processed = ckg_build_result.files_processed
                result.ckg_build_duration_ms = ckg_build_result.build_duration_ms
                result.success = True
                
            else:
                self.logger.error("CKG building failed", extra={
                    'extra_data': {
                        'errors': ckg_build_result.errors,
                        'warnings': ckg_build_result.warnings
                    }
                })
                result.errors.extend(ckg_build_result.errors)
                result.warnings.extend(ckg_build_result.warnings)
                
        except Exception as e:
            error_msg = f"Error in CKG Operations workflow: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            result.errors.append(error_msg)
            
        # Record timing and statistics
        total_duration = time.time() - start_time
        result.operation_duration_ms = total_duration * 1000
        
        self._operation_count += 1
        self._total_processing_time += total_duration
        
        # Log final result
        if result.success:
            self.logger.info(f"CKG Operations completed successfully for {project_name}", extra={
                'extra_data': {
                    'total_duration_ms': result.operation_duration_ms,
                    'parsing_success': result.files_parsed > 0,
                    'ckg_build_success': result.nodes_created > 0,
                    'overall_statistics': {
                        'files_parsed': result.files_parsed,
                        'entities_found': result.entities_found,
                        'relationships_found': result.relationships_found,
                        'nodes_created': result.nodes_created,
                        'relationships_created': result.relationships_created
                    }
                }
            })
        else:
            self.logger.error(f"CKG Operations failed for {project_name}", extra={
                'extra_data': {
                    'total_duration_ms': result.operation_duration_ms,
                    'errors': result.errors,
                    'warnings': result.warnings
                }
            })
        
        log_performance_metric(
            self.logger,
            "ckg_operations_total_duration",
            result.operation_duration_ms,
            "ms",
            project_name=project_name,
            success=result.success
        )
        
        log_function_exit(
            self.logger,
            "process_project_data_context",
            result="success" if result.success else "failed",
            execution_time=total_duration
        )
        
        return result
    
    def get_operation_statistics(self) -> Dict[str, Any]:
        """Get facade operation statistics."""
        avg_processing_time = (
            self._total_processing_time / self._operation_count 
            if self._operation_count > 0 else 0.0
        )
        
        return {
            'total_operations': self._operation_count,
            'total_processing_time_seconds': self._total_processing_time,
            'average_processing_time_seconds': avg_processing_time,
            'neo4j_connected': self.neo4j_connection.is_connected()
        }
    
    def is_ready(self) -> bool:
        """Check if TEAM CKG Operations is ready to process requests."""
        try:
            # Check if Neo4j is available
            if not self.neo4j_connection.is_connected():
                return self.neo4j_connection.connect()
            return True
        except Exception as e:
            self.logger.warning(f"CKG Operations not ready: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown TEAM CKG Operations facade."""
        self.logger.info("Shutting down TEAM CKG Operations Facade")
        
        try:
            if self.neo4j_connection.is_connected():
                self.neo4j_connection.disconnect()
                self.logger.info("Neo4j connection closed")
        except Exception as e:
            self.logger.warning(f"Error closing Neo4j connection: {e}")
        
        self.logger.info(f"Facade shutdown complete. Processed {self._operation_count} operations.") 