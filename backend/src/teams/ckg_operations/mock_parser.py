"""
Mock Language Parser for TEAM CKG Operations Testing

Provides a mock implementation of BaseLanguageParser for testing purposes.
This allows testing of CodeParserCoordinatorModule without requiring 
full implementation of language-specific parsers.

Used for development and testing of Task 2.2 functionality.
"""

import os
import time
from typing import List, Dict, Any
from pathlib import Path

from .base_parser import BaseLanguageParser
from .models import (
    ParseResult, 
    CodeEntity, 
    CallRelationship, 
    CodeEntityType, 
    VisibilityModifier
)


class MockLanguageParser(BaseLanguageParser):
    """
    Mock implementation of BaseLanguageParser for testing purposes.
    
    This parser simulates the behavior of a real language parser by:
    - Finding source files with specified extensions
    - Creating mock code entities and relationships
    - Simulating realistic parsing timing and statistics
    """
    
    def __init__(self, language: str, supported_extensions: List[str], 
                 mock_entities_per_file: int = 3, mock_relationships_per_file: int = 2):
        """
        Initialize the mock parser.
        
        Args:
            language: Programming language name
            supported_extensions: File extensions this parser handles
            mock_entities_per_file: Number of mock entities to create per file
            mock_relationships_per_file: Number of mock relationships per file
        """
        super().__init__(language, supported_extensions)
        
        self.mock_entities_per_file = mock_entities_per_file
        self.mock_relationships_per_file = mock_relationships_per_file
        self.parser_version = "MockParser-1.0.0"
        
        # Mock data templates
        self.entity_templates = [
            ('Calculator', CodeEntityType.CLASS),
            ('add', CodeEntityType.METHOD),
            ('subtract', CodeEntityType.METHOD),
            ('multiply', CodeEntityType.FUNCTION),
            ('divide', CodeEntityType.FUNCTION),
            ('main', CodeEntityType.FUNCTION),
            ('UserService', CodeEntityType.CLASS),
            ('createUser', CodeEntityType.METHOD),
            ('updateUser', CodeEntityType.METHOD),
            ('deleteUser', CodeEntityType.METHOD)
        ]
        
        self.logger.info(f"Mock {language} parser initialized with {mock_entities_per_file} entities per file")
    
    def parse_file(self, file_path: str, project_root: str) -> ParseResult:
        """
        Mock parse a single source file.
        
        Creates realistic mock entities and relationships based on file name
        and simulates parsing timing.
        
        Args:
            file_path: Absolute path to the source file
            project_root: Absolute path to the project root
            
        Returns:
            ParseResult with mock entities and relationships
        """
        start_time = time.time()
        
        # Extract relative path
        relative_path = self._extract_relative_path(file_path, project_root)
        
        # Initialize result
        result = ParseResult(
            file_path=relative_path,
            language=self.language
        )
        
        # Check if file exists
        if not os.path.exists(file_path):
            result.errors.append(f"File not found: {file_path}")
            return result
        
        try:
            # Simulate some parsing time based on file size
            file_size = os.path.getsize(file_path)
            simulated_parse_time = max(0.001, file_size / 10000)  # Simulate processing time
            time.sleep(min(simulated_parse_time, 0.1))  # Cap at 100ms for testing
            
            # Create mock entities based on file name
            file_name = Path(file_path).stem
            class_name = file_name.replace('_', '').replace('-', '').title()
            
            # Create mock entities
            entities = self._create_mock_entities(file_name, class_name, relative_path)
            result.entities = entities[:self.mock_entities_per_file]
            
            # Create mock relationships
            relationships = self._create_mock_relationships(entities, relative_path)
            result.relationships = relationships[:self.mock_relationships_per_file]
            
            self.logger.debug(f"Mock parsed {relative_path}: {len(result.entities)} entities, {len(result.relationships)} relationships")
            
        except Exception as e:
            error_msg = f"Mock parsing error: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(f"Mock parse error for {relative_path}: {e}")
        
        # Record timing
        result.parse_duration_ms = (time.time() - start_time) * 1000
        
        # Add some mock metadata
        result.metadata = {
            'mock_parser': True,
            'file_size_bytes': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            'mock_entities_requested': self.mock_entities_per_file,
            'mock_relationships_requested': self.mock_relationships_per_file
        }
        
        return result
    
    def get_parser_version(self) -> str:
        """Get the mock parser version."""
        return self.parser_version
    
    def _create_mock_entities(self, file_name: str, class_name: str, file_path: str) -> List[CodeEntity]:
        """Create mock code entities for a file."""
        entities = []
        
        # Create a mock class entity
        class_entity = CodeEntity(
            entity_type=CodeEntityType.CLASS,
            name=class_name,
            qualified_name=f"{self.language}.{class_name}",
            file_path=file_path,
            start_line=1,
            end_line=50,
            visibility=VisibilityModifier.PUBLIC,
            language=self.language,
            metadata={'mock': True, 'file_based': True}
        )
        entities.append(class_entity)
        
        # Create mock methods/functions
        method_templates = [
            f"get{class_name}",
            f"set{class_name}",
            f"create{class_name}",
            f"update{class_name}",
            f"delete{class_name}",
            "toString",
            "equals",
            "hashCode"
        ]
        
        for i, method_name in enumerate(method_templates):
            if len(entities) >= self.mock_entities_per_file:
                break
                
            entity_type = CodeEntityType.METHOD if i < 5 else CodeEntityType.FUNCTION
            start_line = 10 + (i * 5)
            
            method_entity = CodeEntity(
                entity_type=entity_type,
                name=method_name,
                qualified_name=f"{self.language}.{class_name}.{method_name}",
                file_path=file_path,
                start_line=start_line,
                end_line=start_line + 4,
                visibility=VisibilityModifier.PUBLIC if i < 3 else VisibilityModifier.PRIVATE,
                parent_entity=class_name if entity_type == CodeEntityType.METHOD else None,
                signature=f"{method_name}()" if entity_type == CodeEntityType.FUNCTION else f"public void {method_name}()",
                return_type="void" if i < 4 else "String",
                language=self.language,
                metadata={'mock': True, 'method_index': i}
            )
            entities.append(method_entity)
        
        return entities
    
    def _create_mock_relationships(self, entities: List[CodeEntity], file_path: str) -> List[CallRelationship]:
        """Create mock call relationships between entities."""
        relationships = []
        
        if len(entities) < 2:
            return relationships
        
        # Create some mock call relationships
        for i in range(min(len(entities) - 1, self.mock_relationships_per_file)):
            caller = entities[i]
            callee = entities[i + 1]
            
            relationship = CallRelationship(
                caller=caller.qualified_name or f"{caller.parent_entity}.{caller.name}" if caller.parent_entity else caller.name,
                callee=callee.qualified_name or f"{callee.parent_entity}.{callee.name}" if callee.parent_entity else callee.name,
                call_type="direct",
                file_path=file_path,
                line_number=caller.start_line + 2 if caller.start_line else None,
                language=self.language
            )
            relationships.append(relationship)
        
        return relationships


class MockJavaParser(MockLanguageParser):
    """Mock Java parser for testing."""
    
    def __init__(self):
        super().__init__("java", [".java"], mock_entities_per_file=4, mock_relationships_per_file=3)


class MockPythonParser(MockLanguageParser):
    """Mock Python parser for testing."""
    
    def __init__(self):
        super().__init__("python", [".py"], mock_entities_per_file=3, mock_relationships_per_file=2)


class MockKotlinParser(MockLanguageParser):
    """Mock Kotlin parser for testing."""
    
    def __init__(self):
        super().__init__("kotlin", [".kt"], mock_entities_per_file=3, mock_relationships_per_file=2)


class MockDartParser(MockLanguageParser):
    """Mock Dart parser for testing."""
    
    def __init__(self):
        super().__init__("dart", [".dart"], mock_entities_per_file=2, mock_relationships_per_file=1) 