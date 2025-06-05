"""
Kotlin Parser for TEAM CKG Operations

This parser analyzes Kotlin source code files and extracts:
- Classes, objects, interfaces, enums
- Functions, methods, constructors
- Properties and variables
- Function call relationships
- Package declarations and imports

Implementation uses Kotlin's AST parsing via Python subprocess execution of
a Kotlin analysis tool.
"""

import os
import re
import json
import time
import subprocess
import tempfile
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path

from .base_parser import BaseLanguageParser
from .models import ParseResult, CodeEntity, CallRelationship
from shared.utils.logging_config import (
    log_function_entry,
    log_function_exit,
    log_performance_metric
)


class KotlinParser(BaseLanguageParser):
    """
    Kotlin language parser that extracts code entities and relationships.
    
    Uses regex-based parsing with Kotlin language constructs for robustness
    when ktlint or other tools are not available.
    """
    
    def __init__(self):
        """Initialize the Kotlin parser."""
        super().__init__(language="kotlin", supported_extensions=[".kt", ".kts"])
        
        # Kotlin language patterns for parsing
        self._class_pattern = re.compile(
            r'(?:^|\s)(?:(?:private|protected|public|internal)\s+)?'
            r'(?:abstract\s+|final\s+|open\s+|sealed\s+)?'
            r'(?:class|interface|object|enum\s+class|data\s+class|inline\s+class)\s+'
            r'(\w+)',
            re.MULTILINE
        )
        
        self._function_pattern = re.compile(
            r'(?:^|\s)(?:(?:private|protected|public|internal)\s+)?'
            r'(?:override\s+|abstract\s+|open\s+|final\s+|inline\s+|suspend\s+)?'
            r'fun\s+(\w+)\s*\(',
            re.MULTILINE
        )
        
        self._property_pattern = re.compile(
            r'(?:^|\s)(?:(?:private|protected|public|internal)\s+)?'
            r'(?:val|var)\s+(\w+)',
            re.MULTILINE
        )
        
        self._function_call_pattern = re.compile(
            r'(\w+)\s*\(',
            re.MULTILINE
        )
        
        self._package_pattern = re.compile(r'^\s*package\s+([\w.]+)', re.MULTILINE)
        self._import_pattern = re.compile(r'^\s*import\s+([\w.*]+)', re.MULTILINE)
        
        # Kotlin visibility modifiers
        self._visibility_modifiers = {'private', 'protected', 'public', 'internal'}
        
        self.logger.info("Kotlin parser initialized with regex-based parsing")
    
    def get_parser_version(self) -> str:
        """Get the version of the Kotlin parser."""
        return "1.0.0-regex"
    
    def parse_file(self, file_path: str, project_root: str) -> ParseResult:
        """
        Parse a single Kotlin file and extract code entities and relationships.
        
        Args:
            file_path: Absolute path to the Kotlin file
            project_root: Absolute path to the project root directory
            
        Returns:
            ParseResult containing entities and relationships found in the file
        """
        start_time = time.time()
        log_function_entry(self.logger, "parse_file", file_path=file_path)
        
        # Update statistics
        self._stats['files_processed'] += 1
        
        result = ParseResult(
            file_path=self._extract_relative_path(file_path, project_root),
            language="kotlin"
        )
        
        try:
            # Read and parse file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract module/package name
            module_name = self._extract_module_name(file_path, project_root, content)
            
            # Parse entities and relationships using Kotlin visitor
            visitor = KotlinSourceVisitor(content, module_name, file_path)
            entities, relationships = visitor.parse()
            
            result.entities = entities
            result.relationships = relationships
            
            # Add metadata
            result.metadata = {
                'module_name': module_name,
                'file_size_bytes': len(content),
                'regex_parser': True,
                'line_count': len(content.splitlines())
            }
            
            # Update statistics for successful parsing
            self._stats['files_successful'] += 1
            self._stats['total_entities_found'] += len(entities)
            self._stats['total_relationships_found'] += len(relationships)
            
            self.logger.info(f"Successfully parsed Kotlin file: {file_path}", extra={
                'extra_data': {
                    'file_path': file_path,
                    'entities_found': len(entities),
                    'relationships_found': len(relationships),
                    'module_name': module_name
                }
            })
            
        except FileNotFoundError:
            error_msg = f"Kotlin file not found: {file_path}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)
            self._stats['files_with_errors'] += 1
            
        except UnicodeDecodeError as e:
            error_msg = f"Encoding error in Kotlin file {file_path}: {e}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)
            self._stats['files_with_errors'] += 1
            
        except Exception as e:
            error_msg = f"Failed to parse Kotlin file {file_path}: {e}"
            result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            self._stats['files_with_errors'] += 1
        
        parse_time = time.time() - start_time
        result.parse_duration_ms = parse_time * 1000
        self._stats['total_parse_time_ms'] += result.parse_duration_ms
        
        log_performance_metric(
            self.logger,
            "kotlin_file_parse_time",
            result.parse_duration_ms,
            "ms"
        )
        log_function_exit(
            self.logger, 
            "parse_file", 
            result=f"{len(result.entities)} entities, {len(result.relationships)} relationships",
            execution_time=parse_time
        )
        
        return result
    
    def _extract_module_name(self, file_path: str, project_root: str, content: str) -> str:
        """
        Extract module name from Kotlin file.
        
        Uses package declaration if available, otherwise derives from file path.
        """
        # Try to extract package declaration
        package_match = self._package_pattern.search(content)
        if package_match:
            return package_match.group(1)
        
        # Derive from file path
        relative_path = self._extract_relative_path(file_path, project_root)
        path_parts = Path(relative_path).with_suffix('').parts
        
        # Remove common Kotlin source directories
        filtered_parts = []
        found_src = False
        for part in path_parts:
            if part in ['src', 'main', 'kotlin', 'test']:
                found_src = True
                continue
            if found_src:
                filtered_parts.append(part)
        
        return '.'.join(filtered_parts) if filtered_parts else Path(file_path).stem


