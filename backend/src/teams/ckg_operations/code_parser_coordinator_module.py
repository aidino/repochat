"""
Code Parser Coordinator Module for TEAM CKG Operations

Coordinates and manages language parsers theo yêu cầu Task 2.2

This module serves as the central coordinator that:
- Receives ProjectDataContext from TEAM Data Acquisition
- Dispatches parsing tasks to appropriate language parsers
- Aggregates results from all parsers
- Returns comprehensive parsing results for CKG construction

Enhanced for Task 2.2 (F2.2) requirements.
"""

from typing import Dict, List, Optional, Type, Any
import time
import os
from datetime import datetime

from shared.models.project_data_context import ProjectDataContext
from .models import CoordinatorParseResult, LanguageParseResult
from .base_parser import BaseLanguageParser
from shared.utils.logging_config import (
    get_logger,
    log_function_entry,
    log_function_exit,
    log_performance_metric
)


class CodeParserCoordinatorModule:
    """
    Coordinates parsing operations across multiple programming languages.
    
    This module acts as a central dispatcher that manages language-specific 
    parsers and aggregates their results into a unified format for CKG construction.
    """
    
    def __init__(self):
        """Initialize the Code Parser Coordinator Module."""
        start_time = time.time()
        
        # Setup logging
        self.logger = get_logger(
            "ckg_operations.code_parser_coordinator",
            extra_context={'component': 'CodeParserCoordinatorModule'}
        )
        
        log_function_entry(self.logger, "__init__")
        
        # Registry of available language parsers
        self._parser_registry: Dict[str, BaseLanguageParser] = {}
        
        # Supported languages mapping
        self._language_mapping = {
            'java': 'java',
            'python': 'python',
            'kotlin': 'kotlin',
            'dart': 'dart',
            'javascript': 'javascript',
            'typescript': 'typescript'
        }
        
        # Statistics tracking
        self._stats = {
            'coordination_sessions': 0,
            'total_languages_processed': 0,
            'total_files_coordinated': 0,
            'total_entities_coordinated': 0,
            'total_relationships_coordinated': 0,
            'total_coordination_time_ms': 0.0,
            'parser_registrations': 0
        }
        
        self.logger.info("Code Parser Coordinator Module initialized", extra={
            'extra_data': {
                'supported_language_mappings': list(self._language_mapping.keys()),
                'registered_parsers': list(self._parser_registry.keys())
            }
        })
        
        init_time = time.time() - start_time
        log_performance_metric(
            self.logger,
            "coordinator_init_time",
            init_time * 1000,
            "ms"
        )
        log_function_exit(self.logger, "__init__", result="success", execution_time=init_time)
    
    def register_parser(self, parser: BaseLanguageParser) -> None:
        """
        Register a language-specific parser with the coordinator.
        
        Args:
            parser: Instance of a language parser that inherits from BaseLanguageParser
            
        Raises:
            ValueError: If parser is invalid or language already registered
        """
        if not isinstance(parser, BaseLanguageParser):
            raise ValueError("Parser must inherit from BaseLanguageParser")
        
        log_function_entry(self.logger, "register_parser", parser_language=parser.language)
        
        if parser.language in self._parser_registry:
            self.logger.warning(f"Parser for {parser.language} already registered, replacing")
        
        self._parser_registry[parser.language] = parser
        self._stats['parser_registrations'] += 1
        
        self.logger.info(f"Registered {parser.language} parser", extra={
            'extra_data': {
                'language': parser.language,
                'parser_type': type(parser).__name__,
                'supported_extensions': parser.supported_extensions,
                'parser_version': parser.get_parser_version()
            }
        })
        
        log_function_exit(self.logger, "register_parser", result="success", execution_time=0)
    
    def unregister_parser(self, language: str) -> bool:
        """
        Unregister a language parser.
        
        Args:
            language: Programming language name
            
        Returns:
            True if parser was unregistered, False if not found
        """
        language = language.lower()
        if language in self._parser_registry:
            del self._parser_registry[language]
            self.logger.info(f"Unregistered {language} parser")
            return True
        return False
    
    def get_registered_languages(self) -> List[str]:
        """
        Get list of currently registered programming languages.
        
        Returns:
            List of registered language names
        """
        return list(self._parser_registry.keys())
    
    def has_parser_for_language(self, language: str) -> bool:
        """
        Check if a parser is registered for the given language.
        
        Args:
            language: Programming language name
            
        Returns:
            True if parser is available, False otherwise
        """
        return language.lower() in self._parser_registry
    
    def coordinate_parsing(self, project_data_context: ProjectDataContext) -> CoordinatorParseResult:
        """
        Coordinate parsing of the project across all detected languages.
        
        This is the main entry point that fulfills Task 2.2 requirements:
        - Receives ProjectDataContext with detected_languages and cloned_code_path
        - Calls appropriate language parsers based on detected_languages
        - Aggregates results from all parsers
        
        Args:
            project_data_context: Context from TEAM Data Acquisition
            
        Returns:
            CoordinatorParseResult with aggregated parsing results
        """
        start_time = time.time()
        log_function_entry(
            self.logger, 
            "coordinate_parsing",
            project_path=project_data_context.cloned_code_path,
            detected_languages=project_data_context.detected_languages
        )
        
        self._stats['coordination_sessions'] += 1
        
        # Initialize result structure
        coordinator_result = CoordinatorParseResult(
            project_path=project_data_context.cloned_code_path,
            languages_processed=[]
        )
        
        # Validate inputs
        if not project_data_context.cloned_code_path:
            error_msg = "ProjectDataContext missing cloned_code_path"
            coordinator_result.errors.append(error_msg)
            self.logger.error(error_msg)
            return coordinator_result
        
        if not os.path.exists(project_data_context.cloned_code_path):
            error_msg = f"Project path does not exist: {project_data_context.cloned_code_path}"
            coordinator_result.errors.append(error_msg)
            self.logger.error(error_msg)
            return coordinator_result
        
        if not project_data_context.detected_languages:
            warning_msg = "No languages detected in ProjectDataContext"
            coordinator_result.warnings.append(warning_msg)
            self.logger.warning(warning_msg)
            coordinator_result.coordination_duration_ms = (time.time() - start_time) * 1000
            log_function_exit(self.logger, "coordinate_parsing", result="no languages", execution_time=time.time() - start_time)
            return coordinator_result
        
        # Process each detected language
        for language in project_data_context.detected_languages:
            language_normalized = language.lower().strip()
            
            # Map language variants to canonical names
            canonical_language = self._language_mapping.get(language_normalized, language_normalized)
            
            if not self.has_parser_for_language(canonical_language):
                warning_msg = f"No parser available for language: {language}"
                coordinator_result.warnings.append(warning_msg)
                self.logger.warning(warning_msg, extra={
                    'extra_data': {
                        'language': language,
                        'canonical_language': canonical_language,
                        'available_parsers': list(self._parser_registry.keys())
                    }
                })
                continue
            
            # Get parser and process language
            try:
                parser = self._parser_registry[canonical_language]
                
                self.logger.info(f"Starting parsing for {canonical_language}", extra={
                    'extra_data': {
                        'language': canonical_language,
                        'parser_type': type(parser).__name__,
                        'project_path': project_data_context.cloned_code_path
                    }
                })
                
                # Execute language-specific parsing
                language_result = parser.parse_project(project_data_context.cloned_code_path)
                
                # Store results
                coordinator_result.language_results[canonical_language] = language_result
                coordinator_result.languages_processed.append(canonical_language)
                
                # Update aggregate statistics
                coordinator_result.total_files_parsed += len(language_result.files_parsed)
                coordinator_result.total_entities_found += language_result.total_entities
                coordinator_result.total_relationships_found += language_result.total_relationships
                
                # Update coordinator statistics
                self._stats['total_languages_processed'] += 1
                self._stats['total_files_coordinated'] += len(language_result.files_parsed)
                self._stats['total_entities_coordinated'] += language_result.total_entities
                self._stats['total_relationships_coordinated'] += language_result.total_relationships
                
                self.logger.info(f"Completed parsing for {canonical_language}", extra={
                    'extra_data': {
                        'language': canonical_language,
                        'files_parsed': len(language_result.files_parsed),
                        'entities_found': language_result.total_entities,
                        'relationships_found': language_result.total_relationships,
                        'files_with_errors': language_result.files_with_errors,
                        'parse_duration_ms': language_result.parse_duration_ms
                    }
                })
                
            except Exception as e:
                error_msg = f"Failed to parse {canonical_language}: {str(e)}"
                coordinator_result.errors.append(error_msg)
                self.logger.error(error_msg, exc_info=True, extra={
                    'extra_data': {
                        'language': canonical_language,
                        'project_path': project_data_context.cloned_code_path
                    }
                })
        
        # Finalize coordination results
        total_time = time.time() - start_time
        coordinator_result.coordination_duration_ms = total_time * 1000
        self._stats['total_coordination_time_ms'] += coordinator_result.coordination_duration_ms
        
        # Log final summary
        self.logger.info("Coordination parsing completed", extra={
            'extra_data': {
                'project_path': project_data_context.cloned_code_path,
                'languages_requested': project_data_context.detected_languages,
                'languages_processed': coordinator_result.languages_processed,
                'total_files_parsed': coordinator_result.total_files_parsed,
                'total_entities_found': coordinator_result.total_entities_found,
                'total_relationships_found': coordinator_result.total_relationships_found,
                'success_rate': coordinator_result.success_rate,
                'coordination_duration_ms': coordinator_result.coordination_duration_ms,
                'errors_count': len(coordinator_result.errors),
                'warnings_count': len(coordinator_result.warnings)
            }
        })
        
        log_performance_metric(
            self.logger,
            "coordination_parse_time",
            coordinator_result.coordination_duration_ms,
            "ms"
        )
        
        log_function_exit(
            self.logger, 
            "coordinate_parsing",
            result=f"{coordinator_result.total_entities_found} entities, {coordinator_result.total_relationships_found} relationships",
            execution_time=total_time
        )
        
        return coordinator_result
    
    def get_parser_info(self, language: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered parser.
        
        Args:
            language: Programming language name
            
        Returns:
            Dictionary with parser information or None if not found
        """
        language = language.lower()
        if language not in self._parser_registry:
            return None
        
        parser = self._parser_registry[language]
        return {
            'language': parser.language,
            'parser_type': type(parser).__name__,
            'supported_extensions': parser.supported_extensions,
            'parser_version': parser.get_parser_version(),
            'parser_stats': parser.get_stats()
        }
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """
        Get coordination statistics.
        
        Returns:
            Dictionary containing coordination statistics
        """
        stats = self._stats.copy()
        stats.update({
            'registered_parsers': list(self._parser_registry.keys()),
            'supported_language_mappings': self._language_mapping,
            'average_coordination_time_ms': (
                self._stats['total_coordination_time_ms'] / self._stats['coordination_sessions']
                if self._stats['coordination_sessions'] > 0 else 0
            ),
            'average_entities_per_session': (
                self._stats['total_entities_coordinated'] / self._stats['coordination_sessions']
                if self._stats['coordination_sessions'] > 0 else 0
            )
        })
        return stats
    
    def validate_project_data_context(self, project_data_context: ProjectDataContext) -> List[str]:
        """
        Validate ProjectDataContext for parsing coordination.
        
        Args:
            project_data_context: Context to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not project_data_context:
            errors.append("ProjectDataContext is None")
            return errors
        
        if not project_data_context.cloned_code_path:
            errors.append("cloned_code_path is missing or empty")
        elif not os.path.exists(project_data_context.cloned_code_path):
            errors.append(f"cloned_code_path does not exist: {project_data_context.cloned_code_path}")
        elif not os.path.isdir(project_data_context.cloned_code_path):
            errors.append(f"cloned_code_path is not a directory: {project_data_context.cloned_code_path}")
        
        if not project_data_context.detected_languages:
            errors.append("detected_languages list is empty")
        else:
            # Check if we have parsers for detected languages
            unsupported_languages = []
            for language in project_data_context.detected_languages:
                canonical = self._language_mapping.get(language.lower(), language.lower())
                if not self.has_parser_for_language(canonical):
                    unsupported_languages.append(language)
            
            if unsupported_languages:
                errors.append(f"No parsers available for languages: {unsupported_languages}")
        
        return errors
    
    def __str__(self) -> str:
        return f"CodeParserCoordinatorModule(parsers={list(self._parser_registry.keys())})"
    
    def __repr__(self) -> str:
        return (f"CodeParserCoordinatorModule(registered_parsers={len(self._parser_registry)}, "
                f"coordination_sessions={self._stats['coordination_sessions']})") 