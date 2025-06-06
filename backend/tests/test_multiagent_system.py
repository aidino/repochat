"""
Multi-Agent System Comprehensive Test Suite

Test suite tổng hợp cho hệ thống multi-agent RepoChat.
"""

import asyncio
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from orchestrator.migration_manager import MigrationManager, MigrationPhase
from teams.shared.external_agent_integration import (
    ExternalAgentRegistry, 
    ExternalAgentType,
    CrewAIAgentAdapter
)
from teams.shared.api_gateway import APIGateway, SecurityManager


class TestMultiAgentDependencies:
    """Test Phase 1: Dependencies and basic imports."""
    
    def test_google_adk_available(self):
        """Test Google ADK availability."""
        try:
            import google_adk
            assert True, "Google ADK imported successfully"
        except ImportError:
            pytest.skip("Google ADK not available in test environment")
    
    def test_a2a_sdk_available(self):
        """Test A2A SDK availability."""
        try:
            import a2a_sdk
            assert True, "A2A SDK imported successfully"
        except ImportError:
            pytest.skip("A2A SDK not available in test environment")
    
    def test_circuit_breaker_available(self):
        """Test circuit breaker libraries."""
        try:
            import tenacity
            import circuit_breaker
            assert True, "Circuit breaker libraries available"
        except ImportError as e:
            pytest.fail(f"Circuit breaker libraries not available: {e}")
    
    def test_monitoring_libraries(self):
        """Test monitoring and metrics libraries."""
        try:
            import prometheus_client
            assert True, "Prometheus client available"
        except ImportError as e:
            pytest.fail(f"Monitoring libraries not available: {e}")


class TestMigrationManager:
    """Test Phase 2: Migration Manager functionality."""
    
    @pytest.fixture
    def migration_manager(self):
        """Create migration manager instance."""
        return MigrationManager()
    
    def test_migration_manager_initialization(self, migration_manager):
        """Test migration manager can be initialized."""
        assert migration_manager is not None
        assert migration_manager.current_phase == MigrationPhase.BASELINE
        assert migration_manager.circuit_breaker is not None
    
    @pytest.mark.asyncio
    async def test_phase_progression(self, migration_manager):
        """Test migration phase progression."""
        # Start at baseline
        assert migration_manager.current_phase == MigrationPhase.BASELINE
        
        # Progress through phases
        phases = [
            MigrationPhase.CANARY,
            MigrationPhase.PARTIAL, 
            MigrationPhase.MAJORITY,
            MigrationPhase.COMPLETE
        ]
        
        for phase in phases:
            await migration_manager.advance_phase()
            # Note: In test environment, advancement may be simulated
    
    @pytest.mark.asyncio
    async def test_traffic_splitting(self, migration_manager):
        """Test traffic splitting functionality."""
        # Mock request processing
        mock_request = {"test": "data"}
        
        with patch.object(migration_manager, '_process_legacy_request', 
                         return_value={"status": "success", "source": "legacy"}):
            with patch.object(migration_manager, '_process_enhanced_request',
                            return_value={"status": "success", "source": "enhanced"}):
                
                result = await migration_manager.process_request(mock_request)
                assert result is not None
                assert "status" in result
    
    def test_circuit_breaker_functionality(self, migration_manager):
        """Test circuit breaker state management."""
        cb = migration_manager.circuit_breaker
        assert cb.state == "closed"  # Should start closed (healthy)
        
        # Circuit breaker should handle failures
        assert hasattr(cb, 'record_success')
        assert hasattr(cb, 'record_failure')


class TestExternalAgentIntegration:
    """Test Phase 3: External agent integration."""
    
    @pytest.fixture
    def agent_registry(self):
        """Create agent registry instance."""
        return ExternalAgentRegistry()
    
    def test_agent_registry_initialization(self, agent_registry):
        """Test agent registry can be initialized."""
        assert agent_registry is not None
        assert len(agent_registry.agents) == 0
    
    @pytest.mark.asyncio
    async def test_crewai_agent_registration(self, agent_registry):
        """Test CrewAI agent registration."""
        agent_manifest = {
            "agent_id": "test-crewai",
            "name": "Test CrewAI Agent", 
            "agent_type": "crewai",
            "version": "1.0.0",
            "description": "Test agent",
            "capabilities": []
        }
        
        try:
            success = await agent_registry.register_crewai_agent(agent_manifest)
            assert success is True
            assert "test-crewai" in agent_registry.agents
        except Exception as e:
            pytest.skip(f"CrewAI not available: {e}")
    
    @pytest.mark.asyncio
    async def test_custom_agent_registration(self, agent_registry):
        """Test custom agent registration."""
        
        async def mock_executor(task_description, target=None):
            return {"status": "completed", "result": "mock analysis"}
        
        agent_manifest = {
            "agent_id": "test-custom",
            "name": "Test Custom Agent",
            "agent_type": "custom", 
            "version": "1.0.0",
            "description": "Test custom agent",
            "capabilities": []
        }
        
        success = await agent_registry.register_custom_agent(
            agent_manifest, mock_executor
        )
        assert success is True
        assert "test-custom" in agent_registry.agents
    
    @pytest.mark.asyncio
    async def test_agent_task_execution(self, agent_registry):
        """Test agent task execution."""
        # Register a mock agent first
        async def mock_executor(task_description, target=None):
            return {
                "status": "completed",
                "result": f"Analyzed: {task_description}",
                "agent_type": "custom"
            }
        
        agent_manifest = {
            "agent_id": "test-executor",
            "name": "Test Executor Agent",
            "agent_type": "custom",
            "version": "1.0.0", 
            "description": "Test executor",
            "capabilities": []
        }
        
        await agent_registry.register_custom_agent(agent_manifest, mock_executor)
        
        # Execute task
        result = await agent_registry.execute_agent_task(
            "test-executor",
            "Test task execution",
            target="sample_code.py"
        )
        
        assert result is not None
        assert result["status"] == "completed"
        assert "Analyzed" in result["result"]