class KotlinSourceVisitor:
    """
    Visits Kotlin source code and extracts entities and relationships.
    
    Uses regex-based parsing to identify Kotlin language constructs.
    """
    
    def __init__(self, content: str, module_name: str, file_path: str):
        """
        Initialize the Kotlin source visitor.
        
        Args:
            content: Kotlin source code content
            module_name: Module name for qualified names
            file_path: File path for error reporting
        """
        self.content = content
        self.module_name = module_name
        self.file_path = file_path
        self.entities: List[CodeEntity] = []
        self.relationships: List[CallRelationship] = []
        
        # Track current context for nested entities
        self.current_class = None
        self.current_function = None
        
        # Function definitions for relationship analysis
        self.function_definitions: Dict[str, str] = {}
        
        # Patterns for parsing
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Setup regex patterns for Kotlin parsing."""
        # Class/Object/Interface patterns
        self.class_pattern = re.compile(
            r'(?:^|\n)\s*(?:(?:private|protected|public|internal)\s+)?'
            r'(?:abstract\s+|final\s+|open\s+|sealed\s+)?'
            r'(class|interface|object|enum\s+class|data\s+class|inline\s+class)\s+'
            r'(\w+)',
            re.MULTILINE
        )
        
        # Function patterns
        self.function_pattern = re.compile(
            r'(?:^|\n)\s*(?:(?:private|protected|public|internal)\s+)?'
            r'(?:override\s+|abstract\s+|open\s+|final\s+|inline\s+|suspend\s+)?'
            r'fun\s+(\w+)\s*\(',
            re.MULTILINE
        )
        
        # Property patterns
        self.property_pattern = re.compile(
            r'(?:^|\n)\s*(?:(?:private|protected|public|internal)\s+)?'
            r'(val|var)\s+(\w+)',
            re.MULTILINE
        )
        
        # Function call patterns
        self.function_call_pattern = re.compile(r'(\w+)\s*\(', re.MULTILINE)
        
        # Import and package patterns
        self.package_pattern = re.compile(r'^\s*package\s+([\w.]+)', re.MULTILINE)
        self.import_pattern = re.compile(r'^\s*import\s+([\w.*]+)', re.MULTILINE)
    
    def parse(self) -> Tuple[List[CodeEntity], List[CallRelationship]]:
        """
        Parse the Kotlin content and extract entities and relationships.
        
        Returns:
            Tuple of (entities, relationships)
        """
        # Parse package declaration
        self._parse_package()
        
        # Parse imports
        self._parse_imports()
        
        # Parse classes, objects, interfaces
        self._parse_classes()
        
        # Parse top-level functions
        self._parse_functions()
        
        # Parse properties
        self._parse_properties()
        
        # Parse function call relationships
        self._parse_function_calls()
        
        return self.entities, self.relationships
    
    def _parse_package(self):
        """Parse package declaration."""
        package_match = self.package_pattern.search(self.content)
        if package_match:
            package_name = package_match.group(1)
            entity = CodeEntity(
                name=package_name,
                qualified_name=package_name,
                entity_type="package",
                language="kotlin",
                file_path=self.file_path,
                start_line=self.content[:package_match.start()].count('\n') + 1,
                visibility="public"
            )
            self.entities.append(entity)
    
    def _parse_imports(self):
        """Parse import statements."""
        for import_match in self.import_pattern.finditer(self.content):
            import_name = import_match.group(1)
            entity = CodeEntity(
                name=import_name,
                qualified_name=import_name,
                entity_type="import",
                language="kotlin",
                file_path=self.file_path,
                start_line=self.content[:import_match.start()].count('\n') + 1,
                visibility="public"
            )
            self.entities.append(entity)
    
    def _parse_classes(self):
        """Parse class, object, interface, and enum declarations."""
        for class_match in self.class_pattern.finditer(self.content):
            # Map Kotlin-specific class types to valid entity types
            raw_class_type = class_match.group(1)
            class_type_mapping = {
                "class": "class",
                "interface": "interface", 
                "object": "class",  # Kotlin object as class
                "enum class": "class",  # enum class as class
                "data class": "class",  # data class as class
                "inline class": "class",  # inline class as class
                "sealed class": "class"  # sealed class as class
            }
            class_type = class_type_mapping.get(raw_class_type, "class")
            class_name = class_match.group(2)
            line_number = self.content[:class_match.start()].count('\n') + 1
            
            # Determine visibility
            visibility = self._extract_visibility(class_match.group(0))
            
            # Create qualified name
            qualified_name = f"{self.module_name}.{class_name}" if self.module_name else class_name
            
            entity = CodeEntity(
                name=class_name,
                qualified_name=qualified_name,
                entity_type=class_type,
                language="kotlin",
                file_path=self.file_path,
                start_line=line_number,
                visibility=visibility
            )
            self.entities.append(entity)
            
            # Parse nested members within this class
            self._parse_class_members(class_match, class_name)
    
    def _parse_class_members(self, class_match, class_name: str):
        """Parse members (functions, properties) within a class."""
        # Find the class body (simplified approach)
        class_start = class_match.end()
        class_content = self.content[class_start:]
        
        # Find matching brace (simplified - may not handle all nested cases)
        brace_count = 0
        class_end = len(self.content)
        in_class = False
        
        for i, char in enumerate(class_content):
            if char == '{':
                brace_count += 1
                in_class = True
            elif char == '}' and in_class:
                brace_count -= 1
                if brace_count == 0:
                    class_end = class_start + i
                    break
        
        class_body = self.content[class_start:class_end]
        
        # Parse functions within the class
        for func_match in self.function_pattern.finditer(class_body):
            func_name = func_match.group(1)
            line_number = self.content[:class_start + func_match.start()].count('\n') + 1
            visibility = self._extract_visibility(func_match.group(0))
            
            qualified_name = f"{self.module_name}.{class_name}.{func_name}" if self.module_name else f"{class_name}.{func_name}"
            
            entity = CodeEntity(
                name=func_name,
                qualified_name=qualified_name,
                entity_type="method",
                language="kotlin",
                file_path=self.file_path,
                start_line=line_number,
                visibility=visibility,
                parent_entity=f"{self.module_name}.{class_name}" if self.module_name else class_name
            )
            self.entities.append(entity)
            self.function_definitions[func_name] = qualified_name
        
        # Parse properties within the class
        for prop_match in self.property_pattern.finditer(class_body):
            prop_type = prop_match.group(1)  # val or var
            prop_name = prop_match.group(2)
            line_number = self.content[:class_start + prop_match.start()].count('\n') + 1
            visibility = self._extract_visibility(prop_match.group(0))
            
            qualified_name = f"{self.module_name}.{class_name}.{prop_name}" if self.module_name else f"{class_name}.{prop_name}"
            
            entity = CodeEntity(
                name=prop_name,
                qualified_name=qualified_name,
                entity_type="field",
                language="kotlin",
                file_path=self.file_path,
                start_line=line_number,
                visibility=visibility,
                parent_entity=f"{self.module_name}.{class_name}" if self.module_name else class_name
            )
            self.entities.append(entity)
    
    def _parse_functions(self):
        """Parse top-level function declarations."""
        for func_match in self.function_pattern.finditer(self.content):
            func_name = func_match.group(1)
            line_number = self.content[:func_match.start()].count('\n') + 1
            
            # Skip if this function is already parsed as a class member
            if any(entity.name == func_name and entity.parent_entity for entity in self.entities):
                continue
            
            visibility = self._extract_visibility(func_match.group(0))
            qualified_name = f"{self.module_name}.{func_name}" if self.module_name else func_name
            
            entity = CodeEntity(
                name=func_name,
                qualified_name=qualified_name,
                entity_type="function",
                language="kotlin",
                file_path=self.file_path,
                start_line=line_number,
                visibility=visibility
            )
            self.entities.append(entity)
            self.function_definitions[func_name] = qualified_name
    
    def _parse_properties(self):
        """Parse top-level property declarations."""
        for prop_match in self.property_pattern.finditer(self.content):
            prop_type = prop_match.group(1)  # val or var
            prop_name = prop_match.group(2)
            line_number = self.content[:prop_match.start()].count('\n') + 1
            
            # Skip if this property is already parsed as a class member
            if any(entity.name == prop_name and entity.parent_entity for entity in self.entities):
                continue
            
            visibility = self._extract_visibility(prop_match.group(0))
            qualified_name = f"{self.module_name}.{prop_name}" if self.module_name else prop_name
            
            entity = CodeEntity(
                name=prop_name,
                qualified_name=qualified_name,
                entity_type="variable",
                language="kotlin",
                file_path=self.file_path,
                start_line=line_number,
                visibility=visibility
            )
            self.entities.append(entity)
    
    def _parse_function_calls(self):
        """Parse function call relationships."""
        # Find all function calls
        for call_match in self.function_call_pattern.finditer(self.content):
            called_function = call_match.group(1)
            call_line = self.content[:call_match.start()].count('\n') + 1
            
            # Find the containing function (caller)
            caller_function = self._find_containing_function(call_match.start())
            if not caller_function:
                continue
            
            # Create qualified names
            caller_qualified = self.function_definitions.get(caller_function)
            if not caller_qualified:
                continue
            
            # For callee, check if it's a known function in this file
            callee_qualified = self.function_definitions.get(called_function)
            if not callee_qualified:
                # Create a qualified name assuming it's in the same module
                callee_qualified = f"{self.module_name}.{called_function}" if self.module_name else called_function
            
            relationship = CallRelationship(
                caller=caller_qualified,
                callee=callee_qualified,
                call_type="function_call",
                language="kotlin",
                file_path=self.file_path,
                line_number=call_line
            )
            self.relationships.append(relationship)
    
    def _find_containing_function(self, position: int) -> Optional[str]:
        """Find the function that contains the given position."""
        # Find all function definitions before this position
        functions_before = []
        for func_match in self.function_pattern.finditer(self.content[:position]):
            func_name = func_match.group(1)
            func_start = func_match.start()
            functions_before.append((func_name, func_start))
        
        if not functions_before:
            return None
        
        # Return the latest function before this position
        # (This is a simplified approach - a proper parser would track scope)
        return functions_before[-1][0]
    
    def _extract_visibility(self, declaration: str) -> str:
        """Extract visibility modifier from a declaration."""
        declaration_lower = declaration.lower()
        
        if 'private' in declaration_lower:
            return "private"
        elif 'protected' in declaration_lower:
            return "protected"
        elif 'internal' in declaration_lower:
            return "internal"
        else:
            return "public"  # Default visibility in Kotlin