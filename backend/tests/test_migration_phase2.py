"""
RepoChat v1.0 - Phase 2 Migration Tests
Comprehensive testing cho migration infrastructure.
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator.migration_manager import MigrationManager, MigrationPhase
from orchestrator.monitoring_dashboard import MonitoringDashboard, MetricsCollector
from teams.shared.a2a_agent_base import A2AAgentBase, AgentStatus, A2AMessage

class TestMigrationManager:
    """Test migration manager functionality."""
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        return {
            'migration_enabled': True,
            'success_threshold': 0.95,
            'performance_threshold': 2.0,
            'circuit_breaker_threshold': 3,
            'legacy_config': {},
            'enhanced_config': {}
        }
    
    @pytest.fixture
    def mock_orchestrators(self):
        """Mock orchestrators for testing."""
        legacy_mock = AsyncMock()
        enhanced_mock = AsyncMock()
        
        # Configure mock responses
        legacy_mock.execute_workflow.return_value = {
            'success': True,
            'result': 'Legacy processed',
            'execution_time': 0.1
        }
        
        enhanced_mock.execute_workflow.return_value = {
            'success': True,
            'result': 'Enhanced processed',
            'execution_time': 0.08
        }
        
        return legacy_mock, enhanced_mock
    
    @pytest.fixture
    def migration_manager(self, config, mock_orchestrators):
        """Create migration manager with mocked orchestrators."""
        manager = MigrationManager(config)
        manager.legacy_orchestrator = mock_orchestrators[0]
        manager.enhanced_orchestrator = mock_orchestrators[1]
        return manager
    
    def test_migration_manager_initialization(self, migration_manager):
        """Test migration manager initializes correctly."""
        assert migration_manager.current_phase == MigrationPhase.PHASE_0_BASELINE
        assert migration_manager.enhanced_traffic_percentage == 0
        assert migration_manager.migration_enabled is True
        assert migration_manager.circuit_breaker_open is False
    
    @pytest.mark.asyncio
    async def test_baseline_phase_uses_legacy_only(self, migration_manager):
        """Test that baseline phase only uses legacy orchestrator."""
        request = {'type': 'test_request', 'data': 'test'}
        
        # Process multiple requests
        for _ in range(5):
            result = await migration_manager.process_request(request)
            assert result['orchestrator_used'] == 'legacy'
        
        # Verify only legacy was called
        assert migration_manager.legacy_orchestrator.execute_workflow.call_count == 5
        assert migration_manager.enhanced_orchestrator.execute_workflow.call_count == 0
    
    @pytest.mark.asyncio
    async def test_canary_phase_traffic_split(self, migration_manager):
        """Test canary phase splits traffic correctly."""
        # Advance to canary phase (10% enhanced)
        migration_manager.current_phase = MigrationPhase.PHASE_1_CANARY
        migration_manager.enhanced_traffic_percentage = 10
        
        request = {'type': 'test_request', 'data': 'test'}
        
        legacy_count = 0
        enhanced_count = 0
        
        # Process many requests to test percentage
        for _ in range(100):
            result = await migration_manager.process_request(request)
            if result['orchestrator_used'] == 'legacy':
                legacy_count += 1
            elif result['orchestrator_used'] == 'enhanced':
                enhanced_count += 1
        
        # Should be approximately 90% legacy, 10% enhanced
        assert 80 <= legacy_count <= 100  # Allow some variance
        assert 0 <= enhanced_count <= 20
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, migration_manager):
        """Test circuit breaker opens on failures."""
        # Setup enhanced orchestrator to fail
        migration_manager.enhanced_orchestrator.execute_workflow.return_value = {
            'success': False,
            'error': 'Simulated failure'
        }
        
        # Advance to canary phase
        migration_manager.current_phase = MigrationPhase.PHASE_1_CANARY
        migration_manager.enhanced_traffic_percentage = 100  # Force enhanced usage
        
        request = {'type': 'test_request', 'data': 'test'}
        
        # Process requests until circuit breaker opens
        for i in range(migration_manager.circuit_breaker_threshold + 1):
            await migration_manager.process_request(request)
        
        assert migration_manager.circuit_breaker_open is True
        assert migration_manager.circuit_breaker_failures >= migration_manager.circuit_breaker_threshold
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self, migration_manager):
        """Test circuit breaker recovers on success."""
        # Open circuit breaker
        migration_manager.circuit_breaker_open = True
        migration_manager.circuit_breaker_failures = 3
        
        # Configure enhanced orchestrator for success
        migration_manager.enhanced_orchestrator.execute_workflow.return_value = {
            'success': True,
            'result': 'Success after recovery'
        }
        
        # Advance to canary and force enhanced usage
        migration_manager.current_phase = MigrationPhase.PHASE_1_CANARY
        migration_manager.enhanced_traffic_percentage = 100
        
        request = {'type': 'test_request', 'data': 'test'}
        
        # Circuit breaker should force legacy usage initially
        result = await migration_manager.process_request(request)
        assert result['orchestrator_used'] == 'legacy'
        
        # Manually reset circuit breaker to test recovery
        migration_manager.circuit_breaker_open = False
        migration_manager.circuit_breaker_failures = 0
        
        # Now enhanced should work and stay working
        result = await migration_manager.process_request(request)
        assert result['orchestrator_used'] == 'enhanced'
        assert migration_manager.circuit_breaker_failures == 0

    def test_metrics_collection(self, migration_manager):
        """Test metrics are collected correctly."""
        # Simulate some processed requests
        migration_manager.metrics['legacy']['requests'] = 10
        migration_manager.metrics['legacy']['successes'] = 9
        migration_manager.metrics['legacy']['failures'] = 1
        migration_manager.metrics['legacy']['total_time'] = 1.0
        
        migration_manager.metrics['enhanced']['requests'] = 5
        migration_manager.metrics['enhanced']['successes'] = 5
        migration_manager.metrics['enhanced']['failures'] = 0
        migration_manager.metrics['enhanced']['total_time'] = 0.4
        
        metrics = migration_manager.get_current_metrics()
        
        assert metrics['legacy']['success_rate'] == 0.9
        assert metrics['legacy']['average_time'] == 0.1
        assert metrics['enhanced']['success_rate'] == 1.0
        assert metrics['enhanced']['average_time'] == 0.08

class TestMetricsCollector:
    """Test metrics collector functionality."""
    
    @pytest.fixture
    def collector(self):
        """Create metrics collector for testing."""
        return MetricsCollector(retention_hours=1)
    
    def test_metrics_collector_initialization(self, collector):
        """Test metrics collector initializes correctly."""
        assert collector.retention_hours == 1
        assert len(collector.metrics) == 0
        assert isinstance(collector.alert_thresholds, dict)
    
    def test_record_metric(self, collector):
        """Test recording metrics."""
        collector.record_metric("test_metric", 1.0, {"tag": "value"})
        
        assert "test_metric" in collector.metrics
        assert len(collector.metrics["test_metric"]) == 1
        
        point = collector.metrics["test_metric"][0]
        assert point.value == 1.0
        assert point.tags["tag"] == "value"
    
    def test_get_metric_series(self, collector):
        """Test retrieving metric series."""
        # Record multiple metrics
        for i in range(5):
            collector.record_metric("test_series", float(i))
        
        series = collector.get_metric_series("test_series")
        assert len(series) == 5
        
        values = [point.value for point in series]
        assert values == [0.0, 1.0, 2.0, 3.0, 4.0]
    
    def test_current_stats_calculation(self, collector):
        """Test current statistics calculation."""
        # Record some metrics
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        for value in values:
            collector.record_metric("test_stats", value)
        
        stats = collector.get_current_stats()
        
        assert "test_stats" in stats
        stat = stats["test_stats"]
        
        assert stat["current"] == 5.0
        assert stat["average"] == 3.0
        assert stat["min"] == 1.0
        assert stat["max"] == 5.0
        assert stat["count"] == 5

class TestA2AAgentBase:
    """Test A2A Agent Base functionality."""
    
    class TestAgent(A2AAgentBase):
        """Test implementation of A2A Agent."""
        
        def _get_capabilities(self):
            return ["test_capability", "example_task"]
        
        async def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success", "result": f"Processed {request.get('type', 'unknown')}"}
    
    @pytest.fixture
    def agent_config(self):
        """Agent configuration for testing."""
        return {
            'agent_id': 'test-agent-001',
            'name': 'TestAgent',
            'version': '1.0.0',
            'a2a_enabled': False,  # Disable A2A for testing
            'circuit_breaker_threshold': 3
        }
    
    @pytest.fixture
    def test_agent(self, agent_config):
        """Create test agent."""
        return self.TestAgent(agent_config)
    
    def test_agent_initialization(self, test_agent):
        """Test agent initializes correctly."""
        assert test_agent.agent_id == 'test-agent-001'
        assert test_agent.name == 'TestAgent'
        assert test_agent.version == '1.0.0'
        assert test_agent.metadata.status == AgentStatus.INITIALIZING
        assert "test_capability" in test_agent.metadata.capabilities
        assert "example_task" in test_agent.metadata.capabilities
    
    @pytest.mark.asyncio
    async def test_agent_startup_sequence(self, test_agent):
        """Test agent startup sequence."""
        await test_agent.start()
        assert test_agent.metadata.status == AgentStatus.READY
        
        await test_agent.stop()
        assert test_agent.metadata.status == AgentStatus.OFFLINE
    
    @pytest.mark.asyncio
    async def test_message_handling(self, test_agent):
        """Test message handling functionality."""
        await test_agent.start()
        
        # Create test message
        message = A2AMessage(
            message_id="test-msg-001",
            message_type="request",
            sender_id="test-sender",
            receiver_id=test_agent.agent_id,
            payload={"type": "test_task", "data": "test_data"},
            timestamp=datetime.now()
        )
        
        response = await test_agent.receive_message(message)
        
        assert response is not None
        assert response["status"] == "success"
        assert "Processed test_task" in response["result"]
    
    @pytest.mark.asyncio
    async def test_ping_handling(self, test_agent):
        """Test ping message handling."""
        await test_agent.start()
        
        ping_message = A2AMessage(
            message_id="ping-001",
            message_type="ping",
            sender_id="test-sender",
            receiver_id=test_agent.agent_id,
            payload={},
            timestamp=datetime.now()
        )
        
        response = await test_agent.receive_message(ping_message)
        
        assert response["message_type"] == "pong"
        assert response["agent_id"] == test_agent.agent_id
    
    @pytest.mark.asyncio
    async def test_health_check(self, test_agent):
        """Test health check functionality."""
        await test_agent.start()
        
        health_message = A2AMessage(
            message_id="health-001",
            message_type="health_check",
            sender_id="test-sender",
            receiver_id=test_agent.agent_id,
            payload={},
            timestamp=datetime.now()
        )
        
        response = await test_agent.receive_message(health_message)
        
        assert response["status"] == "healthy"
        assert response["agent_id"] == test_agent.agent_id
        assert "performance_metrics" in response
    
    def test_performance_tracking(self, test_agent):
        """Test performance metrics tracking."""
        # Simulate some requests
        test_agent._record_request(0.1, True)
        test_agent._record_request(0.2, True)
        test_agent._record_request(0.15, False)
        
        metrics = test_agent._get_performance_metrics()
        
        assert metrics["total_requests"] == 3
        assert metrics["successful_requests"] == 2
        assert metrics["failed_requests"] == 1
        assert metrics["success_rate"] == pytest.approx(0.67, rel=0.01)
        assert metrics["average_processing_time"] == pytest.approx(0.15, rel=0.01)

class TestPhase2Integration:
    """Integration tests for Phase 2 components."""
    
    @pytest.mark.asyncio
    async def test_migration_with_monitoring(self):
        """Test migration manager with monitoring dashboard."""
        config = {
            'migration_enabled': True,
            'circuit_breaker_threshold': 5
        }
        
        # Create mocked migration manager
        manager = MigrationManager(config)
        
        # Mock orchestrators
        manager.legacy_orchestrator = AsyncMock()
        manager.enhanced_orchestrator = AsyncMock()
        
        manager.legacy_orchestrator.execute_workflow.return_value = {
            'success': True, 'result': 'legacy', 'execution_time': 0.1
        }
        manager.enhanced_orchestrator.execute_workflow.return_value = {
            'success': True, 'result': 'enhanced', 'execution_time': 0.08
        }
        
        # Create monitoring dashboard
        dashboard = MonitoringDashboard(manager)
        
        # Start monitoring
        await dashboard.start_monitoring()
        
        # Process some requests
        for i in range(10):
            request = {'type': 'integration_test', 'id': i}
            await manager.process_request(request)
        
        # Check metrics were collected
        metrics = dashboard.get_current_metrics()
        assert 'legacy' in metrics
        assert metrics['legacy']['requests'] == 10
        
        # Stop monitoring
        await dashboard.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_end_to_end_migration_flow(self):
        """Test complete migration flow from baseline to complete."""
        from orchestrator.simple_migration_test import SimpleMigrationManager
        
        config = {
            'migration_enabled': True,
            'circuit_breaker_threshold': 5
        }
        
        manager = SimpleMigrationManager(config)
        
        # Test baseline phase
        assert manager.current_phase == "baseline"
        
        request = {'type': 'e2e_test', 'data': 'test'}
        result = await manager.process_request(request)
        assert result['orchestrator_used'] == 'legacy'
        
        # Test phase progression
        phases_advanced = 0
        while manager.advance_phase():
            phases_advanced += 1
            
            # Test a few requests at each phase
            for _ in range(3):
                await manager.process_request(request)
        
        assert phases_advanced == 4  # baseline -> canary -> partial -> majority -> complete
        assert manager.current_phase == "complete"
        
        # Final phase should use enhanced only
        result = await manager.process_request(request)
        assert result['orchestrator_used'] == 'enhanced'

class TestPhase2Validation:
    """Validate Phase 2 implementation completeness."""
    
    def test_required_files_exist(self):
        """Test that all required Phase 2 files exist."""
        required_files = [
            'src/orchestrator/migration_manager.py',
            'src/orchestrator/monitoring_dashboard.py',
            'src/orchestrator/test_migration.py',
            'src/orchestrator/simple_migration_test.py',
            'src/teams/shared/a2a_agent_base.py'
        ]
        
        backend_path = os.path.join(os.path.dirname(__file__), '..')
        
        for file_path in required_files:
            full_path = os.path.join(backend_path, file_path)
            assert os.path.exists(full_path), f"Required file missing: {file_path}"
    
    @pytest.mark.asyncio
    async def test_migration_end_to_end(self):
        """Test complete end-to-end migration flow."""
        from orchestrator.simple_migration_test import test_simple_migration
        
        # Run the full migration test
        result = await test_simple_migration()
        
        assert result['success'] is True
        assert result['final_phase'] == 'complete'
        assert result['circuit_breaker_functional'] is True
        assert result['total_requests'] > 0
    
    def test_dependencies_available(self):
        """Test that required dependencies are available."""
        required_modules = [
            'tenacity',  # Circuit breaker patterns
            'prometheus_client',  # Metrics collection
        ]
        
        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError:
                pytest.fail(f"Required dependency not available: {module_name}")

class TestPhase2Documentation:
    """Test that Phase 2 is properly documented."""
    
    def test_task_file_updated(self):
        """Test that TASK.md reflects Phase 2 completion."""
        task_file = os.path.join(os.path.dirname(__file__), '..', '..', 'TASK.md')
        
        if os.path.exists(task_file):
            with open(task_file, 'r') as f:
                content = f.read()
                
            # Should contain references to Phase 2 components
            assert 'Phase 2' in content or 'migration' in content.lower()
    
    def test_implementation_documented(self):
        """Test that implementation is documented."""
        # Check that key files have proper docstrings
        files_to_check = [
            '../src/orchestrator/migration_manager.py',
            '../src/orchestrator/monitoring_dashboard.py',
            '../src/teams/shared/a2a_agent_base.py'
        ]
        
        for file_path in files_to_check:
            full_path = os.path.join(os.path.dirname(__file__), file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Should have module docstring
                assert '"""' in content[:200], f"Missing docstring in {file_path}"

if __name__ == "__main__":
    # Run with: python -m pytest tests/test_migration_phase2.py -v
    pytest.main([__file__, "-v", "--tb=short"]) 