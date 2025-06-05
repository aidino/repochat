"""
Java Language Parser for TEAM CKG Operations

Implements Java-specific code parsing using the javalang library.
Extracts classes, methods, and call relationships from Java source files.

Enhanced for Task 2.3 (F2.3) requirements:
- Parse Java files using javalang
- Extract class names and method names
- Extract direct method calls within the same file/class
- Return structured data using existing models
"""

import os
import time
from typing import List, Optional, Dict, Any, Set
from pathlib import Path

try:
    import javalang
    JAVALANG_AVAILABLE = True
except ImportError:
    JAVALANG_AVAILABLE = False
    import warnings
    warnings.warn("javalang library not available. Java parsing will be disabled.")

from .base_parser import BaseLanguageParser
from .models import (
    ParseResult, 
    CodeEntity, 
    CallRelationship, 
    CodeEntityType, 
    VisibilityModifier
)


class JavaParser(BaseLanguageParser):
    """
    Java language parser using javalang library.
    
    Implements the BaseLanguageParser interface to provide Java-specific
    code analysis functionality for the CodeParserCoordinatorModule.
    """
    
    def __init__(self):
        """Initialize the Java parser."""
        super().__init__("java", [".java"])
        
        if not JAVALANG_AVAILABLE:
            self.logger.error("javalang library not available. Java parsing is disabled.")
            raise ImportError("javalang library is required for Java parsing")
        
        # Java-specific parsing statistics
        self._java_stats = {
            'classes_found': 0,
            'methods_found': 0,
            'interfaces_found': 0,
            'constructors_found': 0,
            'fields_found': 0,
            'method_calls_found': 0,
            'parse_errors': 0
        }
        
        self.logger.info("Java parser initialized with javalang")
    
    def parse_file(self, file_path: str, project_root: str) -> ParseResult:
        """
        Parse a single Java source file.
        
        Args:
            file_path: Absolute path to the Java source file
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
            # Read Java source file
            if not os.path.exists(file_path):
                result.errors.append(f"File not found: {file_path}")
                return result
            
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            if not source_code.strip():
                result.warnings.append(f"Empty file: {relative_path}")
                return result
            
            # Parse Java source using javalang
            try:
                tree = javalang.parse.parse(source_code)
            except javalang.parser.JavaSyntaxError as e:
                error_msg = f"Java syntax error in {relative_path}: {str(e)}"
                result.errors.append(error_msg)
                self.logger.error(error_msg)
                self._java_stats['parse_errors'] += 1
                return result
            except Exception as e:
                error_msg = f"Failed to parse Java file {relative_path}: {str(e)}"
                result.errors.append(error_msg)
                self.logger.error(error_msg)
                self._java_stats['parse_errors'] += 1
                return result
            
            # Extract package information
            package_name = None
            if tree.package:
                package_name = tree.package.name
            
            # Extract entities and relationships
            entities, relationships = self._extract_entities_and_relationships(
                tree, relative_path, package_name
            )
            
            result.entities = entities
            result.relationships = relationships
            
            # Add metadata
            result.metadata = {
                'package_name': package_name,
                'import_count': len(tree.imports) if tree.imports else 0,
                'file_size_bytes': len(source_code),
                'javalang_parser': True
            }
            
            self.logger.debug(
                f"Java parsed {relative_path}: {len(entities)} entities, {len(relationships)} relationships"
            )
            
        except Exception as e:
            error_msg = f"Unexpected error parsing {relative_path}: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            self._java_stats['parse_errors'] += 1
        
        # Record timing
        result.parse_duration_ms = (time.time() - start_time) * 1000
        
        return result
    
    def get_parser_version(self) -> str:
        """Get the version of the javalang parser."""
        if JAVALANG_AVAILABLE:
            try:
                return f"javalang-{javalang.__version__}"
            except AttributeError:
                return "javalang-unknown"
        return "javalang-unavailable"
    
    def _extract_entities_and_relationships(
        self, 
        tree: javalang.tree.CompilationUnit, 
        file_path: str, 
        package_name: Optional[str]
    ) -> tuple[List[CodeEntity], List[CallRelationship]]:
        """
        Extract code entities and relationships from the parsed Java AST.
        
        Args:
            tree: Parsed Java AST from javalang
            file_path: Relative path to the source file
            package_name: Java package name
            
        Returns:
            Tuple of (entities, relationships)
        """
        entities = []
        relationships = []
        
        # Track method calls for relationship extraction
        all_method_calls = []
        
        # Process all type declarations (classes, interfaces, enums)
        if tree.types:
            for type_decl in tree.types:
                if isinstance(type_decl, javalang.tree.ClassDeclaration):
                    class_entities, class_calls = self._extract_class_entities(
                        type_decl, file_path, package_name
                    )
                    entities.extend(class_entities)
                    all_method_calls.extend(class_calls)
                    
                elif isinstance(type_decl, javalang.tree.InterfaceDeclaration):
                    interface_entities, interface_calls = self._extract_interface_entities(
                        type_decl, file_path, package_name
                    )
                    entities.extend(interface_entities)
                    all_method_calls.extend(interface_calls)
                    
                elif isinstance(type_decl, javalang.tree.EnumDeclaration):
                    enum_entities, enum_calls = self._extract_enum_entities(
                        type_decl, file_path, package_name
                    )
                    entities.extend(enum_entities)
                    all_method_calls.extend(enum_calls)
        
        # Create relationships from method calls
        relationships = self._create_call_relationships(
            all_method_calls, entities, file_path
        )
        
        return entities, relationships
    
    def _extract_class_entities(
        self, 
        class_decl: javalang.tree.ClassDeclaration, 
        file_path: str, 
        package_name: Optional[str]
    ) -> tuple[List[CodeEntity], List[Dict[str, Any]]]:
        """Extract entities from a Java class declaration."""
        entities = []
        method_calls = []
        
        # Create class entity
        class_qualified_name = self._create_qualified_name(
            class_decl.name, package_name=package_name
        )
        
        class_entity = CodeEntity(
            entity_type=CodeEntityType.CLASS,
            name=class_decl.name,
            qualified_name=class_qualified_name,
            file_path=file_path,
            visibility=self._extract_visibility(class_decl.modifiers),
            modifiers=self._extract_modifiers(class_decl.modifiers),
            language=self.language,
            metadata={
                'extends': class_decl.extends.name if class_decl.extends else None,
                'implements': [impl.name for impl in class_decl.implements] if class_decl.implements else [],
                'is_abstract': 'abstract' in (class_decl.modifiers or []),
                'is_final': 'final' in (class_decl.modifiers or [])
            }
        )
        entities.append(class_entity)
        self._java_stats['classes_found'] += 1
        
        # Process class body
        if class_decl.body:
            for member in class_decl.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_entity, calls = self._extract_method_entity(
                        member, file_path, package_name, class_decl.name
                    )
                    entities.append(method_entity)
                    method_calls.extend(calls)
                    
                elif isinstance(member, javalang.tree.ConstructorDeclaration):
                    constructor_entity, calls = self._extract_constructor_entity(
                        member, file_path, package_name, class_decl.name
                    )
                    entities.append(constructor_entity)
                    method_calls.extend(calls)
                    
                elif isinstance(member, javalang.tree.FieldDeclaration):
                    field_entities = self._extract_field_entities(
                        member, file_path, package_name, class_decl.name
                    )
                    entities.extend(field_entities)
        
        return entities, method_calls
    
    def _extract_interface_entities(
        self, 
        interface_decl: javalang.tree.InterfaceDeclaration, 
        file_path: str, 
        package_name: Optional[str]
    ) -> tuple[List[CodeEntity], List[Dict[str, Any]]]:
        """Extract entities from a Java interface declaration."""
        entities = []
        method_calls = []
        
        # Create interface entity
        interface_qualified_name = self._create_qualified_name(
            interface_decl.name, package_name=package_name
        )
        
        interface_entity = CodeEntity(
            entity_type=CodeEntityType.INTERFACE,
            name=interface_decl.name,
            qualified_name=interface_qualified_name,
            file_path=file_path,
            visibility=self._extract_visibility(interface_decl.modifiers),
            modifiers=self._extract_modifiers(interface_decl.modifiers),
            language=self.language,
            metadata={
                'extends': [ext.name for ext in interface_decl.extends] if interface_decl.extends else []
            }
        )
        entities.append(interface_entity)
        self._java_stats['interfaces_found'] += 1
        
        # Process interface methods
        if interface_decl.body:
            for member in interface_decl.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_entity, calls = self._extract_method_entity(
                        member, file_path, package_name, interface_decl.name
                    )
                    entities.append(method_entity)
                    method_calls.extend(calls)
        
        return entities, method_calls
    
    def _extract_enum_entities(
        self, 
        enum_decl: javalang.tree.EnumDeclaration, 
        file_path: str, 
        package_name: Optional[str]
    ) -> tuple[List[CodeEntity], List[Dict[str, Any]]]:
        """Extract entities from a Java enum declaration."""
        entities = []
        method_calls = []
        
        # Create enum entity (treated as a special class)
        enum_qualified_name = self._create_qualified_name(
            enum_decl.name, package_name=package_name
        )
        
        enum_entity = CodeEntity(
            entity_type=CodeEntityType.CLASS,  # Enum is a special class
            name=enum_decl.name,
            qualified_name=enum_qualified_name,
            file_path=file_path,
            visibility=self._extract_visibility(enum_decl.modifiers),
            modifiers=self._extract_modifiers(enum_decl.modifiers) + ['enum'],
            language=self.language,
            metadata={
                'is_enum': True,
                'enum_constants': [const.name for const in enum_decl.body.constants] if enum_decl.body and enum_decl.body.constants else []
            }
        )
        entities.append(enum_entity)
        self._java_stats['classes_found'] += 1  # Count as class
        
        return entities, method_calls
    
    def _extract_method_entity(
        self, 
        method_decl: javalang.tree.MethodDeclaration, 
        file_path: str, 
        package_name: Optional[str], 
        class_name: str
    ) -> tuple[CodeEntity, List[Dict[str, Any]]]:
        """Extract a method entity and its calls."""
        
        # Create method qualified name
        method_qualified_name = self._create_qualified_name(
            method_decl.name, parent_name=class_name, package_name=package_name
        )
        
        # Extract parameters
        parameters = []
        if method_decl.parameters:
            for param in method_decl.parameters:
                param_type = self._extract_type_name(param.type)
                parameters.append({
                    'name': param.name,
                    'type': param_type
                })
        
        # Create method signature
        param_types = [p['type'] for p in parameters]
        signature = f"{method_decl.name}({', '.join(param_types)})"
        
        # Extract return type
        return_type = None
        if method_decl.return_type:
            return_type = self._extract_type_name(method_decl.return_type)
        
        method_entity = CodeEntity(
            entity_type=CodeEntityType.METHOD,
            name=method_decl.name,
            qualified_name=method_qualified_name,
            file_path=file_path,
            visibility=self._extract_visibility(method_decl.modifiers),
            parent_entity=class_name,
            signature=signature,
            return_type=return_type,
            parameters=parameters,
            modifiers=self._extract_modifiers(method_decl.modifiers),
            language=self.language,
            metadata={
                'is_static': 'static' in (method_decl.modifiers or []),
                'is_abstract': 'abstract' in (method_decl.modifiers or []),
                'is_final': 'final' in (method_decl.modifiers or [])
            }
        )
        self._java_stats['methods_found'] += 1
        
        # Extract method calls from method body
        method_calls = []
        if method_decl.body:
            calls = self._extract_method_calls_from_statements(
                method_decl.body, method_qualified_name
            )
            method_calls.extend(calls)
        
        return method_entity, method_calls
    
    def _extract_constructor_entity(
        self, 
        constructor_decl: javalang.tree.ConstructorDeclaration, 
        file_path: str, 
        package_name: Optional[str], 
        class_name: str
    ) -> tuple[CodeEntity, List[Dict[str, Any]]]:
        """Extract a constructor entity and its calls."""
        
        constructor_qualified_name = self._create_qualified_name(
            class_name, parent_name=class_name, package_name=package_name
        )
        
        # Extract parameters
        parameters = []
        if constructor_decl.parameters:
            for param in constructor_decl.parameters:
                param_type = self._extract_type_name(param.type)
                parameters.append({
                    'name': param.name,
                    'type': param_type
                })
        
        # Create constructor signature
        param_types = [p['type'] for p in parameters]
        signature = f"{class_name}({', '.join(param_types)})"
        
        constructor_entity = CodeEntity(
            entity_type=CodeEntityType.CONSTRUCTOR,
            name=class_name,  # Constructor name is class name
            qualified_name=constructor_qualified_name,
            file_path=file_path,
            visibility=self._extract_visibility(constructor_decl.modifiers),
            parent_entity=class_name,
            signature=signature,
            parameters=parameters,
            modifiers=self._extract_modifiers(constructor_decl.modifiers),
            language=self.language,
            metadata={'is_constructor': True}
        )
        self._java_stats['constructors_found'] += 1
        
        # Extract method calls from constructor body
        method_calls = []
        if constructor_decl.body:
            calls = self._extract_method_calls_from_statements(
                constructor_decl.body, constructor_qualified_name
            )
            method_calls.extend(calls)
        
        return constructor_entity, method_calls
    
    def _extract_field_entities(
        self, 
        field_decl: javalang.tree.FieldDeclaration, 
        file_path: str, 
        package_name: Optional[str], 
        class_name: str
    ) -> List[CodeEntity]:
        """Extract field entities from a field declaration."""
        entities = []
        
        field_type = self._extract_type_name(field_decl.type)
        
        for declarator in field_decl.declarators:
            field_qualified_name = self._create_qualified_name(
                declarator.name, parent_name=class_name, package_name=package_name
            )
            
            field_entity = CodeEntity(
                entity_type=CodeEntityType.FIELD,
                name=declarator.name,
                qualified_name=field_qualified_name,
                file_path=file_path,
                visibility=self._extract_visibility(field_decl.modifiers),
                parent_entity=class_name,
                return_type=field_type,
                modifiers=self._extract_modifiers(field_decl.modifiers),
                language=self.language,
                metadata={
                    'field_type': field_type,
                    'is_static': 'static' in (field_decl.modifiers or []),
                    'is_final': 'final' in (field_decl.modifiers or [])
                }
            )
            entities.append(field_entity)
            self._java_stats['fields_found'] += 1
        
        return entities
    
    def _extract_method_calls_from_statements(
        self, 
        statements: List[javalang.tree.Statement], 
        caller_qualified_name: str
    ) -> List[Dict[str, Any]]:
        """Extract method calls from a list of statements recursively."""
        method_calls = []
        
        # Walk through each statement and find method invocations
        for statement in statements:
            self._extract_method_calls_from_node_recursive(
                statement, caller_qualified_name, method_calls
            )
        
        return method_calls
    
    def _extract_method_calls_from_node_recursive(
        self, 
        node: javalang.tree.Node, 
        caller_qualified_name: str,
        method_calls: List[Dict[str, Any]]
    ) -> None:
        """Recursively extract method calls from an AST node."""
        if node is None:
            return
        
        # Check if current node is a method invocation
        if isinstance(node, javalang.tree.MethodInvocation):
            call_info = {
                'caller': caller_qualified_name,
                'method_name': node.member,
                'qualifier': None,
                'node': node
            }
            
            # Extract qualifier (object/class the method is called on)
            if node.qualifier:
                if isinstance(node.qualifier, javalang.tree.This):
                    call_info['qualifier'] = 'this'
                elif hasattr(node.qualifier, 'member'):
                    call_info['qualifier'] = node.qualifier.member
                elif hasattr(node.qualifier, 'value'):
                    call_info['qualifier'] = node.qualifier.value
                elif isinstance(node.qualifier, javalang.tree.MemberReference):
                    call_info['qualifier'] = node.qualifier.member
            
            method_calls.append(call_info)
            self._java_stats['method_calls_found'] += 1
        
        # Recursively process child nodes
        for child in node.children:
            if child is not None:
                if isinstance(child, list):
                    for item in child:
                        if hasattr(item, 'children'):  # Only process if it's a Node
                            self._extract_method_calls_from_node_recursive(
                                item, caller_qualified_name, method_calls
                            )
                elif hasattr(child, 'children'):  # Only process if it's a Node
                    self._extract_method_calls_from_node_recursive(
                        child, caller_qualified_name, method_calls
                    )
    
    def _create_call_relationships(
        self, 
        method_calls: List[Dict[str, Any]], 
        entities: List[CodeEntity], 
        file_path: str
    ) -> List[CallRelationship]:
        """Create call relationships from extracted method calls."""
        relationships = []
        
        # Create a mapping of method names to qualified names for local methods
        method_name_map = {}
        for entity in entities:
            if entity.entity_type in [CodeEntityType.METHOD, CodeEntityType.CONSTRUCTOR]:
                method_name_map[entity.name] = entity.qualified_name
        
        for call_info in method_calls:
            caller = call_info['caller']
            method_name = call_info['method_name']
            qualifier = call_info['qualifier']
            
            # Try to resolve the callee
            callee = None
            call_type = "direct"
            
            if qualifier == 'this' or qualifier is None:
                # Local method call within the same class
                if method_name in method_name_map:
                    callee = method_name_map[method_name]
            else:
                # External method call - create a qualified name
                callee = f"{qualifier}.{method_name}" if qualifier else method_name
                call_type = "external"
            
            if callee and callee != caller:  # Avoid self-calls
                relationship = CallRelationship(
                    caller=caller,
                    callee=callee,
                    call_type=call_type,
                    file_path=file_path,
                    language=self.language
                )
                relationships.append(relationship)
        
        return relationships
    
    def _extract_visibility(self, modifiers: Optional[List[str]]) -> VisibilityModifier:
        """Extract visibility modifier from Java modifiers."""
        if not modifiers:
            return VisibilityModifier.PACKAGE  # Default Java visibility
        
        modifiers_set = set(modifiers)
        
        if 'public' in modifiers_set:
            return VisibilityModifier.PUBLIC
        elif 'private' in modifiers_set:
            return VisibilityModifier.PRIVATE
        elif 'protected' in modifiers_set:
            return VisibilityModifier.PROTECTED
        else:
            return VisibilityModifier.PACKAGE
    
    def _extract_modifiers(self, modifiers: Optional[List[str]]) -> List[str]:
        """Extract all modifiers as strings."""
        return list(modifiers) if modifiers else []
    
    def _extract_type_name(self, type_node: javalang.tree.Type) -> str:
        """Extract type name from a javalang type node."""
        if hasattr(type_node, 'name'):
            return type_node.name
        elif hasattr(type_node, 'element_type'):
            # Array type
            element_type = self._extract_type_name(type_node.element_type)
            return f"{element_type}[]"
        else:
            return str(type_node)
    
    def get_java_stats(self) -> Dict[str, Any]:
        """Get Java-specific parsing statistics."""
        stats = self.get_stats()
        stats.update(self._java_stats)
        return stats 