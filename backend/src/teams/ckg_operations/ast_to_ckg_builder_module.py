"""
AST to CKG Builder Module for TEAM CKG Operations

Implements Task 2.6-2.7: Chuyển đổi AST/parsed results thành Code Knowledge Graph
- Convert code entities to Neo4j nodes  
- Convert method calls to Neo4j relationships
- Comprehensive CKG schema implementation
- Performance optimized bulk operations

Enhanced for manual testing and code review insights.
"""

import time
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from .models import (
    CoordinatorParseResult, 
    LanguageParseResult, 
    ParseResult,
    CodeEntity, 
    CallRelationship,
    CodeEntityType,
    VisibilityModifier
)
from .neo4j_connection_module import Neo4jConnectionModule
# Note: Logging utilities not available in current structure
# from ..shared.utils.logging_config import (
#     log_function_entry, 
#     log_function_exit,
#     log_performance_metric
# )

def log_function_entry(logger, func_name, **kwargs):
    """Mock function entry logging."""
    logger.debug(f"Entering {func_name} with {kwargs}")

def log_function_exit(logger, func_name, **kwargs):
    """Mock function exit logging."""
    logger.debug(f"Exiting {func_name} with {kwargs}")

def log_performance_metric(logger, metric_name, value, unit):
    """Mock performance metric logging."""
    logger.info(f"METRIC {metric_name}: {value} {unit}")


