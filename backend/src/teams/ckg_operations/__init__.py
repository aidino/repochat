"""
TEAM CKG Operations

Responsible for:
- Code Knowledge Graph (CKG) construction and management
- Code parsing and AST generation
- Neo4j database operations
- CKG schema definition and maintenance
- Graph querying and analysis

Main components:
- Neo4jConnectionModule: Database connection and basic operations
- CodeParserCoordinatorModule: Coordinates language-specific parsing
- BaseLanguageParser: Abstract base for language parsers
- MockParser implementations: For testing and development
- ASTtoCKGBuilderModule: Converts AST to CKG nodes/relationships  
- CKGQueryInterfaceModule: High-level graph querying interface
- Language-specific parsers (Java, Python, Kotlin, Dart)

Phase 2 Implementation Status:
✅ Task 2.1: Neo4jConnectionModule - COMPLETED
✅ Task 2.2: CodeParserCoordinatorModule - COMPLETED
✅ Task 2.3: Java Parser - COMPLETED
⏳ Task 2.4: Python Parser - TODO
⏳ Task 2.5: Kotlin/Dart Parser - TODO
⏳ Task 2.6: ASTtoCKGBuilderModule (nodes) - TODO
⏳ Task 2.7: ASTtoCKGBuilderModule (relationships) - TODO
⏳ Task 2.8: CKGQueryInterfaceModule - TODO
⏳ Task 2.9: Orchestrator integration - TODO
"""

# Import implemented modules
from .neo4j_connection_module import Neo4jConnectionModule
from .code_parser_coordinator_module import CodeParserCoordinatorModule
from .base_parser import BaseLanguageParser
from .mock_parser import (
    MockLanguageParser,
    MockJavaParser,
    MockPythonParser,
    MockKotlinParser,
    MockDartParser
)
from .models import (
    CodeEntity,
    CallRelationship,
    ParseResult,
    LanguageParseResult,
    CoordinatorParseResult,
    CodeEntityType,
    VisibilityModifier
)

# Import real parsers if available
try:
    from .java_parser import JavaParser
    _JAVA_PARSER_AVAILABLE = True
except ImportError:
    JavaParser = None
    _JAVA_PARSER_AVAILABLE = False

# Export public interface
__all__ = [
    'Neo4jConnectionModule',
    'CodeParserCoordinatorModule',
    'BaseLanguageParser',
    'MockLanguageParser',
    'MockJavaParser',
    'MockPythonParser',
    'MockKotlinParser',
    'MockDartParser',
    'CodeEntity',
    'CallRelationship',
    'ParseResult',
    'LanguageParseResult',
    'CoordinatorParseResult',
    'CodeEntityType',
    'VisibilityModifier'
    # Real parsers (available if dependencies installed)
    'JavaParser',  # Available if javalang is installed
    # Future exports:
    # 'ASTtoCKGBuilderModule', 
    # 'CKGQueryInterfaceModule',
    # 'PythonParser',
    # 'KotlinParser',
    # 'DartParser'
]
