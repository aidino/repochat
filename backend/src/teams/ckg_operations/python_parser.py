"""
Python Language Parser for TEAM CKG Operations

Implements Python-specific code parsing using the built-in ast module.
Extracts classes, functions, methods, and call relationships from Python source files.

Enhanced for Task 2.4 (F2.4) requirements:
- Parse Python files using ast module
- Extract function names, class names, method names in class
- Extract direct function/method calls within the same file
- Return structured data using existing models
"""

import ast
import os
import time
from typing import List, Optional, Dict, Any, Set, Union
from pathlib import Path

from .base_parser import BaseLanguageParser
from .models import (
    ParseResult, 
    CodeEntity, 
    CallRelationship, 
    CodeEntityType, 
    VisibilityModifier
)


class PythonParser(BaseLanguageParser):
    """
    Python language parser using built-in ast module.
    
    Implements the BaseLanguageParser interface to provide Python-specific
    code analysis functionality for the CodeParserCoordinatorModule.
    """
    
    def __init__(self):
        """Initialize the Python parser."""
        super().__init__("python", [".py"])
        
        # Python-specific parsing statistics
        self._python_stats = {
            'classes_found': 0,
            'functions_found': 0,
            'methods_found': 0,
            'async_functions_found': 0,
            'variables_found': 0,
            'function_calls_found': 0,
            'parse_errors': 0
        }
        
        self.logger.info("Python parser initialized with ast module")
    
    def parse_file(self, file_path: str, project_root: str) -> ParseResult:
        """
        Parse a single Python source file.
        
        Args:
            file_path: Absolute path to the Python source file
            project_root: Absolute path to the project root directory
            
        Returns:
            ParseResult containing entities and relationships found in the file
        """
        start_time = time.time()
        
        # Extract relative path
        relative_path = self._extract_relative_path(file_path, project_root)
        
        # Initialize result
        result = ParseResult(
            file_path=relative_path,
            language=self.language
        )
        
        try:
            # Read Python source file
            if not os.path.exists(file_path):
                result.errors.append(f"File not found: {file_path}")
                return result
            
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            if not source_code.strip():
                result.warnings.append(f"Empty file: {relative_path}")
                return result
            
            # Parse Python source using ast
            try:
                tree = ast.parse(source_code, filename=file_path)
            except SyntaxError as e:
                error_msg = f"Python syntax error in {relative_path}: {str(e)} at line {e.lineno}"
                result.errors.append(error_msg)
                self.logger.error(error_msg)
                self._python_stats['parse_errors'] += 1
                return result
            except Exception as e:
                error_msg = f"Failed to parse Python file {relative_path}: {str(e)}"
                result.errors.append(error_msg)
                self.logger.error(error_msg)
                self._python_stats['parse_errors'] += 1
                return result
            
            # Extract module name from file path
            module_name = self._extract_module_name(relative_path)
            
            # Extract entities and relationships
            entities, relationships = self._extract_entities_and_relationships(
                tree, relative_path, module_name
            )
            
            result.entities = entities
            result.relationships = relationships
            
            # Add metadata
            result.metadata = {
                'module_name': module_name,
                'file_size_bytes': len(source_code),
                'ast_parser': True,
                'line_count': len(source_code.splitlines())
            }
            
            self.logger.debug(
                f"Python parsed {relative_path}: {len(entities)} entities, {len(relationships)} relationships"
            )
            
        except Exception as e:
            error_msg = f"Unexpected error parsing {relative_path}: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            self._python_stats['parse_errors'] += 1
        
        # Record timing
        result.parse_duration_ms = (time.time() - start_time) * 1000
        
        return result
    
    def get_parser_version(self) -> str:
        """Get the version of the ast parser (Python version)."""
        import sys
        return f"ast-python-{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _extract_module_name(self, file_path: str) -> str:
        """
        Extract module name from file path.
        
        Args:
            file_path: Relative path to the Python file
            
        Returns:
            Module name (e.g., "package.module")
        """
        # Convert file path to module name
        # e.g., "src/package/module.py" -> "src.package.module"
        path_obj = Path(file_path)
        parts = list(path_obj.with_suffix('').parts)
        return '.'.join(parts)
    
    def _extract_entities_and_relationships(
        self, 
        tree: ast.AST, 
        file_path: str, 
        module_name: str
    ) -> tuple[List[CodeEntity], List[CallRelationship]]:
        """
        Extract code entities and relationships from the parsed Python AST.
        
        Args:
            tree: Parsed Python AST
            file_path: Relative path to the source file
            module_name: Python module name
            
        Returns:
            Tuple of (entities, relationships)
        """
        entities = []
        relationships = []
        
        # Track function calls for relationship extraction
        all_function_calls = []
        
        # Use AST visitor to extract entities
        visitor = PythonASTVisitor(file_path, module_name, self._python_stats)
        visitor.visit(tree)
        
        entities = visitor.entities
        all_function_calls = visitor.function_calls
        
        # Create call relationships
        relationships = self._create_call_relationships(
            all_function_calls, entities, file_path
        )
        
        return entities, relationships
    
    def _create_call_relationships(
        self, 
        function_calls: List[Dict[str, Any]], 
        entities: List[CodeEntity], 
        file_path: str
    ) -> List[CallRelationship]:
        """
        Create call relationships from extracted function calls.
        
        Args:
            function_calls: List of function call information
            entities: List of extracted entities
            file_path: File path for context
            
        Returns:
            List of CallRelationship objects
        """
        relationships = []
        
        # Create mapping of entity names to entities for quick lookup
        entity_map = {}
        for entity in entities:
            entity_map[entity.qualified_name] = entity
            if entity.name:
                entity_map[entity.name] = entity
        
        for call_info in function_calls:
            caller_name = call_info.get('caller')
            callee_name = call_info.get('callee')
            
            if not caller_name or not callee_name:
                continue
            
            # Try to find caller and callee entities
            caller_entity = entity_map.get(caller_name)
            callee_entity = entity_map.get(callee_name)
            
            # Only create relationship if both entities exist in the same file
            if caller_entity and callee_entity:
                relationship = CallRelationship(
                    caller=caller_entity.qualified_name,
                    callee=callee_entity.qualified_name,
                    file_path=file_path,
                    language="python",
                    line_number=call_info.get('line_number', 0)
                )
                relationships.append(relationship)
                self._python_stats['function_calls_found'] += 1
        
        return relationships
    
    def get_python_stats(self) -> Dict[str, Any]:
        """Get Python-specific parsing statistics."""
        return {
            **self.get_stats(),
            'python_specific': self._python_stats
        }