@dataclass
class CKGBuildResult:
    """Result of CKG building operation."""
    success: bool
    nodes_created: int = 0
    relationships_created: int = 0
    files_processed: int = 0
    build_duration_ms: float = 0.0
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class ASTtoCKGBuilderModule:
    """
    AST to Code Knowledge Graph Builder Module.
    
    Converts parsed code entities and relationships into Neo4j graph structure.
    Implements comprehensive CKG schema for code analysis and review.
    """
    
    def __init__(self, neo4j_connection: Optional[Neo4jConnectionModule] = None):
        """
        Initialize AST to CKG builder.
        
        Args:
            neo4j_connection: Optional Neo4j connection module. If None, creates new one.
        """
        self.logger = logging.getLogger(f"repochat.ckg_operations.ast_to_ckg_builder")
        
        # Neo4j connection
        self.neo4j = neo4j_connection or Neo4jConnectionModule()
        
        # CKG Schema constants
        self.NODE_LABELS = {
            CodeEntityType.FILE: "File",
            CodeEntityType.PACKAGE: "Package", 
            CodeEntityType.CLASS: "Class",
            CodeEntityType.INTERFACE: "Interface",
            CodeEntityType.METHOD: "Method",
            CodeEntityType.CONSTRUCTOR: "Constructor",
            CodeEntityType.FIELD: "Field",
            CodeEntityType.VARIABLE: "Variable"
        }
        
        # Build statistics
        self._stats = {
            'build_sessions': 0,
            'total_nodes_created': 0,
            'total_relationships_created': 0,
            'total_files_processed': 0,
            'total_build_time_ms': 0.0
        }
        
        self.logger.info("AST to CKG Builder Module initialized")
    
    def build_ckg_from_coordinator_result(
        self, 
        coordinator_result: CoordinatorParseResult,
        project_name: str
    ) -> CKGBuildResult:
        """
        Build CKG from coordinator parsing results.
        
        Args:
            coordinator_result: Results from CodeParserCoordinatorModule
            project_name: Name of the project for graph organization
            
        Returns:
            CKGBuildResult with detailed build statistics
        """
        start_time = time.time()
        log_function_entry(
            self.logger, 
            "build_ckg_from_coordinator_result",
            project_name=project_name,
            languages_count=len(coordinator_result.languages_processed)
        )
        
        self._stats['build_sessions'] += 1
        
        # Initialize result
        result = CKGBuildResult(success=False)
        
        try:
            # Ensure connection
            if not self.neo4j.is_connected():
                if not self.neo4j.connect():
                    raise RuntimeError("Failed to connect to Neo4j")
            
            with self.neo4j.get_session() as session:
                # Clear existing project data
                self._clear_project_data(session, project_name)
                
                # Create project root node
                self._create_project_node(session, project_name, coordinator_result)
                
                # Process each language
                for language, language_result in coordinator_result.language_results.items():
                    self.logger.info(f"Building CKG for {language}")
                    
                    language_stats = self._build_language_ckg(
                        session, project_name, language, language_result
                    )
                    
                    result.nodes_created += language_stats['nodes_created']
                    result.relationships_created += language_stats['relationships_created']
                    result.files_processed += language_stats['files_processed']
                
                # Create indexes for performance
                self._create_ckg_indexes(session)
                
                result.success = True
                
        except Exception as e:
            error_msg = f"Failed to build CKG: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
        
        # Record timing and statistics
        result.build_duration_ms = (time.time() - start_time) * 1000
        
        self._stats['total_nodes_created'] += result.nodes_created
        self._stats['total_relationships_created'] += result.relationships_created
        self._stats['total_files_processed'] += result.files_processed
        self._stats['total_build_time_ms'] += result.build_duration_ms
        
        log_performance_metric(
            self.logger,
            "ckg_build_time",
            result.build_duration_ms,
            "ms"
        )
        
        log_function_exit(
            self.logger, 
            "build_ckg_from_coordinator_result", 
            result="success" if result.success else "failed",
            execution_time=(time.time() - start_time),
            nodes_created=result.nodes_created,
            relationships_created=result.relationships_created
        )
        
        return result
    
    def _clear_project_data(self, session, project_name: str):
        """Clear existing project data from Neo4j."""
        
        clear_query = """
        MATCH (n)
        WHERE n.project_name = $project_name
        DETACH DELETE n
        """
        
        session.run(clear_query, project_name=project_name)
        self.logger.info(f"Cleared existing data for project: {project_name}")
    
    def _create_project_node(
        self, 
        session, 
        project_name: str, 
        coordinator_result: CoordinatorParseResult
    ):
        """Create project root node."""
        
        create_project_query = """
        CREATE (p:Project {
            name: $project_name,
            project_name: $project_name,
            path: $project_path,
            languages_count: $languages_count,
            languages: $languages,
            total_files: $total_files,
            total_entities: $total_entities,
            total_relationships: $total_relationships,
            created_at: datetime(),
            coordination_duration_ms: $coordination_duration_ms
        })
        RETURN p
        """
        
        session.run(create_project_query,
            project_name=project_name,
            project_path=coordinator_result.project_path,
            languages_count=len(coordinator_result.languages_processed),
            languages=coordinator_result.languages_processed,
            total_files=coordinator_result.total_files_parsed,
            total_entities=coordinator_result.total_entities_found,
            total_relationships=coordinator_result.total_relationships_found,
            coordination_duration_ms=coordinator_result.coordination_duration_ms
        )
        
        self.logger.info(f"Created project node: {project_name}")
    
    def _build_language_ckg(
        self, 
        session, 
        project_name: str, 
        language: str, 
        language_result: LanguageParseResult
    ) -> Dict[str, int]:
        """Build CKG for a specific language."""
        
        stats = {
            'nodes_created': 0,
            'relationships_created': 0,
            'files_processed': 0
        }
        
        # Process each file
        for file_result in language_result.files_parsed:
            file_stats = self._build_file_ckg(
                session, project_name, language, file_result
            )
            
            stats['nodes_created'] += file_stats['nodes_created']
            stats['relationships_created'] += file_stats['relationships_created']
            stats['files_processed'] += 1
        
        return stats
    
    def _build_file_ckg(
        self, 
        session, 
        project_name: str, 
        language: str, 
        file_result: ParseResult
    ) -> Dict[str, int]:
        """Build CKG for a single file."""
        
        stats = {'nodes_created': 0, 'relationships_created': 0}
        
        # Create file node
        file_node_id = self._create_file_node(
            session, project_name, language, file_result
        )
        stats['nodes_created'] += 1
        
        # Create entity nodes
        entity_map = {}  # qualified_name -> node_id
        
        for entity in file_result.entities:
            node_id = self._create_entity_node(
                session, project_name, language, entity, file_node_id
            )
            entity_map[entity.qualified_name] = node_id
            stats['nodes_created'] += 1
        
        # Create call relationships
        for relationship in file_result.relationships:
            if self._create_call_relationship(
                session, relationship, entity_map
            ):
                stats['relationships_created'] += 1
        
        return stats
    
    def _create_file_node(
        self, 
        session, 
        project_name: str, 
        language: str, 
        file_result: ParseResult
    ) -> str:
        """Create file node in Neo4j."""
        
        create_file_query = """
        CREATE (f:File {
            name: $file_name,
            path: $file_path,
            project_name: $project_name,
            language: $language,
            entities_count: $entities_count,
            relationships_count: $relationships_count,
            parse_duration_ms: $parse_duration_ms,
            has_errors: $has_errors,
            created_at: datetime()
        })
        RETURN elementId(f) as file_id
        """
        
        file_name = file_result.file_path.split('/')[-1]
        
        result = session.run(create_file_query,
            file_name=file_name,
            file_path=file_result.file_path,
            project_name=project_name,
            language=language,
            entities_count=len(file_result.entities),
            relationships_count=len(file_result.relationships),
            parse_duration_ms=file_result.parse_duration_ms,
            has_errors=len(file_result.errors) > 0
        )
        
        return result.single()['file_id']
    
    def _create_entity_node(
        self, 
        session, 
        project_name: str, 
        language: str, 
        entity: CodeEntity, 
        file_node_id: str
    ) -> str:
        """Create entity node in Neo4j."""
        
        label = self.NODE_LABELS.get(entity.entity_type, "CodeEntity")
        
        create_entity_query = f"""
        CREATE (e:{label} {{
            name: $name,
            qualified_name: $qualified_name,
            project_name: $project_name,
            language: $language,
            entity_type: $entity_type,
            visibility: $visibility,
            parent_entity: $parent_entity,
            signature: $signature,
            return_type: $return_type,
            parameters_count: $parameters_count,
            modifiers: $modifiers,
            created_at: datetime()
        }})
        WITH e
        MATCH (f:File) WHERE elementId(f) = $file_id
        CREATE (f)-[:CONTAINS]->(e)
        RETURN elementId(e) as entity_id
        """
        
        result = session.run(create_entity_query,
            name=entity.name,
            qualified_name=entity.qualified_name,
            project_name=project_name,
            language=language,
            entity_type=entity.entity_type.value,
            visibility=entity.visibility.value,
            parent_entity=entity.parent_entity,
            signature=entity.signature,
            return_type=entity.return_type,
            parameters_count=len(entity.parameters) if entity.parameters else 0,
            modifiers=entity.modifiers,
            file_id=file_node_id
        )
        
        return result.single()['entity_id']
    
    def _create_call_relationship(
        self, 
        session, 
        relationship: CallRelationship, 
        entity_map: Dict[str, str]
    ) -> bool:
        """Create call relationship in Neo4j."""
        
        caller_id = entity_map.get(relationship.caller)
        callee_id = entity_map.get(relationship.callee)
        
        if not caller_id or not callee_id:
            # Cross-file call or external call - log for potential future enhancement
            self.logger.debug(f"Skipping cross-file call: {relationship.caller} -> {relationship.callee}")
            return False
        
        create_call_query = """
        MATCH (caller) WHERE elementId(caller) = $caller_id
        MATCH (callee) WHERE elementId(callee) = $callee_id
        CREATE (caller)-[:CALLS {
            call_type: $call_type,
            language: $language,
            created_at: datetime()
        }]->(callee)
        """
        
        session.run(create_call_query,
            caller_id=caller_id,
            callee_id=callee_id,
            call_type=relationship.call_type,
            language=relationship.language
        )
        
        return True
    
    def _create_ckg_indexes(self, session):
        """Create indexes for CKG performance."""
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (p:Project) ON (p.project_name)",
            "CREATE INDEX IF NOT EXISTS FOR (f:File) ON (f.project_name)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Class) ON (c.project_name)",
            "CREATE INDEX IF NOT EXISTS FOR (m:Method) ON (m.project_name)",
            "CREATE INDEX IF NOT EXISTS FOR (n) ON (n.qualified_name)",
            "CREATE INDEX IF NOT EXISTS FOR (n) ON (n.name)"
        ]
        
        for index_query in indexes:
            try:
                session.run(index_query)
            except Exception as e:
                self.logger.warning(f"Failed to create index: {e}")
    
    def get_build_statistics(self) -> Dict[str, Any]:
        """Get CKG build statistics."""
        return self._stats.copy()


