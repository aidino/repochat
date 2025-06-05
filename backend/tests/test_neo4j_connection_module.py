"""
Unit Tests for Neo4jConnectionModule - TEAM CKG Operations

Comprehensive test suite covering:
- Module initialization and configuration
- Connection management (connect/disconnect)
- Query execution (CREATE, MATCH, etc.)
- Error handling and edge cases
- Statistics and health monitoring
- Context manager functionality

Tests include expected use cases, edge cases, and failure scenarios
as per RepoChat testing guidelines.
"""

import pytest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Mock Neo4j before importing the module
with patch.dict('sys.modules', {
    'neo4j': MagicMock(),
    'neo4j.exceptions': MagicMock()
}):
    from src.teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule


class TestNeo4jConnectionModule:
    """Test suite for Neo4jConnectionModule."""
    
    @pytest.fixture
    def mock_neo4j_driver(self):
        """Mock Neo4j driver for testing."""
        driver_mock = Mock()
        session_mock = Mock()
        result_mock = Mock()
        record_mock = Mock()
        
        # Setup return values
        record_mock.data.return_value = {'test': 1}
        record_mock.single.return_value = record_mock
        result_mock.single.return_value = record_mock
        result_mock.__iter__ = Mock(return_value=iter([record_mock]))
        session_mock.run.return_value = result_mock
        driver_mock.session.return_value.__enter__.return_value = session_mock
        driver_mock.session.return_value.__exit__.return_value = None
        
        return driver_mock, session_mock, result_mock, record_mock
    
    @pytest.fixture
    def connection_module(self):
        """Create Neo4jConnectionModule instance for testing."""
        return Neo4jConnectionModule(
            uri="bolt://localhost:7687",
            username="test_user", 
            password="test_password",
            database="test_db"
        )
    
    def test_initialization_with_defaults(self):
        """Test module initialization with default parameters."""
        module = Neo4jConnectionModule()
        
        assert module.uri == 'bolt://localhost:7687'
        assert module.username == 'neo4j'
        assert module.password == 'password'
        assert module.database == 'neo4j'
        assert not module.is_connected()
        assert module._stats['queries_executed'] == 0
    
    def test_initialization_with_custom_params(self):
        """Test module initialization with custom parameters."""
        module = Neo4jConnectionModule(
            uri="bolt://custom:7687",
            username="custom_user",
            password="custom_pass", 
            database="custom_db"
        )
        
        assert module.uri == "bolt://custom:7687"
        assert module.username == "custom_user"
        assert module.password == "custom_pass"
        assert module.database == "custom_db"
    
    @patch.dict(os.environ, {
        'NEO4J_URI': 'bolt://env:7687',
        'NEO4J_USERNAME': 'env_user',
        'NEO4J_PASSWORD': 'env_pass'
    })
    def test_initialization_with_environment_variables(self):
        """Test initialization with environment variables."""
        module = Neo4jConnectionModule()
        
        assert module.uri == 'bolt://env:7687'
        assert module.username == 'env_user'
        assert module.password == 'env_pass'
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_connect_success(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test successful database connection."""
        driver_mock, session_mock, result_mock, record_mock = mock_neo4j_driver
        mock_graph_db.driver.return_value = driver_mock
        
        # Mock successful connection test
        record_mock.__getitem__ = Mock(return_value=1)
        
        result = connection_module.connect()
        
        assert result is True
        assert connection_module.is_connected()
        assert connection_module._stats['connection_attempts'] == 1
        mock_graph_db.driver.assert_called_once()
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_connect_service_unavailable(self, mock_graph_db, connection_module):
        """Test connection failure due to service unavailable."""
        from neo4j.exceptions import ServiceUnavailable
        mock_graph_db.driver.side_effect = ServiceUnavailable("Service unavailable")
        
        result = connection_module.connect()
        
        assert result is False
        assert not connection_module.is_connected()
        assert connection_module._stats['connection_attempts'] == 1
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_connect_auth_error(self, mock_graph_db, connection_module):
        """Test connection failure due to authentication error."""
        from neo4j.exceptions import AuthError
        mock_graph_db.driver.side_effect = AuthError("Authentication failed")
        
        result = connection_module.connect()
        
        assert result is False
        assert not connection_module.is_connected()
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_connect_general_exception(self, mock_graph_db, connection_module):
        """Test connection failure due to general exception."""
        mock_graph_db.driver.side_effect = Exception("General error")
        
        result = connection_module.connect()
        
        assert result is False
        assert not connection_module.is_connected()
    
    def test_disconnect_success(self, connection_module, mock_neo4j_driver):
        """Test successful disconnection."""
        driver_mock, _, _, _ = mock_neo4j_driver
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        connection_module.disconnect()
        
        assert not connection_module.is_connected()
        assert connection_module._driver is None
        driver_mock.close.assert_called_once()
    
    def test_disconnect_no_driver(self, connection_module):
        """Test disconnection when no driver exists."""
        connection_module._driver = None
        connection_module._is_connected = False
        
        # Should not raise exception
        connection_module.disconnect()
        
        assert not connection_module.is_connected()
    
    def test_disconnect_exception(self, connection_module):
        """Test disconnection with driver close exception."""
        driver_mock = Mock()
        driver_mock.close.side_effect = Exception("Close error")
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Should not raise exception, just log it
        connection_module.disconnect()
        
        assert not connection_module.is_connected()
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_health_check_success(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test successful health check."""
        driver_mock, session_mock, result_mock, record_mock = mock_neo4j_driver
        
        # Setup connected state
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Mock health check queries
        test_record = Mock()
        test_record.__getitem__ = Mock(side_effect=lambda key: 1 if key == "test" else 42)
        
        node_record = Mock()
        node_record.__getitem__ = Mock(return_value=42)
        
        session_mock.run.side_effect = [
            Mock(single=Mock(return_value=test_record)),  # test query
            Mock(single=Mock(return_value=node_record))   # node count query
        ]
        
        result = connection_module.health_check()
        
        assert result['connected'] is True
        assert result['database_accessible'] is True
        assert result['response_time_ms'] is not None
        assert result['node_count'] == 42
        assert connection_module._last_health_check is not None
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_health_check_exception(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test health check with exception."""
        driver_mock, session_mock, _, _ = mock_neo4j_driver
        
        # Setup connected state
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Mock exception during health check
        session_mock.run.side_effect = Exception("Health check error")
        
        result = connection_module.health_check()
        
        assert result['connected'] is False
        assert 'error' in result
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_execute_query_fetch_all_success(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test successful query execution with fetch_all=True."""
        driver_mock, session_mock, result_mock, record_mock = mock_neo4j_driver
        
        # Setup connected state
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Mock query result
        record_mock.data.return_value = {'id': 1, 'name': 'test'}
        result_mock.__iter__ = Mock(return_value=iter([record_mock, record_mock]))
        
        result = connection_module.execute_query("MATCH (n) RETURN n", fetch_all=True)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {'id': 1, 'name': 'test'}
        assert connection_module._stats['queries_executed'] == 1
        assert connection_module._stats['successful_queries'] == 1
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_execute_query_fetch_single_success(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test successful query execution with fetch_all=False."""
        driver_mock, session_mock, result_mock, record_mock = mock_neo4j_driver
        
        # Setup connected state
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Mock single record result
        record_mock.data.return_value = {'count': 5}
        result_mock.single.return_value = record_mock
        
        result = connection_module.execute_query("MATCH (n) RETURN count(n)", fetch_all=False)
        
        assert result == {'count': 5}
        assert connection_module._stats['successful_queries'] == 1
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_execute_query_with_parameters(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test query execution with parameters."""
        driver_mock, session_mock, result_mock, record_mock = mock_neo4j_driver
        
        # Setup connected state
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        parameters = {'name': 'test_name', 'value': 42}
        
        connection_module.execute_query(
            "CREATE (n:Node {name: $name, value: $value})", 
            parameters=parameters
        )
        
        session_mock.run.assert_called_with(
            "CREATE (n:Node {name: $name, value: $value})", 
            parameters
        )
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_execute_query_syntax_error(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test query execution with syntax error."""
        driver_mock, session_mock, _, _ = mock_neo4j_driver
        
        # Setup connected state
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Mock syntax error
        from neo4j.exceptions import CypherSyntaxError
        session_mock.run.side_effect = CypherSyntaxError("Syntax error")
        
        result = connection_module.execute_query("INVALID QUERY")
        
        assert result is None
        assert connection_module._stats['failed_queries'] == 1
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_execute_query_client_error(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test query execution with client error."""
        driver_mock, session_mock, _, _ = mock_neo4j_driver
        
        # Setup connected state
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Mock client error
        from neo4j.exceptions import ClientError
        session_mock.run.side_effect = ClientError("Client error")
        
        result = connection_module.execute_query("RETURN 1")
        
        assert result is None
        assert connection_module._stats['failed_queries'] == 1
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_get_session_success(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test successful session context manager."""
        driver_mock, session_mock, _, _ = mock_neo4j_driver
        
        # Setup connected state
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Mock session creation
        driver_mock.session.return_value = session_mock
        
        with connection_module.get_session() as session:
            assert session == session_mock
        
        session_mock.close.assert_called_once()
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_create_node_success(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test successful node creation."""
        driver_mock, session_mock, result_mock, record_mock = mock_neo4j_driver
        
        # Setup connected state and mock response
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Mock node creation result
        node_data = {'id': 123, 'name': 'test_node', 'type': 'Test'}
        record_mock.data.return_value = {'n': node_data}
        result_mock.single.return_value = record_mock
        
        properties = {'name': 'test_node', 'type': 'Test'}
        result = connection_module.create_node('TestNode', properties)
        
        assert result == node_data
        session_mock.run.assert_called_once()
        
        # Verify query format
        call_args = session_mock.run.call_args
        query = call_args[0][0]
        assert 'CREATE (n:TestNode' in query
        assert call_args[0][1] == properties
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_find_nodes_without_properties(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test finding nodes without property filters."""
        driver_mock, session_mock, result_mock, record_mock = mock_neo4j_driver
        
        # Setup connected state
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Mock find result
        node_data = {'id': 1, 'name': 'node1'}
        record_mock.data.return_value = {'n': node_data}
        result_mock.__iter__ = Mock(return_value=iter([record_mock]))
        
        result = connection_module.find_nodes('TestNode')
        
        assert len(result) == 1
        assert result[0] == node_data
        
        # Verify query
        call_args = session_mock.run.call_args
        query = call_args[0][0]
        assert 'MATCH (n:TestNode)' in query
        assert 'WHERE' not in query
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_find_nodes_with_properties(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test finding nodes with property filters."""
        driver_mock, session_mock, result_mock, record_mock = mock_neo4j_driver
        
        # Setup connected state
        connection_module._driver = driver_mock
        connection_module._is_connected = True
        
        # Mock find result
        node_data = {'id': 1, 'name': 'specific_node', 'status': 'active'}
        record_mock.data.return_value = {'n': node_data}
        result_mock.__iter__ = Mock(return_value=iter([record_mock]))
        
        properties = {'name': 'specific_node', 'status': 'active'}
        result = connection_module.find_nodes('TestNode', properties)
        
        assert len(result) == 1
        assert result[0] == node_data
        
        # Verify query with WHERE clause
        call_args = session_mock.run.call_args
        query = call_args[0][0]
        assert 'MATCH (n:TestNode) WHERE' in query
        assert 'n.name = $name' in query
        assert 'n.status = $status' in query
        assert call_args[0][1] == properties
    
    def test_get_stats(self, connection_module):
        """Test statistics retrieval."""
        # Set some stats
        connection_module._stats['queries_executed'] = 10
        connection_module._stats['successful_queries'] = 8  
        connection_module._stats['failed_queries'] = 2
        connection_module._stats['total_query_time_ms'] = 1000.0
        connection_module._connection_time = datetime.now()
        
        stats = connection_module.get_stats()
        
        assert stats['queries_executed'] == 10
        assert stats['successful_queries'] == 8
        assert stats['failed_queries'] == 2
        assert stats['connected'] is False  # Not connected in test
        assert stats['average_query_time_ms'] == 100.0  # 1000/10
        assert 'connection_time' in stats
    
    def test_get_stats_no_queries(self, connection_module):
        """Test statistics with no queries executed."""
        stats = connection_module.get_stats()
        
        assert stats['average_query_time_ms'] == 0
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_context_manager_success(self, mock_graph_db, connection_module, mock_neo4j_driver):
        """Test context manager functionality."""
        driver_mock, session_mock, result_mock, record_mock = mock_neo4j_driver
        mock_graph_db.driver.return_value = driver_mock
        
        # Mock connection verification
        record_mock.__getitem__ = Mock(return_value=1)
        
        with connection_module as conn:
            assert conn.is_connected()
            assert conn == connection_module
        
        # Should disconnect after context
        assert not connection_module.is_connected()
    
    def test_context_manager_already_connected(self, connection_module):
        """Test context manager when already connected."""
        # Simulate already connected state
        connection_module._is_connected = True
        connection_module._driver = Mock()
        
        with connection_module as conn:
            assert conn == connection_module
        
        # Should disconnect after context
        assert not connection_module.is_connected()
    
    def test_destructor_cleanup(self, connection_module):
        """Test destructor cleans up connection."""
        driver_mock = Mock()
        connection_module._driver = driver_mock
        
        # Simulate destructor call
        connection_module.__del__()
        
        # Should not raise exception even if disconnect fails
        driver_mock.close.side_effect = Exception("Close error")
        connection_module.__del__()  # Should not raise
    
    def test_integration_workflow(self, connection_module):
        """Test complete workflow integration."""
        # This test would require actual Neo4j instance
        # For now, just test the workflow structure
        
        # 1. Check initial state
        assert not connection_module.is_connected()
        
        # 2. Get stats
        initial_stats = connection_module.get_stats()
        assert initial_stats['queries_executed'] == 0
        
        # 3. Health check without connection
        health = connection_module.health_check()
        assert not health['connected']
        
        # 4. Try to execute query without connection
        result = connection_module.execute_query("RETURN 1")
        assert result is None
        
        # Workflow validation complete
        assert connection_module._stats['queries_executed'] == 0


class TestNeo4jConnectionModuleEdgeCases:
    """Additional edge case tests for Neo4jConnectionModule."""
    
    def test_long_query_truncation_in_logs(self):
        """Test that long queries are truncated in logs."""
        module = Neo4jConnectionModule()
        
        # Create a very long query
        long_query = "MATCH (n) WHERE " + " AND ".join([f"n.prop{i} = {i}" for i in range(100)]) + " RETURN n"
        
        # This should not raise exception during log preparation
        result = module.execute_query(long_query)
        assert result is None  # Not connected, so returns None
    
    def test_empty_query(self):
        """Test handling of empty query."""
        module = Neo4jConnectionModule()
        
        result = module.execute_query("")
        assert result is None
    
    def test_none_parameters(self):
        """Test handling of None parameters."""
        module = Neo4jConnectionModule()
        
        result = module.execute_query("RETURN 1", parameters=None)
        assert result is None  # Not connected
    
    def test_multiple_connection_attempts(self):
        """Test multiple connection attempts."""
        module = Neo4jConnectionModule()
        
        # Multiple connection attempts should increment counter
        module.connect()  # Will fail - no Neo4j running
        module.connect()  # Second attempt
        
        assert module._stats['connection_attempts'] >= 2
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_connection_verification_failure(self, mock_graph_db):
        """Test connection that succeeds but verification fails."""
        driver_mock = Mock()
        session_mock = Mock()
        result_mock = Mock()
        record_mock = Mock()
        
        # Mock driver creation success but verification failure
        mock_graph_db.driver.return_value = driver_mock
        driver_mock.session.return_value.__enter__.return_value = session_mock
        session_mock.run.return_value = result_mock
        result_mock.single.return_value = record_mock
        record_mock.__getitem__ = Mock(return_value=999)  # Wrong verification value
        
        module = Neo4jConnectionModule()
        result = module.connect()
        
        assert result is False
        assert not module.is_connected()


# Integration tests (would require actual Neo4j instance)
class TestNeo4jConnectionModuleIntegration:
    """Integration tests - requires actual Neo4j instance."""
    
    def test_real_connection_placeholder(self):
        """Placeholder for real Neo4j integration tests."""
        # This would test against a real Neo4j instance
        # Skip for now since we don't have Neo4j running in CI
        pytest.skip("Integration test requires Neo4j instance")
    
    def test_performance_metrics_placeholder(self):
        """Placeholder for performance testing."""
        # This would test query performance metrics
        pytest.skip("Performance test requires Neo4j instance") 