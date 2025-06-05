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
- ASTtoCKGBuilderModule: Converts AST to CKG nodes/relationships  
- CKGQueryInterfaceModule: High-level graph querying interface
- Language-specific parsers (Java, Python, Kotlin, Dart)

Phase 2 Implementation Status:
✅ Task 2.1: Neo4jConnectionModule - COMPLETED
⏳ Task 2.2: CodeParserCoordinatorModule - TODO
⏳ Task 2.3: Java Parser - TODO
⏳ Task 2.4: Python Parser - TODO
⏳ Task 2.5: Kotlin/Dart Parser - TODO
⏳ Task 2.6: ASTtoCKGBuilderModule (nodes) - TODO
⏳ Task 2.7: ASTtoCKGBuilderModule (relationships) - TODO
⏳ Task 2.8: CKGQueryInterfaceModule - TODO
⏳ Task 2.9: Orchestrator integration - TODO
"""

# Import implemented modules
from .neo4j_connection_module import Neo4jConnectionModule

# Export public interface
__all__ = [
    'Neo4jConnectionModule',
    # Future exports:
    # 'CodeParserCoordinatorModule',
    # 'ASTtoCKGBuilderModule', 
    # 'CKGQueryInterfaceModule',
    # 'JavaParser',
    # 'PythonParser',
    # 'KotlinParser',
    # 'DartParser'
]