class PythonASTVisitor(ast.NodeVisitor):
    """
    AST visitor to extract entities and function calls from Python code.
    """
    
    def __init__(self, file_path: str, module_name: str, stats: Dict[str, int]):
        self.file_path = file_path
        self.module_name = module_name
        self.stats = stats
        
        self.entities: List[CodeEntity] = []
        self.function_calls: List[Dict[str, Any]] = []
        
        # Stack to track current context (class/function)
        self.context_stack: List[str] = []
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        class_name = node.name
        qualified_name = self._create_qualified_name(class_name)
        
        # Create class entity
        entity = CodeEntity(
            name=class_name,
            qualified_name=qualified_name,
            entity_type=CodeEntityType.CLASS,
            file_path=self.file_path,
            language="python",
            start_line=node.lineno,
            visibility=self._extract_visibility(class_name),
            metadata={
                'base_classes': [self._extract_base_name(base) for base in node.bases],
                'decorators': [self._extract_decorator_name(dec) for dec in node.decorator_list],
                'docstring': ast.get_docstring(node),
                'is_abstract': self._is_abstract_class(node)
            }
        )
        
        self.entities.append(entity)
        self.stats['classes_found'] += 1
        
        # Add class to context stack
        self.context_stack.append(class_name)
        
        # Visit class methods and attributes
        self.generic_visit(node)
        
        # Remove class from context stack
        self.context_stack.pop()
    
    def visit_FunctionDef(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> None:
        """Visit function definition (regular or async)."""
        function_name = node.name
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        # Determine if this is a method (inside a class) or standalone function
        if self.context_stack and self.context_stack[-1]:
            # This is a method
            entity_type = CodeEntityType.METHOD
            qualified_name = self._create_qualified_name(function_name)
            self.stats['methods_found'] += 1
        else:
            # This is a standalone function
            entity_type = CodeEntityType.FUNCTION
            qualified_name = self._create_qualified_name(function_name)
            self.stats['functions_found'] += 1
        
        if is_async:
            self.stats['async_functions_found'] += 1
        
        # Extract function parameters
        args = []
        if node.args:
            for arg in node.args.args:
                args.append(arg.arg)
        
        # Create function/method entity
        entity = CodeEntity(
            name=function_name,
            qualified_name=qualified_name,
            entity_type=entity_type,
            file_path=self.file_path,
            language="python",
            start_line=node.lineno,
            visibility=self._extract_visibility(function_name),
            metadata={
                'parameters': args,
                'is_async': is_async,
                'decorators': [self._extract_decorator_name(dec) for dec in node.decorator_list],
                'docstring': ast.get_docstring(node),
                'return_annotation': self._extract_annotation(getattr(node, 'returns', None))
            }
        )
        
        self.entities.append(entity)
        
        # Add function to context stack
        self.context_stack.append(function_name)
        
        # Visit function body to find function calls
        for stmt in node.body:
            self.visit(stmt)
        
        # Remove function from context stack
        self.context_stack.pop()
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        self.visit_FunctionDef(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function call."""
        # Extract caller (current function/method) - use direct qualified name creation
        if self.context_stack:
            caller_qualified_name = f"{self.module_name}.{'.'.join(self.context_stack)}"
        else:
            caller_qualified_name = self.module_name
        
        # Extract callee (function being called)
        callee = self._extract_call_name(node.func)
        
        if callee and caller_qualified_name:
            # Try to create qualified name for callee if it's a simple name
            if '.' not in callee:
                # Simple function name, assume it's in the same module
                qualified_callee = f"{self.module_name}.{callee}"
            else:
                qualified_callee = callee
                
            call_info = {
                'caller': caller_qualified_name,
                'callee': qualified_callee,
                'line_number': node.lineno
            }
            self.function_calls.append(call_info)

        
        # Continue visiting child nodes
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit variable assignment."""
        # Extract simple variable assignments
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                qualified_name = self._create_qualified_name(var_name)
                
                # Create variable entity
                entity = CodeEntity(
                    name=var_name,
                    qualified_name=qualified_name,
                    entity_type=CodeEntityType.FIELD,  # Use FIELD for variables
                    file_path=self.file_path,
                    language="python",
                    start_line=node.lineno,
                    visibility=self._extract_visibility(var_name),
                    metadata={
                        'is_global': len(self.context_stack) == 0,
                        'value_type': self._extract_value_type(node.value)
                    }
                )
                
                self.entities.append(entity)
                self.stats['variables_found'] += 1
        
        # Continue visiting child nodes
        self.generic_visit(node)
    
    def _create_qualified_name(self, name: str) -> str:
        """Create qualified name based on current context."""
        if self.context_stack:
            full_context = '.'.join([self.module_name] + self.context_stack + [name])
        else:
            full_context = f"{self.module_name}.{name}"
        return full_context
    
    def _extract_visibility(self, name: str) -> VisibilityModifier:
        """Extract visibility modifier from name conventions."""
        if name.startswith('__') and name.endswith('__'):
            return VisibilityModifier.PUBLIC  # Magic methods are public
        elif name.startswith('__'):
            return VisibilityModifier.PRIVATE  # Double underscore = private
        elif name.startswith('_'):
            return VisibilityModifier.PROTECTED  # Single underscore = protected
        else:
            return VisibilityModifier.PUBLIC  # Default is public
    
    def _extract_call_name(self, func_node: ast.AST) -> Optional[str]:
        """Extract function/method name from call node."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            # Handle method calls like obj.method()
            if isinstance(func_node.value, ast.Name):
                return f"{func_node.value.id}.{func_node.attr}"
            else:
                return func_node.attr
        elif isinstance(func_node, ast.Call):
            # Handle chained calls
            return self._extract_call_name(func_node.func)
        else:
            return None
    
    def _extract_base_name(self, base_node: ast.AST) -> str:
        """Extract base class name."""
        if isinstance(base_node, ast.Name):
            return base_node.id
        elif isinstance(base_node, ast.Attribute):
            return f"{self._extract_call_name(base_node.value)}.{base_node.attr}"
        else:
            return str(base_node)
    
    def _extract_decorator_name(self, decorator_node: ast.AST) -> str:
        """Extract decorator name."""
        if isinstance(decorator_node, ast.Name):
            return decorator_node.id
        elif isinstance(decorator_node, ast.Attribute):
            return f"{self._extract_call_name(decorator_node.value)}.{decorator_node.attr}"
        else:
            return str(decorator_node)
    
    def _extract_annotation(self, annotation_node: Optional[ast.AST]) -> Optional[str]:
        """Extract type annotation."""
        if annotation_node is None:
            return None
        if isinstance(annotation_node, ast.Name):
            return annotation_node.id
        elif isinstance(annotation_node, ast.Constant):
            return str(annotation_node.value)
        else:
            return str(annotation_node)
    
    def _extract_value_type(self, value_node: ast.AST) -> str:
        """Extract value type from assignment."""
        if isinstance(value_node, ast.Constant):
            return type(value_node.value).__name__
        elif isinstance(value_node, ast.Name):
            return value_node.id
        elif isinstance(value_node, ast.Call):
            call_name = self._extract_call_name(value_node.func)
            return call_name or "unknown"
        else:
            return "unknown"
    
    def _is_abstract_class(self, class_node: ast.ClassDef) -> bool:
        """Check if class is abstract."""
        # Simple heuristic: check if ABC is in base classes
        for base in class_node.bases:
            base_name = self._extract_base_name(base)
            if 'ABC' in base_name or 'Abstract' in base_name:
                return True
        return False
