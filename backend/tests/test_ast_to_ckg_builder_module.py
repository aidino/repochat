"""
Comprehensive tests for ASTtoCKGBuilderModule and CKGQueryInterfaceModule
Tests Phase 2: Tasks 2.6, 2.7, 2.8 functionality
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from typing import Dict, List

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, src_dir)

from teams.ckg_operations.ast_to_ckg_builder_module import (
    ASTtoCKGBuilderModule,
    CKGQueryInterfaceModule,
    CKGBuildResult
)
from teams.ckg_operations.models import (
    CoordinatorParseResult,
    LanguageParseResult,
    ParseResult,
    CodeEntity,
    CallRelationship,
    CodeEntityType,
    VisibilityModifier
)
from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule


class TestASTtoCKGBuilderModule:
    """Test AST to CKG Builder functionality."""
    
    @pytest.fixture
    def mock_neo4j_connection(self):
        """Create mock Neo4j connection."""
        mock_conn = Mock(spec=Neo4jConnectionModule)
        mock_conn.is_connected.return_value = True
        mock_conn.connect.return_value = True
        
        # Mock session context manager properly
        mock_session = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_session)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_conn.get_session.return_value = mock_context_manager
        
        return mock_conn
    
    @pytest.fixture
    def sample_coordinator_result(self):
        """Create sample coordinator parse result."""
        # Create sample entities
        class_entity = CodeEntity(
            name="TestClass",
            entity_type=CodeEntityType.CLASS,
            file_path="/test/TestClass.java",
            start_line=5,
            visibility=VisibilityModifier.PUBLIC,
            language="java"
        )
        
        method_entity = CodeEntity(
            name="testMethod",
            entity_type=CodeEntityType.METHOD,
            file_path="/test/TestClass.java",
            start_line=10,
            visibility=VisibilityModifier.PUBLIC,
            parent_entity="TestClass",
            language="java"
        )
        
        # Create sample relationships
        call_relationship = CallRelationship(
            caller="testMethod",
            callee="helper",
            file_path="/test/TestClass.java",
            line_number=12,
            language="java"
        )
        
        # Create parse result
        parse_result = ParseResult(
            file_path="/test/TestClass.java",
            language="java",
            entities=[class_entity, method_entity],
            relationships=[call_relationship],
            parse_duration_ms=50.0
        )
        
        # Create language result
        language_result = LanguageParseResult(
            language="java",
            files_parsed=[parse_result],
            total_entities=2,
            total_relationships=1,
            parse_duration_ms=50.0
        )
        
        # Create coordinator result
        return CoordinatorParseResult(
            project_path="/test",
            languages_processed=["java"],
            language_results={"java": language_result},
            total_files_parsed=1,
            total_entities_found=2,
            total_relationships_found=1,
            coordination_duration_ms=50.0
        )
    
    @pytest.fixture
    def ckg_builder(self, mock_neo4j_connection):
        """Create CKG builder with mock connection."""
        return ASTtoCKGBuilderModule(neo4j_connection=mock_neo4j_connection)
    
    def test_init_with_connection(self, mock_neo4j_connection):
        """Test initialization with provided connection."""
        builder = ASTtoCKGBuilderModule(neo4j_connection=mock_neo4j_connection)
        assert builder.neo4j == mock_neo4j_connection
        assert builder.logger is not None
        assert 'build_sessions' in builder._stats
    
    def test_init_without_connection(self):
        """Test initialization without provided connection."""
        with patch('teams.ckg_operations.ast_to_ckg_builder_module.Neo4jConnectionModule'):
            builder = ASTtoCKGBuilderModule()
            assert builder.neo4j is not None
    
    def test_build_ckg_success(self, ckg_builder, sample_coordinator_result):
        """Test successful CKG building from coordinator result."""
        # Setup mock session behavior
        mock_session = ckg_builder.neo4j.get_session.return_value.__enter__.return_value
        mock_session.run.return_value = Mock()
        
        # Execute build
        result = ckg_builder.build_ckg_from_coordinator_result(
            coordinator_result=sample_coordinator_result,
            project_name="test_project"
        )
        
        # Verify result
        assert isinstance(result, CKGBuildResult)
        assert result.success is True
        assert result.build_duration_ms > 0
        assert result.files_processed >= 0
        
        # Verify statistics updated
        assert ckg_builder._stats['build_sessions'] == 1
    
    def test_build_ckg_connection_failure(self, sample_coordinator_result):
        """Test CKG building with connection failure."""
        # Create builder with failing connection
        mock_conn = Mock(spec=Neo4jConnectionModule)
        mock_conn.is_connected.return_value = False
        mock_conn.connect.return_value = False
        
        builder = ASTtoCKGBuilderModule(neo4j_connection=mock_conn)
        
        # Execute build
        result = builder.build_ckg_from_coordinator_result(
            coordinator_result=sample_coordinator_result,
            project_name="test_project"
        )
        
        # Verify failure
        assert result.success is False
        assert len(result.errors) > 0
        assert "Failed to connect to Neo4j" in result.errors[0]
    
    def test_build_ckg_exception_handling(self, mock_neo4j_connection, sample_coordinator_result):
        """Test CKG building with exception during processing."""
        # Setup session to raise exception
        mock_session = Mock()
        mock_session.run.side_effect = Exception("Database error")
        mock_neo4j_connection.get_session.return_value.__enter__.return_value = mock_session
        
        builder = ASTtoCKGBuilderModule(neo4j_connection=mock_neo4j_connection)
        
        # Execute build
        result = builder.build_ckg_from_coordinator_result(
            coordinator_result=sample_coordinator_result,
            project_name="test_project"
        )
        
        # Verify error handling
        assert result.success is False
        assert len(result.errors) > 0
        assert "Failed to build CKG" in result.errors[0]
    
    def test_get_build_statistics(self, ckg_builder):
        """Test getting build statistics."""
        stats = ckg_builder.get_build_statistics()
        
        assert isinstance(stats, dict)
        assert 'build_sessions' in stats
        assert 'total_nodes_created' in stats
        assert 'total_relationships_created' in stats
        assert 'total_files_processed' in stats
        assert 'total_build_time_ms' in stats
    
    def test_node_labels_mapping(self, ckg_builder):
        """Test that node labels are correctly mapped."""
        expected_labels = {
            CodeEntityType.FILE: "File",
            CodeEntityType.PACKAGE: "Package",
            CodeEntityType.CLASS: "Class",
            CodeEntityType.INTERFACE: "Interface",
            CodeEntityType.METHOD: "Method",
            CodeEntityType.CONSTRUCTOR: "Constructor",
            CodeEntityType.FIELD: "Field",
            CodeEntityType.VARIABLE: "Variable"
        }
        
        assert ckg_builder.NODE_LABELS == expected_labels


class TestCKGQueryInterfaceModule:
    """Test CKG Query Interface functionality."""
    
    @pytest.fixture
    def mock_neo4j_connection(self):
        """Create mock Neo4j connection for queries."""
        mock_conn = Mock(spec=Neo4jConnectionModule)
        mock_conn.is_connected.return_value = True
        
        # Mock session and query results properly
        mock_session = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_session)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_conn.get_session.return_value = mock_context_manager
        
        return mock_conn
    
    @pytest.fixture
    def query_interface(self, mock_neo4j_connection):
        """Create query interface with mock connection."""
        return CKGQueryInterfaceModule(neo4j_connection=mock_neo4j_connection)
    
    def test_init_with_connection(self, mock_neo4j_connection):
        """Test initialization with provided connection."""
        interface = CKGQueryInterfaceModule(neo4j_connection=mock_neo4j_connection)
        assert interface.neo4j == mock_neo4j_connection
        assert interface.logger is not None
    
    def test_init_without_connection(self):
        """Test initialization without provided connection."""
        with patch('teams.ckg_operations.ast_to_ckg_builder_module.Neo4jConnectionModule'):
            interface = CKGQueryInterfaceModule()
            assert interface.neo4j is not None
    
    def test_get_project_overview(self, query_interface):
        """Test getting project overview."""
        # Mock query results
        mock_session = query_interface.neo4j.get_session.return_value.__enter__.return_value
        mock_session.run.return_value = [
            {"language": "java", "files": 5, "classes": 3, "methods": 15},
            {"language": "python", "files": 2, "classes": 1, "methods": 8}
        ]
        
        # Execute query
        overview = query_interface.get_project_overview("test_project")
        
        # Verify results
        assert isinstance(overview, dict)
        assert "project_name" in overview
        assert overview["project_name"] == "test_project"
        
        # Verify query was called
        mock_session.run.assert_called()
    
    def test_get_class_complexity_analysis(self, query_interface):
        """Test getting class complexity analysis."""
        # Mock query results
        mock_session = query_interface.neo4j.get_session.return_value.__enter__.return_value
        mock_session.run.return_value = [
            {
                "class_name": "ComplexClass", 
                "method_count": 20, 
                "public_method_count": 15,
                "complexity_score": 85.5
            }
        ]
        
        # Execute query
        analysis = query_interface.get_class_complexity_analysis("test_project", limit=10)
        
        # Verify results
        assert isinstance(analysis, list)
        mock_session.run.assert_called()
    
    def test_get_method_call_patterns(self, query_interface):
        """Test getting method call patterns."""
        # Mock query results
        mock_session = query_interface.neo4j.get_session.return_value.__enter__.return_value
        mock_session.run.return_value = [
            {
                "caller": "TestClass.testMethod",
                "callee": "Helper.process", 
                "call_count": 5,
                "files_involved": 2
            }
        ]
        
        # Execute query
        patterns = query_interface.get_method_call_patterns("test_project", limit=15)
        
        # Verify results
        assert isinstance(patterns, list)
        mock_session.run.assert_called()
    
    def test_get_public_api_surface(self, query_interface):
        """Test getting public API surface."""
        # Mock query results
        mock_session = query_interface.neo4j.get_session.return_value.__enter__.return_value
        mock_session.run.return_value = [
            {
                "entity_name": "PublicClass.publicMethod",
                "entity_type": "Method",
                "file_path": "/src/PublicClass.java",
                "line_number": 25
            }
        ]
        
        # Execute query
        api_surface = query_interface.get_public_api_surface("test_project")
        
        # Verify results
        assert isinstance(api_surface, list)
        mock_session.run.assert_called()
    
    def test_get_potential_refactoring_candidates(self, query_interface):
        """Test getting refactoring candidates."""
        # Mock query results
        mock_session = query_interface.neo4j.get_session.return_value.__enter__.return_value
        mock_session.run.return_value = [
            {
                "entity_name": "LargeClass",
                "issue_type": "Large Class",
                "severity": "HIGH",
                "description": "Class has too many methods (50)",
                "file_path": "/src/LargeClass.java"
            }
        ]
        
        # Execute query
        candidates = query_interface.get_potential_refactoring_candidates("test_project")
        
        # Verify results
        assert isinstance(candidates, list)
        mock_session.run.assert_called()


class TestIntegratedCKGWorkflow:
    """Test integrated workflow of CKG building and querying."""
    
    @pytest.fixture
    def mock_neo4j_connection(self):
        """Create comprehensive mock for integrated testing."""
        mock_conn = Mock(spec=Neo4jConnectionModule)
        mock_conn.is_connected.return_value = True
        mock_conn.connect.return_value = True
        
        mock_session = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_session)
        mock_context_manager.__exit__ = Mock(return_value=None)
        mock_conn.get_session.return_value = mock_context_manager
        
        return mock_conn
    
    def test_full_ckg_workflow(self, mock_neo4j_connection):
        """Test complete CKG workflow: build then query."""
        # Create sample data
        class_entity = CodeEntity(
            name="TestService",
            entity_type=CodeEntityType.CLASS,
            file_path="/src/TestService.java",
            start_line=1,
            visibility=VisibilityModifier.PUBLIC,
            language="java"
        )
        
        parse_result = ParseResult(
            file_path="/src/TestService.java",
            language="java",
            entities=[class_entity],
            relationships=[],
            parse_duration_ms=30.0
        )
        
        language_result = LanguageParseResult(
            language="java",
            files_parsed=[parse_result],
            total_entities=1,
            total_relationships=0,
            parse_duration_ms=30.0
        )
        
        coordinator_result = CoordinatorParseResult(
            project_path="/src",
            languages_processed=["java"],
            language_results={"java": language_result},
            total_files_parsed=1,
            total_entities_found=1,
            total_relationships_found=0,
            coordination_duration_ms=30.0
        )
        
        # Test building
        builder = ASTtoCKGBuilderModule(neo4j_connection=mock_neo4j_connection)
        build_result = builder.build_ckg_from_coordinator_result(
            coordinator_result=coordinator_result,
            project_name="integration_test"
        )
        
        assert build_result.success is True
        
        # Test querying
        query_interface = CKGQueryInterfaceModule(neo4j_connection=mock_neo4j_connection)
        
        # Mock query results for overview
        mock_session = mock_neo4j_connection.get_session.return_value.__enter__.return_value
        mock_session.run.return_value = [
            {"language": "java", "files": 1, "classes": 1, "methods": 0}
        ]
        
        overview = query_interface.get_project_overview("integration_test")
        assert overview["project_name"] == "integration_test"
    
    def test_error_recovery_workflow(self, mock_neo4j_connection):
        """Test workflow with errors and recovery."""
        # Setup session to fail initially then succeed
        mock_session = Mock()
        mock_session.run.side_effect = [
            Exception("Initial failure"),  # First call fails
            Mock()  # Second call succeeds
        ]
        mock_neo4j_connection.get_session.return_value.__enter__.return_value = mock_session
        
        # Create minimal coordinator result
        coordinator_result = CoordinatorParseResult(
            project_path="/error_test",
            languages_processed=[],
            language_results={},
            total_files_parsed=0,
            total_entities_found=0,
            total_relationships_found=0,
            coordination_duration_ms=0.0
        )
        
        # Test that builder handles errors gracefully
        builder = ASTtoCKGBuilderModule(neo4j_connection=mock_neo4j_connection)
        result = builder.build_ckg_from_coordinator_result(
            coordinator_result=coordinator_result,
            project_name="error_test"
        )
        
        # Should fail gracefully
        assert result.success is False
        assert len(result.errors) > 0
        
        # Statistics should still be updated
        stats = builder.get_build_statistics()
        assert stats['build_sessions'] == 1


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"]) 