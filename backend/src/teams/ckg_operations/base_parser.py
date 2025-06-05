"""
Abstract Base Parser for TEAM CKG Operations

Defines the interface that all language-specific parsers must implement
for the CodeParserCoordinatorModule.

This ensures consistency across different language parsers (Java, Python, etc.)
and provides a standardized way to handle parsing operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Set
import os
import time
from pathlib import Path

from .models import ParseResult, LanguageParseResult, CodeEntity, CallRelationship
from shared.utils.logging_config import (
    get_logger,
    log_function_entry,
    log_function_exit,
    log_performance_metric
)


class BaseLanguageParser(ABC):
    """
    Abstract base class for language-specific code parsers.
    
    All language parsers (Java, Python, Kotlin, Dart) must inherit from this class
    and implement the required abstract methods.
    """
    
    def __init__(self, language: str, supported_extensions: List[str]):
        """
        Initialize the language parser.
        
        Args:
            language: Name of the programming language (e.g., "java", "python")
            supported_extensions: List of file extensions (e.g., [".java", ".kt"])
        """
        self.language = language.lower()
        self.supported_extensions = [ext.lower() for ext in supported_extensions]
        
        # Setup logging
        self.logger = get_logger(
            f"ckg_operations.{self.language}_parser",
            extra_context={'component': f'{self.language.title()}Parser'}
        )
        
        # Statistics tracking
        self._stats = {
            'files_processed': 0,
            'files_successful': 0,
            'files_with_errors': 0,
            'total_entities_found': 0,
            'total_relationships_found': 0,
            'total_parse_time_ms': 0.0
        }
        
        self.logger.info(f"{self.language.title()} parser initialized", extra={
            'extra_data': {
                'language': self.language,
                'supported_extensions': self.supported_extensions
            }
        })
    
    @abstractmethod
    def parse_file(self, file_path: str, project_root: str) -> ParseResult:
        """
        Parse a single source file and extract code entities and relationships.
        
        Args:
            file_path: Absolute path to the source file
            project_root: Absolute path to the project root directory
            
        Returns:
            ParseResult containing entities and relationships found in the file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ParsingError: If the file cannot be parsed
        """
        pass
    
    @abstractmethod
    def get_parser_version(self) -> str:
        """
        Get the version of the underlying parser library.
        
        Returns:
            Version string of the parser library being used
        """
        pass
    
    def can_parse_file(self, file_path: str) -> bool:
        """
        Check if this parser can handle the given file based on its extension.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this parser supports the file extension, False otherwise
        """
        if not file_path:
            return False
        
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.supported_extensions
    
    def find_source_files(self, project_path: str) -> List[str]:
        """
        Find all source files in the project that this parser can handle.
        
        Args:
            project_path: Absolute path to the project directory
            
        Returns:
            List of absolute paths to source files this parser can handle
        """
        start_time = time.time()
        log_function_entry(self.logger, "find_source_files", project_path=project_path)
        
        source_files = []
        
        try:
            project_root = Path(project_path)
            if not project_root.exists() or not project_root.is_dir():
                self.logger.warning(f"Project path does not exist or is not a directory: {project_path}")
                return source_files
            
            # Walk through all files in the project
            for file_path in project_root.rglob("*"):
                if file_path.is_file() and self.can_parse_file(str(file_path)):
                    source_files.append(str(file_path.absolute()))
            
            self.logger.info(f"Found {len(source_files)} {self.language} source files", extra={
                'extra_data': {
                    'language': self.language,
                    'source_files_count': len(source_files),
                    'project_path': project_path
                }
            })
            
        except Exception as e:
            self.logger.error(f"Error finding source files: {e}", exc_info=True)
        
        find_time = time.time() - start_time
        log_performance_metric(
            self.logger,
            f"{self.language}_file_discovery_time",
            find_time * 1000,
            "ms"
        )
        log_function_exit(self.logger, "find_source_files", result=f"{len(source_files)} files", execution_time=find_time)
        
        return source_files
    
    def parse_project(self, project_path: str) -> LanguageParseResult:
        """
        Parse all source files of this language in the given project.
        
        Args:
            project_path: Absolute path to the project directory
            
        Returns:
            LanguageParseResult containing aggregated parsing results
        """
        start_time = time.time()
        log_function_entry(self.logger, "parse_project", project_path=project_path)
        
        # Find all source files for this language
        source_files = self.find_source_files(project_path)
        
        # Initialize result structure
        language_result = LanguageParseResult(
            language=self.language,
            parser_version=self.get_parser_version()
        )
        
        if not source_files:
            self.logger.info(f"No {self.language} source files found in project")
            language_result.parse_duration_ms = (time.time() - start_time) * 1000
            log_function_exit(self.logger, "parse_project", result="no files", execution_time=time.time() - start_time)
            return language_result
        
        # Parse each source file
        for file_path in source_files:
            try:
                self._stats['files_processed'] += 1
                
                file_result = self.parse_file(file_path, project_path)
                language_result.files_parsed.append(file_result)
                
                # Update statistics
                if file_result.errors:
                    self._stats['files_with_errors'] += 1
                    language_result.files_with_errors += 1
                else:
                    self._stats['files_successful'] += 1
                
                # Aggregate counts
                language_result.total_entities += len(file_result.entities)
                language_result.total_relationships += len(file_result.relationships)
                
                self._stats['total_entities_found'] += len(file_result.entities)
                self._stats['total_relationships_found'] += len(file_result.relationships)
                
                if file_result.parse_duration_ms:
                    self._stats['total_parse_time_ms'] += file_result.parse_duration_ms
                
            except Exception as e:
                self.logger.error(f"Failed to parse file {file_path}: {e}", exc_info=True)
                self._stats['files_with_errors'] += 1
                language_result.files_with_errors += 1
                
                # Create error result for tracking
                error_result = ParseResult(
                    file_path=os.path.relpath(file_path, project_path),
                    language=self.language,
                    errors=[f"Parser error: {str(e)}"]
                )
                language_result.files_parsed.append(error_result)
        
        # Finalize timing and statistics
        total_time = time.time() - start_time
        language_result.parse_duration_ms = total_time * 1000
        
        self.logger.info(f"Completed parsing {self.language} project", extra={
            'extra_data': {
                'language': self.language,
                'total_files': len(source_files),
                'successful_files': self._stats['files_successful'],
                'files_with_errors': language_result.files_with_errors,
                'total_entities': language_result.total_entities,
                'total_relationships': language_result.total_relationships,
                'parse_duration_ms': language_result.parse_duration_ms
            }
        })
        
        log_performance_metric(
            self.logger,
            f"{self.language}_project_parse_time",
            language_result.parse_duration_ms,
            "ms"
        )
        
        log_function_exit(self.logger, "parse_project", 
                         result=f"{language_result.total_entities} entities, {language_result.total_relationships} relationships",
                         execution_time=total_time)
        
        return language_result
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get parsing statistics for this language parser.
        
        Returns:
            Dictionary containing parsing statistics
        """
        stats = self._stats.copy()
        stats.update({
            'language': self.language,
            'supported_extensions': self.supported_extensions,
            'parser_version': self.get_parser_version(),
            'average_parse_time_ms': (
                self._stats['total_parse_time_ms'] / self._stats['files_processed']
                if self._stats['files_processed'] > 0 else 0
            )
        })
        return stats
    
    def _extract_relative_path(self, file_path: str, project_root: str) -> str:
        """
        Extract relative path from absolute file path.
        
        Args:
            file_path: Absolute path to the file
            project_root: Absolute path to the project root
            
        Returns:
            Relative path from project root to the file
        """
        try:
            return os.path.relpath(file_path, project_root)
        except ValueError:
            # Handle case where paths are on different drives (Windows)
            return file_path
    
    def _create_qualified_name(self, entity_name: str, parent_name: Optional[str] = None, 
                             package_name: Optional[str] = None) -> str:
        """
        Create a qualified name for a code entity.
        
        Args:
            entity_name: Name of the entity
            parent_name: Name of the parent entity (e.g., class for a method)
            package_name: Package or module name
            
        Returns:
            Fully qualified name
        """
        parts = []
        
        if package_name:
            parts.append(package_name)
        if parent_name:
            parts.append(parent_name)
        if entity_name:
            parts.append(entity_name)
        
        return ".".join(parts)
    
    def __str__(self) -> str:
        return f"{self.language.title()}Parser(extensions={self.supported_extensions})"
    
    def __repr__(self) -> str:
        return (f"BaseLanguageParser(language='{self.language}', "
                f"supported_extensions={self.supported_extensions})") 