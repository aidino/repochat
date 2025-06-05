"""
Neo4j Connection Module for TEAM CKG Operations

This module provides Neo4j database connection and basic operations
for Code Knowledge Graph (CKG) management.

Features:
- Secure connection management with proper resource cleanup
- Basic Cypher query execution (CREATE, MATCH, MERGE)
- Connection health monitoring
- Comprehensive error handling and logging
- Session management for optimal performance

Enhanced for Task 2.1 (F2.1) requirements.
"""

from typing import Optional, Dict, Any, List, Union
import os
import time
from contextlib import contextmanager
from datetime import datetime

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError, ConfigurationError, ClientError, CypherSyntaxError

from shared.utils.logging_config import (
    get_logger, 
    log_function_entry, 
    log_function_exit, 
    log_performance_metric
)


class Neo4jConnectionModule:
    """
    Neo4j connection and operations module for Code Knowledge Graph.
    
    Provides secure database connection, query execution, and health monitoring
    for the CKG operations.
    """
    
    def __init__(
        self, 
        uri: Optional[str] = None,
        username: Optional[str] = None, 
        password: Optional[str] = None,
        database: str = "neo4j"
    ):
        """
        Initialize Neo4j connection module.
        
        Args:
            uri: Neo4j connection URI (default: bolt://localhost:7687)
            username: Neo4j username (default: neo4j)
            password: Neo4j password (default from env or 'password')
            database: Database name (default: neo4j)
        """
        start_time = time.time()
        
        # Setup logging
        self.logger = get_logger(
            "ckg_operations.neo4j_connection",
            extra_context={'component': 'Neo4jConnectionModule'}
        )
        
        log_function_entry(
            self.logger, 
            "__init__", 
            uri=uri, 
            username=username, 
            database=database
        )
        
        # Connection configuration with defaults
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.username = username or os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'repochat123')
        self.database = database
        
        # Connection state
        self._driver: Optional[Driver] = None
        self._is_connected = False
        self._connection_time: Optional[datetime] = None
        self._last_health_check: Optional[datetime] = None
        
        # Statistics
        self._stats = {
            'queries_executed': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'connection_attempts': 0,
            'total_query_time_ms': 0.0
        }
        
        self.logger.info("Neo4j Connection Module initialized", extra={
            'extra_data': {
                'uri': self.uri,
                'username': self.username,
                'database': self.database,
                'driver_initialized': self._driver is not None
            }
        })
        
        init_time = time.time() - start_time
        log_performance_metric(
            self.logger,
            "neo4j_module_init_time",
            init_time * 1000,
            "ms"
        )
        log_function_exit(self.logger, "__init__", result="success", execution_time=init_time)
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        start_time = time.time()
        log_function_entry(self.logger, "connect")
        
        try:
            self._stats['connection_attempts'] += 1
            
            self.logger.info(f"Attempting to connect to Neo4j at {self.uri}")
            
            # Create driver with optimized configuration
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                max_connection_lifetime=3600,  # 1 hour
                max_connection_pool_size=50,
                connection_acquisition_timeout=60  # 60 seconds
            )
            
            # Verify connectivity with a simple query
            connection_start = time.time()
            with self._driver.session(database=self.database) as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value != 1:
                    raise RuntimeError("Connection verification failed")
            
            connection_time = time.time() - connection_start
            
            self._is_connected = True
            self._connection_time = datetime.now()
            self._last_health_check = datetime.now()
            
            self.logger.info("Successfully connected to Neo4j database", extra={
                'extra_data': {
                    'uri': self.uri,
                    'database': self.database,
                    'connection_time_ms': connection_time * 1000,
                    'connection_timestamp': self._connection_time.isoformat()
                }
            })
            
            log_performance_metric(
                self.logger,
                "neo4j_connection_time",
                connection_time * 1000,
                "ms"
            )
            
            total_time = time.time() - start_time
            log_function_exit(self.logger, "connect", result="success", execution_time=total_time)
            return True
            
        except Exception as e:
            # Debug: Check if this is ServiceUnavailable
            if type(e).__name__ == 'ServiceUnavailable':
                self.logger.error(f"Neo4j service unavailable: {e}", extra={
                    'extra_data': {
                        'uri': self.uri,
                        'error_type': 'ServiceUnavailable',
                        'connection_attempt': self._stats['connection_attempts']
                    }
                })
                self._is_connected = False
                log_function_exit(self.logger, "connect", result="service_unavailable", execution_time=time.time() - start_time)
                return False
            # Debug: Check if this is AuthError
            elif type(e).__name__ == 'AuthError':
                self.logger.error(f"Neo4j authentication failed: {e}", extra={
                    'extra_data': {
                        'uri': self.uri,
                        'username': self.username,
                        'error_type': 'AuthError'
                    }
                })
                self._is_connected = False
                log_function_exit(self.logger, "connect", result="auth_error", execution_time=time.time() - start_time)
                return False
            else:
                self.logger.error(f"Failed to connect to Neo4j: {e}", exc_info=True, extra={
                    'extra_data': {
                        'uri': self.uri,
                        'error_type': type(e).__name__,
                        'connection_attempt': self._stats['connection_attempts']
                    }
                })
                self._is_connected = False
                log_function_exit(self.logger, "connect", result="error", execution_time=time.time() - start_time)
                return False

    
    def disconnect(self) -> None:
        """Close Neo4j connection and cleanup resources."""
        start_time = time.time()
        log_function_entry(self.logger, "disconnect")
        
        try:
            if self._driver:
                self._driver.close()
                self.logger.info("Neo4j driver closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during Neo4j disconnect: {e}", exc_info=True)
        
        finally:
            # Always reset connection state, even if close fails
            self._is_connected = False
            self._driver = None
            self._connection_time = None
            
            self.logger.info("Disconnected from Neo4j database", extra={
                'extra_data': {
                    'final_stats': self._stats.copy()
                }
            })
            
            log_function_exit(self.logger, "disconnect", result="success", execution_time=time.time() - start_time)
    
    def is_connected(self) -> bool:
        """
        Check if connection to Neo4j is active.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._is_connected and self._driver is not None
    
    def test_connection(self) -> bool:
        """
        Test Neo4j connection by connecting and executing a simple query.
        
        Returns:
            bool: True if connection test successful, False otherwise
        """
        if not self.is_connected():
            return self.connect()
        
        # If already connected, verify with health check
        health = self.health_check()
        return health.get('database_accessible', False)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Neo4j connection.
        
        Returns:
            Dict with health status information
        """
        start_time = time.time()
        log_function_entry(self.logger, "health_check")
        
        health_status = {
            'connected': False,
            'database_accessible': False,
            'response_time_ms': None,
            'node_count': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if not self.is_connected():
                log_function_exit(self.logger, "health_check", result="not_connected", execution_time=time.time() - start_time)
                return health_status
            
            query_start = time.time()
            with self._driver.session(database=self.database) as session:
                # Simple connectivity test
                result = session.run("RETURN 1 as test")
                test_result = result.single()["test"]
                
                # Get node count for database status
                node_result = session.run("MATCH (n) RETURN count(n) as node_count")
                node_count = node_result.single()["node_count"]
                
                query_time = (time.time() - query_start) * 1000
                
                health_status.update({
                    'connected': True,
                    'database_accessible': test_result == 1,
                    'response_time_ms': query_time,
                    'node_count': node_count
                })
                
                self._last_health_check = datetime.now()
                
                self.logger.debug("Health check completed successfully", extra={
                    'extra_data': health_status
                })
            
            log_function_exit(self.logger, "health_check", result="success", execution_time=time.time() - start_time)
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            health_status['error'] = str(e)
            log_function_exit(self.logger, "health_check", result="error", execution_time=time.time() - start_time)
            return health_status
    
    def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        fetch_all: bool = True
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """
        Execute a Cypher query against Neo4j database.
        
        Args:
            query: Cypher query string
            parameters: Query parameters dict
            fetch_all: If True, return all records; if False, return single record
            
        Returns:
            Query results as list of dicts or single dict, None if error
        """
        start_time = time.time()
        log_function_entry(
            self.logger, 
            "execute_query", 
            query=query[:100] + "..." if len(query) > 100 else query,
            parameters=parameters,
            fetch_all=fetch_all
        )
        
        if not self.is_connected():
            self.logger.error("Cannot execute query: not connected to Neo4j")
            log_function_exit(self.logger, "execute_query", result="not_connected", execution_time=time.time() - start_time)
            return None
        
        try:
            self._stats['queries_executed'] += 1
            
            query_start = time.time()
            with self._driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                
                if fetch_all:
                    records = [record.data() for record in result]
                    query_result = records
                else:
                    single_record = result.single()
                    query_result = single_record.data() if single_record else None
                
                query_time = (time.time() - query_start) * 1000
                self._stats['total_query_time_ms'] += query_time
                self._stats['successful_queries'] += 1
                
                log_performance_metric(
                    self.logger,
                    "neo4j_query_execution_time", 
                    query_time,
                    "ms",
                    query_type=query.strip().split()[0].upper()
                )
                
                self.logger.debug("Query executed successfully", extra={
                    'extra_data': {
                        'query_type': query.strip().split()[0].upper(),
                        'execution_time_ms': query_time,
                        'result_count': len(query_result) if isinstance(query_result, list) else (1 if query_result else 0),
                        'parameters_provided': bool(parameters)
                    }
                })
                
                total_time = time.time() - start_time
                log_function_exit(self.logger, "execute_query", result="success", execution_time=total_time)
                return query_result
                
        except neo4j_exceptions.CypherSyntaxError as e:
            self._stats['failed_queries'] += 1
            self.logger.error(f"Cypher syntax error: {e}", extra={
                'extra_data': {
                    'query': query,
                    'parameters': parameters,
                    'error_type': 'CypherSyntaxError'
                }
            })
            log_function_exit(self.logger, "execute_query", result="syntax_error", execution_time=time.time() - start_time)
            return None
            
        except neo4j_exceptions.ClientError as e:
            self._stats['failed_queries'] += 1
            self.logger.error(f"Neo4j client error: {e}", extra={
                'extra_data': {
                    'query': query,
                    'parameters': parameters,
                    'error_type': 'ClientError'
                }
            })
            log_function_exit(self.logger, "execute_query", result="client_error", execution_time=time.time() - start_time)
            return None
            
        except Exception as e:
            self._stats['failed_queries'] += 1
            self.logger.error(f"Failed to execute query: {e}", exc_info=True, extra={
                'extra_data': {
                    'query': query,
                    'parameters': parameters,
                    'error_type': type(e).__name__
                }
            })
            log_function_exit(self.logger, "execute_query", result="error", execution_time=time.time() - start_time)
            return None
    
    @contextmanager
    def get_session(self):
        """
        Context manager for Neo4j session.
        
        Yields:
            Neo4j session for advanced operations
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to Neo4j database")
        
        session = None
        try:
            session = self._driver.session(database=self.database)
            self.logger.debug("Neo4j session created")
            yield session
        finally:
            if session:
                session.close()
                self.logger.debug("Neo4j session closed")
    
    def create_node(
        self, 
        label: str, 
        properties: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a node with specified label and properties.
        
        Args:
            label: Node label
            properties: Node properties
            
        Returns:
            Created node data or None if error
        """
        log_function_entry(self.logger, "create_node", label=label, properties=properties)
        
        # Build property string for Cypher query
        props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        query = f"CREATE (n:{label} {{{props_str}}}) RETURN n"
        
        result = self.execute_query(query, properties, fetch_all=False)
        
        if result and 'n' in result:
            node_data = result['n']
            self.logger.info(f"Node created successfully: {label}", extra={
                'extra_data': {
                    'label': label,
                    'properties': properties,
                    'node_id': node_data.get('id', 'unknown')
                }
            })
            return node_data
        
        return None
    
    def find_nodes(
        self, 
        label: str, 
        properties: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find nodes by label and optional properties.
        
        Args:
            label: Node label
            properties: Optional property filters
            
        Returns:
            List of matching nodes
        """
        log_function_entry(self.logger, "find_nodes", label=label, properties=properties)
        
        if properties:
            where_clause = " AND ".join([f"n.{k} = ${k}" for k in properties.keys()])
            query = f"MATCH (n:{label}) WHERE {where_clause} RETURN n"
            parameters = properties
        else:
            query = f"MATCH (n:{label}) RETURN n"
            parameters = None
        
        result = self.execute_query(query, parameters, fetch_all=True)
        
        if result:
            nodes = [record['n'] for record in result]
            self.logger.debug(f"Found {len(nodes)} nodes with label {label}")
            return nodes
        
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection and query statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats.update({
            'connected': self.is_connected(),
            'connection_time': self._connection_time.isoformat() if self._connection_time else None,
            'last_health_check': self._last_health_check.isoformat() if self._last_health_check else None,
            'average_query_time_ms': (
                self._stats['total_query_time_ms'] / self._stats['queries_executed'] 
                if self._stats['queries_executed'] > 0 else 0
            )
        })
        return stats
    
    def __enter__(self):
        """Context manager entry."""
        if not self.is_connected():
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __del__(self):
        """Destructor to ensure connection cleanup."""
        try:
            if self._driver:
                self.disconnect()
        except:
            pass  # Ignore errors during cleanup 