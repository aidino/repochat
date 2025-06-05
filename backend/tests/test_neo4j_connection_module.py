"""
Tests for Neo4j Connection Module

This module contains comprehensive unit tests for the Neo4j Connection Module,
including connection, disconnection, query execution, and error handling scenarios.

Created for Task 2.1 (F2.1) requirements.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule


class TestNeo4jConnectionModule:
    """Test cases for Neo4jConnectionModule basic functionality."""
    
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
    def test_connect_success(self, mock_graph_db):
        """Test successful database connection."""
        # Create module
        module = Neo4jConnectionModule(
            uri="bolt://localhost:7687",
            username="test_user", 
            password="test_password",
            database="test_db"
        )
        
        # Setup mocks
        driver_mock = Mock()
        session_mock = Mock()
        result_mock = Mock()
        record_mock = Mock()
        
        # Configure the mock chain
        mock_graph_db.driver.return_value = driver_mock
        
        # Setup context manager for session
        session_context = Mock()
        session_context.__enter__ = Mock(return_value=session_mock)
        session_context.__exit__ = Mock(return_value=None)
        driver_mock.session.return_value = session_context
        
        # Setup query execution chain
        session_mock.run.return_value = result_mock
        result_mock.single.return_value = record_mock
        record_mock.__getitem__ = Mock(return_value=1)
        
        # Test connection
        result = module.connect()
        
        assert result is True
        assert module.is_connected()
        assert module._stats['connection_attempts'] == 1
        mock_graph_db.driver.assert_called_once()
        session_mock.run.assert_called_once_with("RETURN 1 as test")
        record_mock.__getitem__.assert_called_once_with("test")
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_connect_service_unavailable(self, mock_graph_db):
        """Test connection failure due to service unavailable."""
        from neo4j.exceptions import ServiceUnavailable
        
        module = Neo4jConnectionModule()
        mock_graph_db.driver.side_effect = ServiceUnavailable("Service unavailable")
        
        result = module.connect()
        
        assert result is False
        assert not module.is_connected()
        assert module._stats['connection_attempts'] == 1
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_connect_auth_error(self, mock_graph_db):
        """Test connection failure due to authentication error."""
        from neo4j.exceptions import AuthError
        
        module = Neo4jConnectionModule()
        mock_graph_db.driver.side_effect = AuthError("Authentication failed")
        
        result = module.connect()
        
        assert result is False
        assert not module.is_connected()
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_connect_general_exception(self, mock_graph_db):
        """Test connection failure due to general exception."""
        module = Neo4jConnectionModule()
        mock_graph_db.driver.side_effect = Exception("General error")
        
        result = module.connect()
        
        assert result is False
        assert not module.is_connected()
    
    def test_disconnect_success(self):
        """Test successful disconnection."""
        module = Neo4jConnectionModule()
        driver_mock = Mock()
        module._driver = driver_mock
        module._is_connected = True
        
        module.disconnect()
        
        assert not module.is_connected()
        assert module._driver is None
        driver_mock.close.assert_called_once()
    
    def test_disconnect_no_driver(self):
        """Test disconnection when no driver exists."""
        module = Neo4jConnectionModule()
        module._driver = None
        module._is_connected = False
        
        # Should not raise exception
        module.disconnect()
        
        assert not module.is_connected()
    
    def test_disconnect_exception(self):
        """Test disconnection with driver close exception."""
        module = Neo4jConnectionModule()
        driver_mock = Mock()
        driver_mock.close.side_effect = Exception("Close error")
        module._driver = driver_mock
        module._is_connected = True
        
        # Should not raise exception, just log it
        module.disconnect()
        
        assert not module.is_connected()
    
    def test_get_stats(self):
        """Test statistics retrieval."""
        module = Neo4jConnectionModule()
        module._stats['queries_executed'] = 5
        module._stats['successful_queries'] = 4
        module._stats['failed_queries'] = 1
        
        stats = module.get_stats()
        
        assert 'queries_executed' in stats
        assert 'successful_queries' in stats
        assert 'failed_queries' in stats
        assert 'average_query_time_ms' in stats
        assert stats['queries_executed'] == 5
    
    def test_get_stats_no_queries(self):
        """Test statistics when no queries executed."""
        module = Neo4jConnectionModule()
        stats = module.get_stats()
        assert stats['average_query_time_ms'] == 0.0
    
    def test_context_manager_already_connected(self):
        """Test context manager when already connected."""
        module = Neo4jConnectionModule()
        module._is_connected = True
        module._driver = Mock()  # Mock driver to satisfy is_connected() check
        
        with module as conn:
            assert conn is module
            assert module.is_connected()
    
    def test_destructor_cleanup(self):
        """Test destructor performs cleanup."""
        module = Neo4jConnectionModule()
        driver_mock = Mock()
        module._driver = driver_mock
        module._is_connected = True
        
        # Simulate destructor call
        module.__del__()
        
        # Should have called disconnect functionality
        assert not module.is_connected()


class TestNeo4jConnectionModuleEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_multiple_connection_attempts(self):
        """Test multiple connection attempts increment counter."""
        module = Neo4jConnectionModule()
        
        # Multiple connection attempts should increment counter
        with patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase') as mock_graph_db:
            mock_graph_db.driver.side_effect = Exception("Connection failed")
            
            module.connect()  # First attempt
            module.connect()  # Second attempt
            
            assert module._stats['connection_attempts'] == 2
    
    @patch('src.teams.ckg_operations.neo4j_connection_module.GraphDatabase')
    def test_connection_verification_failure(self, mock_graph_db):
        """Test connection that succeeds but verification fails."""
        module = Neo4jConnectionModule()
        
        # Setup mocks
        driver_mock = Mock()
        session_mock = Mock()
        result_mock = Mock()
        record_mock = Mock()
        
        # Configure successful driver creation
        mock_graph_db.driver.return_value = driver_mock
        
        # Setup context manager
        session_context = Mock()
        session_context.__enter__ = Mock(return_value=session_mock)
        session_context.__exit__ = Mock(return_value=None)
        driver_mock.session.return_value = session_context
        
        # Setup query but return wrong value for verification
        session_mock.run.return_value = result_mock
        result_mock.single.return_value = record_mock
        record_mock.__getitem__ = Mock(return_value=0)  # Wrong value, should be 1
        
        result = module.connect()
        
        assert result is False
        assert not module.is_connected()


class TestNeo4jConnectionModuleIntegration:
    """Integration test placeholders for manual testing."""
    
    def test_real_connection_placeholder(self):
        """Placeholder for real Neo4j connection tests."""
        # This would require a real Neo4j instance running
        # Should be run as part of integration test suite
        pass
    
    def test_performance_metrics_placeholder(self):
        """Placeholder for performance testing."""
        # Would test actual query performance and metrics
        pass 