"""
Dart Parser for TEAM CKG Operations

This parser analyzes Dart source code files and extracts:
- Classes, abstract classes, interfaces, mixins, enums
- Functions, methods, constructors
- Variables and properties
- Function call relationships
- Library declarations and imports

Implementation uses regex-based parsing with Dart language constructs
for robustness and compatibility.
"""

import os
import re
import time
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path

from .base_parser import BaseLanguageParser
from .models import ParseResult, CodeEntity, CallRelationship
from shared.utils.logging_config import (
    log_function_entry,
    log_function_exit,
    log_performance_metric
)


class DartParser(BaseLanguageParser):
    """
    Dart language parser that extracts code entities and relationships.
    
    Uses regex-based parsing with Dart language constructs for robustness
    when dart analyzer or other tools are not available.
    """
    
    def __init__(self):
        """Initialize the Dart parser."""
        super().__init__(language="dart", supported_extensions=[".dart"])
        
        # Dart language patterns for parsing
        self._class_pattern = re.compile(
            r'(?:^|\s)(?:(?:abstract|final|mixin)\s+)?'
            r'(?:class|interface|mixin|enum)\s+'
            r'(\w+)',
            re.MULTILINE
        )
        
        self._function_pattern = re.compile(
            r'(?:^|\s)(?:(?:static|final|const|external|factory)\s+)?'
            r'(?:(?:async|sync)\s+)?'
            r'(?:\w+\s+)*?'  # Return type (optional)
            r'(\w+)\s*\(',
            re.MULTILINE
        )
        
        self._variable_pattern = re.compile(
            r'(?:^|\s)(?:(?:static|final|const|late|var)\s+)?'
            r'(?:(?:\w+)\s+)?'  # Type (optional)
            r'(\w+)\s*[=;]',
            re.MULTILINE
        )
        
        self._function_call_pattern = re.compile(
            r'(\w+)\s*\(',
            re.MULTILINE
        )
        
        self._library_pattern = re.compile(r'^\s*library\s+([\w.]+)', re.MULTILINE)
        self._import_pattern = re.compile(r'^\s*import\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE)
        self._part_pattern = re.compile(r'^\s*part\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE)
        
        # Dart keywords that shouldn't be treated as functions
        self._dart_keywords = {
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw',
            'new', 'const', 'final', 'var', 'dynamic', 'void', 'null', 'true', 'false',
            'class', 'interface', 'mixin', 'enum', 'extends', 'implements', 'with',
            'static', 'abstract', 'override', 'async', 'await', 'sync', 'yield',
            'import', 'export', 'library', 'part', 'show', 'hide', 'as', 'deferred'
        }
        
        self.logger.info("Dart parser initialized with regex-based parsing")
    
    def get_parser_version(self) -> str:
        """Get the version of the Dart parser."""
        return "1.0.0-regex"
    
    def parse_file(self, file_path: str, project_root: str) -> ParseResult:
        """
        Parse a single Dart file and extract code entities and relationships.
        
        Args:
            file_path: Absolute path to the Dart file
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
            language="dart"
        )
        
        try:
            # Read and parse file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract module/library name
            module_name = self._extract_module_name(file_path, project_root, content)
            
            # Parse entities and relationships using Dart visitor
            visitor = DartSourceVisitor(content, module_name, file_path)
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
            
            self.logger.info(f"Successfully parsed Dart file: {file_path}", extra={
                'extra_data': {
                    'file_path': file_path,
                    'entities_found': len(entities),
                    'relationships_found': len(relationships),
                    'module_name': module_name
                }
            })
            
        except FileNotFoundError:
            error_msg = f"Dart file not found: {file_path}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)
            self._stats['files_with_errors'] += 1
            
        except UnicodeDecodeError as e:
            error_msg = f"Encoding error in Dart file {file_path}: {e}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)
            self._stats['files_with_errors'] += 1
            
        except Exception as e:
            error_msg = f"Failed to parse Dart file {file_path}: {e}"
            result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            self._stats['files_with_errors'] += 1
        
        parse_time = time.time() - start_time
        result.parse_duration_ms = parse_time * 1000
        self._stats['total_parse_time_ms'] += result.parse_duration_ms
        
        log_performance_metric(
            self.logger,
            "dart_file_parse_time",
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
        Extract module name from Dart file.
        
        Uses library declaration if available, otherwise derives from file path.
        """
        # Try to extract library declaration
        library_match = self._library_pattern.search(content)
        if library_match:
            return library_match.group(1)
        
        # Derive from file path
        relative_path = self._extract_relative_path(file_path, project_root)
        path_parts = Path(relative_path).with_suffix('').parts
        
        # For Dart, remove lib/src/bin/test prefix and include remaining parts
        filtered_parts = []
        skip_dirs = {'lib', 'src', 'test', 'bin'}
        
        # Start including parts after we find a source directory
        include_parts = False
        for part in path_parts:
            if part in skip_dirs:
                include_parts = True
                continue
            if include_parts:
                filtered_parts.append(part)
        
        # If no source directory found, include all parts except the first few common directories
        if not filtered_parts:
            filtered_parts = [p for p in path_parts if p not in skip_dirs]
        
        return '.'.join(filtered_parts) if filtered_parts else Path(file_path).stem


class DartSourceVisitor:
    """
    Visits Dart source code and extracts entities and relationships.
    
    Uses regex-based parsing to identify Dart language constructs.
    """
    
    def __init__(self, content: str, module_name: str, file_path: str):
        """
        Initialize the Dart source visitor.
        
        Args:
            content: Dart source code content
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
        
        # Dart keywords that shouldn't be treated as functions
        self._dart_keywords = {
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw',
            'new', 'const', 'final', 'var', 'dynamic', 'void', 'null', 'true', 'false',
            'class', 'interface', 'mixin', 'enum', 'extends', 'implements', 'with',
            'static', 'abstract', 'override', 'async', 'await', 'sync', 'yield',
            'import', 'export', 'library', 'part', 'show', 'hide', 'as', 'deferred'
        }
        
        # Patterns for parsing
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Setup regex patterns for Dart parsing."""
        # Class/Interface/Mixin/Enum patterns
        self.class_pattern = re.compile(
            r'(?:^|\n)\s*(?:abstract\s+|final\s+|mixin\s+)?'
            r'(class|interface|mixin|enum)\s+'
            r'(\w+)',
            re.MULTILINE
        )
        
        # Function patterns (including getters/setters)
        self.function_pattern = re.compile(
            r'(?:^|\n)\s*(?:static\s+|final\s+|const\s+|external\s+|factory\s+)?'
            r'(?:(?:async|sync)\s+)?'
            r'(?:(?:\w+)\s+)?'  # Return type (optional)
            r'(?:get\s+|set\s+)?'  # Getter/setter
            r'(\w+)\s*\(',
            re.MULTILINE
        )
        
        # Variable/Property patterns
        self.variable_pattern = re.compile(
            r'(?:^|\n)\s*(?:static\s+|final\s+|const\s+|late\s+|var\s+)?'
            r'(?:(?:\w+)\s+)?'  # Type (optional)
            r'(\w+)\s*[=;]',
            re.MULTILINE
        )
        
        # Function call patterns
        self.function_call_pattern = re.compile(r'(\w+)\s*\(', re.MULTILINE)
        
        # Import/Library patterns
        self.library_pattern = re.compile(r'^\s*library\s+([\w.]+)', re.MULTILINE)
        self.import_pattern = re.compile(r'^\s*import\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE)
        self.part_pattern = re.compile(r'^\s*part\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE)
    
    def parse(self) -> Tuple[List[CodeEntity], List[CallRelationship]]:
        """
        Parse the Dart content and extract entities and relationships.
        
        Returns:
            Tuple of (entities, relationships)
        """
        # Parse library declaration
        self._parse_library()
        
        # Parse imports
        self._parse_imports()
        
        # Parse part declarations
        self._parse_parts()
        
        # Parse classes, interfaces, mixins, enums
        self._parse_classes()
        
        # Parse top-level functions
        self._parse_functions()
        
        # Parse top-level variables
        self._parse_variables()
        
        # Parse function call relationships
        self._parse_function_calls()
        
        return self.entities, self.relationships
    
    def _parse_library(self):
        """Parse library declaration."""
        library_match = self.library_pattern.search(self.content)
        if library_match:
            library_name = library_match.group(1)
            # Use "module" entity type instead of "library"
            entity = CodeEntity(
                name=library_name,
                qualified_name=library_name,
                entity_type="module",
                language="dart",
                file_path=self.file_path,
                start_line=self.content[:library_match.start()].count('\n') + 1,
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
                language="dart",
                file_path=self.file_path,
                start_line=self.content[:import_match.start()].count('\n') + 1,
                visibility="public"
            )
            self.entities.append(entity)
    
    def _parse_parts(self):
        """Parse part declarations."""
        for part_match in self.part_pattern.finditer(self.content):
            part_name = part_match.group(1)
            # Use "import" entity type for part declarations
            entity = CodeEntity(
                name=part_name,
                qualified_name=part_name,
                entity_type="import",
                language="dart",
                file_path=self.file_path,
                start_line=self.content[:part_match.start()].count('\n') + 1,
                visibility="public"
            )
            self.entities.append(entity)
    
    def _parse_classes(self):
        """Parse class, interface, mixin, and enum declarations."""
        for class_match in self.class_pattern.finditer(self.content):
            class_type = class_match.group(1)
            class_name = class_match.group(2)
            line_number = self.content[:class_match.start()].count('\n') + 1
            
            # Determine visibility (Dart uses _ prefix for private)
            visibility = "private" if class_name.startswith('_') else "public"
            
            # Create qualified name
            qualified_name = f"{self.module_name}.{class_name}" if self.module_name else class_name
            
            # Map Dart-specific types to valid entity types
            entity_type_mapping = {
                "class": "class",
                "abstract": "class",  # abstract class
                "mixin": "interface",  # treat mixin as interface
                "enum": "class",  # treat enum as class
                "interface": "interface"
            }
            mapped_entity_type = entity_type_mapping.get(class_type, "class")
            
            entity = CodeEntity(
                name=class_name,
                qualified_name=qualified_name,
                entity_type=mapped_entity_type,
                language="dart",
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
        
        # Parse functions/methods within the class
        for func_match in self.function_pattern.finditer(class_body):
            func_name = func_match.group(1)
            
            # Skip Dart keywords
            if func_name.lower() in self._dart_keywords:
                continue
            
            line_number = self.content[:class_start + func_match.start()].count('\n') + 1
            visibility = "private" if func_name.startswith('_') else "public"
            
            qualified_name = f"{self.module_name}.{class_name}.{func_name}" if self.module_name else f"{class_name}.{func_name}"
            
            entity = CodeEntity(
                name=func_name,
                qualified_name=qualified_name,
                entity_type="method",
                language="dart",
                file_path=self.file_path,
                start_line=line_number,
                visibility=visibility,
                parent_entity=f"{self.module_name}.{class_name}" if self.module_name else class_name
            )
            self.entities.append(entity)
            self.function_definitions[func_name] = qualified_name
        
        # Parse variables/properties within the class
        for var_match in self.variable_pattern.finditer(class_body):
            var_name = var_match.group(1)
            line_number = self.content[:class_start + var_match.start()].count('\n') + 1
            visibility = "private" if var_name.startswith('_') else "public"
            
            qualified_name = f"{self.module_name}.{class_name}.{var_name}" if self.module_name else f"{class_name}.{var_name}"
            
            entity = CodeEntity(
                name=var_name,
                qualified_name=qualified_name,
                entity_type="field",  # Use "field" instead of "property"
                language="dart",
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
            
            # Skip Dart keywords
            if func_name.lower() in self._dart_keywords:
                continue
            
            line_number = self.content[:func_match.start()].count('\n') + 1
            
            # Skip if this function is already parsed as a class member
            if any(entity.name == func_name and entity.parent_entity for entity in self.entities):
                continue
            
            visibility = "private" if func_name.startswith('_') else "public"
            qualified_name = f"{self.module_name}.{func_name}" if self.module_name else func_name
            
            entity = CodeEntity(
                name=func_name,
                qualified_name=qualified_name,
                entity_type="function",
                language="dart",
                file_path=self.file_path,
                start_line=line_number,
                visibility=visibility
            )
            self.entities.append(entity)
            self.function_definitions[func_name] = qualified_name
    
    def _parse_variables(self):
        """Parse top-level variable declarations."""
        for var_match in self.variable_pattern.finditer(self.content):
            var_name = var_match.group(1)
            line_number = self.content[:var_match.start()].count('\n') + 1
            
            # Skip if this variable is already parsed as a class member
            if any(entity.name == var_name and entity.parent_entity for entity in self.entities):
                continue
            
            # Skip Dart keywords and common patterns that aren't variables
            if var_name.lower() in self._dart_keywords or var_name in ['main', 'runApp']:
                continue
            
            visibility = "private" if var_name.startswith('_') else "public"
            qualified_name = f"{self.module_name}.{var_name}" if self.module_name else var_name
            
            entity = CodeEntity(
                name=var_name,
                qualified_name=qualified_name,
                entity_type="variable",
                language="dart",
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
            
            # Skip Dart keywords
            if called_function.lower() in self._dart_keywords:
                continue
            
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
                language="dart",
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
            # Skip Dart keywords
            if func_name.lower() in self._dart_keywords:
                continue
            func_start = func_match.start()
            functions_before.append((func_name, func_start))
        
        if not functions_before:
            return None
        
        # Return the latest function before this position
        # (This is a simplified approach - a proper parser would track scope)
        return functions_before[-1][0]