class CKGQueryInterfaceModule:
    """
    CKG Query Interface Module for code review insights.
    
    Provides specialized queries for extracting useful information
    from the Code Knowledge Graph for code review purposes.
    """
    
    def __init__(self, neo4j_connection: Optional[Neo4jConnectionModule] = None):
        """Initialize CKG query interface."""
        self.logger = logging.getLogger(f"repochat.ckg_operations.ckg_query_interface")
        self.neo4j = neo4j_connection or Neo4jConnectionModule()
        
        self.logger.info("CKG Query Interface Module initialized")
    
    def get_project_overview(self, project_name: str) -> Dict[str, Any]:
        """Get comprehensive project overview."""
        
        query = """
        MATCH (p:Project {project_name: $project_name})
        OPTIONAL MATCH (f:File {project_name: $project_name})
        OPTIONAL MATCH (e {project_name: $project_name})
        WHERE e:Class OR e:Method OR e:Field OR e:Constructor OR e:Interface
        RETURN p,
               count(DISTINCT f) as files_count,
               count(DISTINCT e) as entities_count,
               collect(DISTINCT labels(e)[0]) as entity_types
        """
        
        # Ensure connection
        if not self.neo4j.is_connected():
            if not self.neo4j.connect():
                return {}
        
        with self.neo4j.get_session() as session:
            result = session.run(query, project_name=project_name)
            record = result.single()
            
            if record and record['p']:
                project = record['p']
                return {
                    'project_name': project['name'],
                    'languages': project.get('languages', []),
                    'total_files': project.get('total_files', 0),
                    'files_in_graph': record['files_count'],
                    'total_entities': project.get('total_entities', 0),
                    'entities_in_graph': record['entities_count'],
                    'entity_types': record['entity_types'],
                    'coordination_time_ms': project.get('coordination_duration_ms', 0)
                }
        
        return {}
    
    def get_class_complexity_analysis(self, project_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Analyze class complexity based on methods and call relationships."""
        
        query = """
        MATCH (c:Class {project_name: $project_name})
        OPTIONAL MATCH (f:File)-[:CONTAINS]->(c)
        OPTIONAL MATCH (f)-[:CONTAINS]->(m:Method)
        OPTIONAL MATCH (m)-[:CALLS]->(called)
        OPTIONAL MATCH (caller)-[:CALLS]->(m)
        RETURN c.name as class_name,
               c.qualified_name as qualified_name,
               f.path as file_path,
               count(DISTINCT m) as methods_count,
               count(DISTINCT called) as outgoing_calls,
               count(DISTINCT caller) as incoming_calls,
               c.visibility as visibility,
               c.modifiers as modifiers
        ORDER BY methods_count DESC, outgoing_calls DESC
        LIMIT $limit
        """
        
        # Ensure connection
        if not self.neo4j.is_connected():
            if not self.neo4j.connect():
                return []
        
        with self.neo4j.get_session() as session:
            result = session.run(query, project_name=project_name, limit=limit)
            
            classes = []
            for record in result:
                complexity_score = (
                    record['methods_count'] * 2 + 
                    record['outgoing_calls'] + 
                    record['incoming_calls']
                )
                
                classes.append({
                    'class_name': record['class_name'],
                    'qualified_name': record['qualified_name'],
                    'file_path': record['file_path'],
                    'methods_count': record['methods_count'],
                    'outgoing_calls': record['outgoing_calls'],
                    'incoming_calls': record['incoming_calls'],
                    'complexity_score': complexity_score,
                    'visibility': record['visibility'],
                    'modifiers': record['modifiers']
                })
            
            return classes
    
    def get_method_call_patterns(self, project_name: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Analyze method call patterns for code review insights."""
        
        query = """
        MATCH (caller:Method {project_name: $project_name})-[:CALLS]->(callee:Method)
        OPTIONAL MATCH (caller_file:File)-[:CONTAINS]->(caller)
        OPTIONAL MATCH (callee_file:File)-[:CONTAINS]->(callee)
        OPTIONAL MATCH (caller_file)-[:CONTAINS]->(caller_class:Class)
        OPTIONAL MATCH (callee_file)-[:CONTAINS]->(callee_class:Class)
        RETURN caller.name as caller_method,
               callee.name as callee_method,
               caller.qualified_name as caller_qualified,
               callee.qualified_name as callee_qualified,
               caller_class.name as caller_class,
               callee_class.name as callee_class,
               caller.visibility as caller_visibility,
               callee.visibility as callee_visibility
        ORDER BY caller.name, callee.name
        LIMIT $limit
        """
        
        # Ensure connection
        if not self.neo4j.is_connected():
            if not self.neo4j.connect():
                return []
        
        with self.neo4j.get_session() as session:
            result = session.run(query, project_name=project_name, limit=limit)
            
            patterns = []
            for record in result:
                is_cross_class = record['caller_class'] != record['callee_class']
                
                patterns.append({
                    'caller_method': record['caller_method'],
                    'callee_method': record['callee_method'],
                    'caller_qualified': record['caller_qualified'],
                    'callee_qualified': record['callee_qualified'],
                    'caller_class': record['caller_class'],
                    'callee_class': record['callee_class'],
                    'is_cross_class_call': is_cross_class,
                    'caller_visibility': record['caller_visibility'],
                    'callee_visibility': record['callee_visibility']
                })
            
            return patterns
    
    def get_public_api_surface(self, project_name: str) -> List[Dict[str, Any]]:
        """Get public API surface for review."""
        
        query = """
        MATCH (e {project_name: $project_name})
        WHERE e.visibility = 'public' 
        AND (e:Method OR e:Class OR e:Field)
        OPTIONAL MATCH (parent_file:File)-[:CONTAINS]->(parent)-[:CONTAINS]->(e)
        OPTIONAL MATCH (f:File)-[:CONTAINS]->(e)
        OPTIONAL MATCH (caller)-[:CALLS]->(e)
        RETURN labels(e)[0] as entity_type,
               e.name as name,
               e.qualified_name as qualified_name,
               e.signature as signature,
               parent.name as parent_name,
               COALESCE(f.path, parent_file.path) as file_path,
               count(DISTINCT caller) as usage_count
        ORDER BY entity_type, usage_count DESC, name
        """
        
        # Ensure connection
        if not self.neo4j.is_connected():
            if not self.neo4j.connect():
                return []
        
        with self.neo4j.get_session() as session:
            result = session.run(query, project_name=project_name)
            
            api_elements = []
            for record in result:
                api_elements.append({
                    'entity_type': record['entity_type'],
                    'name': record['name'],
                    'qualified_name': record['qualified_name'],
                    'signature': record['signature'],
                    'parent_name': record['parent_name'],
                    'file_path': record['file_path'],
                    'usage_count': record['usage_count']
                })
            
            return api_elements
    
    def get_potential_refactoring_candidates(self, project_name: str) -> List[Dict[str, Any]]:
        """Find potential refactoring candidates."""
        
        query = """
        // Find methods with high complexity (many calls)
        MATCH (m:Method {project_name: $project_name})
        OPTIONAL MATCH (m)-[:CALLS]->(called)
        WITH m, count(called) as outgoing_calls
        WHERE outgoing_calls > 5
        
        OPTIONAL MATCH (f:File)-[:CONTAINS]->(c:Class)
        OPTIONAL MATCH (f)-[:CONTAINS]->(m)
        
        RETURN m.name as method_name,
               m.qualified_name as qualified_name,
               c.name as class_name,
               f.path as file_path,
               outgoing_calls,
               m.signature as signature,
               m.visibility as visibility
        ORDER BY outgoing_calls DESC
        LIMIT 10
        """
        
        # Ensure connection  
        if not self.neo4j.is_connected():
            if not self.neo4j.connect():
                return []
        
        with self.neo4j.get_session() as session:
            result = session.run(query, project_name=project_name)
            
            candidates = []
            for record in result:
                candidates.append({
                    'method_name': record['method_name'],
                    'qualified_name': record['qualified_name'],
                    'class_name': record['class_name'],
                    'file_path': record['file_path'],
                    'outgoing_calls': record['outgoing_calls'],
                    'signature': record['signature'],
                    'visibility': record['visibility'],
                    'refactoring_reason': f"High complexity: {record['outgoing_calls']} outgoing calls"
                })
            
            return candidates 