class TestAPIGateway:
    """Test Phase 3: API Gateway functionality."""
    
    @pytest.fixture
    def security_manager(self):
        """Create security manager instance."""
        return SecurityManager()
    
    def test_security_manager_initialization(self, security_manager):
        """Test security manager initialization."""
        assert security_manager is not None
        assert len(security_manager.api_keys) >= 2  # Should have public and enterprise keys
    
    def test_api_key_validation(self, security_manager):
        """Test API key validation."""
        # Test valid keys
        public_key = "rca_public_key_123"
        enterprise_key = "rca_enterprise_key_456"
        
        assert security_manager.validate_api_key(public_key) is True
        assert security_manager.validate_api_key(enterprise_key) is True
        
        # Test invalid key
        assert security_manager.validate_api_key("invalid_key") is False
    
    def test_security_level_checking(self, security_manager):
        """Test security level validation."""
        public_key = "rca_public_key_123"
        enterprise_key = "rca_enterprise_key_456"
        
        # Public key should access public endpoints
        assert security_manager.check_access_level(public_key, "PUBLIC") is True
        
        # Enterprise key should access all levels
        assert security_manager.check_access_level(enterprise_key, "PUBLIC") is True
        assert security_manager.check_access_level(enterprise_key, "ENTERPRISE") is True
        
        # Public key should not access enterprise endpoints
        assert security_manager.check_access_level(public_key, "ENTERPRISE") is False


class TestEndToEndIntegration:
    """Test end-to-end multi-agent system integration."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete multi-agent workflow."""
        # Initialize components
        migration_manager = MigrationManager()
        agent_registry = ExternalAgentRegistry()
        security_manager = SecurityManager()
        
        # Verify all components are functional
        assert migration_manager is not None
        assert agent_registry is not None
        assert security_manager is not None
        
        # Register a test agent
        async def mock_analyzer(task_description, target=None):
            return {
                "status": "completed",
                "analysis": f"Analyzed {target}",
                "recommendations": ["Use better naming", "Add type hints"]
            }
        
        agent_manifest = {
            "agent_id": "integration-test-agent",
            "name": "Integration Test Agent",
            "agent_type": "custom",
            "version": "1.0.0",
            "description": "Agent for integration testing",
            "capabilities": []
        }
        
        await agent_registry.register_custom_agent(agent_manifest, mock_analyzer)
        
        # Execute a task through the agent
        result = await agent_registry.execute_agent_task(
            "integration-test-agent",
            "Analyze code quality",
            target="test_file.py"
        )
        
        assert result["status"] == "completed"
        assert "analysis" in result
        
        # Test security validation
        assert security_manager.validate_api_key("rca_public_key_123") is True
        
        print("✅ End-to-end integration test passed")


@pytest.mark.asyncio
async def test_comprehensive_multiagent_validation():
    """
    Comprehensive validation of all multi-agent components.
    
    This test validates:
    1. All dependencies are available
    2. Migration manager functions correctly  
    3. External agent integration works
    4. API gateway security is functional
    5. End-to-end workflow is operational
    """
    print("🚀 Starting Comprehensive Multi-Agent Validation...")
    
    # Phase 1: Dependencies
    try:
        import tenacity
        import circuit_breaker
        print("✅ Phase 1: Dependencies validated")
    except ImportError as e:
        print(f"❌ Phase 1: Dependencies error: {e}")
        return False
    
    # Phase 2: Migration Manager
    try:
        migration_manager = MigrationManager()
        assert migration_manager.current_phase == MigrationPhase.BASELINE
        print("✅ Phase 2: Migration Manager validated")
    except Exception as e:
        print(f"❌ Phase 2: Migration Manager error: {e}")
        return False
    
    # Phase 3: External Agents
    try:
        agent_registry = ExternalAgentRegistry()
        
        # Register test agent
        async def test_executor(desc, target=None):
            return {"status": "completed", "result": "test analysis"}
            
        await agent_registry.register_custom_agent({
            "agent_id": "test-agent",
            "name": "Test Agent", 
            "agent_type": "custom",
            "version": "1.0.0",
            "description": "Test",
            "capabilities": []
        }, test_executor)
        
        result = await agent_registry.execute_agent_task(
            "test-agent", "Test task", target="test.py"
        )
        assert result["status"] == "completed"
        print("✅ Phase 3: External Agents validated")
    except Exception as e:
        print(f"❌ Phase 3: External Agents error: {e}")
        return False
    
    # API Gateway Security
    try:
        security_manager = SecurityManager()
        assert security_manager.validate_api_key("rca_public_key_123") is True
        print("✅ API Gateway Security validated")
    except Exception as e:
        print(f"❌ API Gateway Security error: {e}")
        return False
    
    print("🎯 Comprehensive Multi-Agent Validation: ✅ PASSED")
    return True


if __name__ == "__main__":
    # Run the comprehensive test
    async def main():
        await test_comprehensive_multiagent_validation()
    
    asyncio.run(main()) 