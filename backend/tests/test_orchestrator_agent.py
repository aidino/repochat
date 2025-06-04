"""
Unit Tests for OrchestratorAgent

Tests for the OrchestratorAgent class, including:
- Expected use case
- Edge case 
- Failure case
"""

import pytest
from unittest.mock import patch, MagicMock
import uuid

from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition


class TestOrchestratorAgent:
    """Test suite for OrchestratorAgent class."""
    
    def test_orchestrator_agent_initialization_expected_use(self):
        """Test normal OrchestratorAgent initialization."""
        # Act
        orchestrator = OrchestratorAgent()
        
        # Assert
        assert orchestrator.agent_id is not None
        assert len(orchestrator.agent_id) == 36  # UUID length
        assert orchestrator._is_initialized is True
        assert isinstance(orchestrator._active_tasks, dict)
        assert len(orchestrator._active_tasks) == 0
        assert str(orchestrator).startswith("OrchestratorAgent(id=")
        assert "initialized=True" in str(orchestrator)
    
    def test_orchestrator_agent_with_custom_id(self):
        """Test OrchestratorAgent initialization with custom agent ID."""
        # Arrange
        custom_id = "test-agent-123"
        
        # Act
        orchestrator = OrchestratorAgent(agent_id=custom_id)
        
        # Assert
        assert orchestrator.agent_id == custom_id
        assert orchestrator._is_initialized is True
    
    def test_handle_task_expected_use(self):
        """Test handling a valid task - expected use case."""
        # Arrange
        orchestrator = OrchestratorAgent()
        task_def = TaskDefinition(repository_url="https://github.com/example/test-repo.git")
        
        # Act
        execution_id = orchestrator.handle_task(task_def)
        
        # Assert
        assert execution_id is not None
        assert len(execution_id) == 36  # UUID length
        assert task_def.task_id == execution_id
        assert task_def.created_at is not None
        
        # Check task was stored
        task_info = orchestrator.get_task_status(execution_id)
        assert task_info is not None
        assert task_info['status'] == 'in_progress'
        assert task_info['definition'] == task_def
    
    def test_handle_task_edge_case_empty_repository_url(self):
        """Test handling task with empty repository URL - edge case."""
        # Arrange
        orchestrator = OrchestratorAgent()
        task_def = TaskDefinition(repository_url="")
        
        # Act
        execution_id = orchestrator.handle_task(task_def)
        
        # Assert
        assert execution_id is not None
        task_info = orchestrator.get_task_status(execution_id)
        assert task_info is not None
        assert task_info['status'] == 'in_progress'
    
    def test_handle_task_failure_case_not_initialized(self):
        """Test handling task when agent is not initialized - failure case."""
        # Arrange
        orchestrator = OrchestratorAgent()
        orchestrator._is_initialized = False  # Force uninitialized state
        task_def = TaskDefinition(repository_url="https://github.com/example/test-repo.git")
        
        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            orchestrator.handle_task(task_def)
        
        assert "not initialized" in str(exc_info.value)
    
    @patch('orchestrator.orchestrator_agent.OrchestratorAgent._initialize')
    def test_initialization_failure_case(self, mock_initialize):
        """Test agent initialization failure handling."""
        # Arrange
        mock_initialize.side_effect = Exception("Initialization failed")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            OrchestratorAgent()
        
        assert "Initialization failed" in str(exc_info.value)
    
    def test_get_task_status_existing_task(self):
        """Test getting status of existing task."""
        # Arrange
        orchestrator = OrchestratorAgent()
        task_def = TaskDefinition(repository_url="https://github.com/example/test-repo.git")
        execution_id = orchestrator.handle_task(task_def)
        
        # Act
        status = orchestrator.get_task_status(execution_id)
        
        # Assert
        assert status is not None
        assert status['status'] == 'in_progress'
        assert status['definition'] == task_def
        assert 'created_at' in status
    
    def test_get_task_status_nonexistent_task(self):
        """Test getting status of non-existent task."""
        # Arrange
        orchestrator = OrchestratorAgent()
        fake_id = str(uuid.uuid4())
        
        # Act
        status = orchestrator.get_task_status(fake_id)
        
        # Assert
        assert status is None
    
    def test_shutdown_with_active_tasks(self):
        """Test shutdown behavior with active tasks."""
        # Arrange
        orchestrator = OrchestratorAgent()
        task_def1 = TaskDefinition(repository_url="https://github.com/example/test-repo1.git")
        task_def2 = TaskDefinition(repository_url="https://github.com/example/test-repo2.git")
        
        # Add some active tasks
        orchestrator.handle_task(task_def1)
        orchestrator.handle_task(task_def2)
        
        # Act
        orchestrator.shutdown()
        
        # Assert
        assert orchestrator._is_initialized is False
    
    def test_shutdown_no_active_tasks(self):
        """Test shutdown behavior with no active tasks."""
        # Arrange
        orchestrator = OrchestratorAgent()
        
        # Act
        orchestrator.shutdown()
        
        # Assert
        assert orchestrator._is_initialized is False
    
    def test_task_definition_metadata_set_automatically(self):
        """Test that task metadata is set automatically when task_id and created_at are None."""
        # Arrange
        orchestrator = OrchestratorAgent()
        task_def = TaskDefinition(repository_url="https://github.com/example/test-repo.git")
        
        # Verify initial state
        assert task_def.task_id is None
        assert task_def.created_at is None
        
        # Act
        execution_id = orchestrator.handle_task(task_def)
        
        # Assert
        assert task_def.task_id == execution_id
        assert task_def.created_at is not None
    
    def test_task_definition_metadata_preserved_when_set(self):
        """Test that existing task metadata is preserved."""
        # Arrange
        orchestrator = OrchestratorAgent()
        existing_task_id = "existing-task-123"
        from datetime import datetime
        existing_created_at = datetime(2025, 6, 4, 10, 0, 0)
        
        task_def = TaskDefinition(
            repository_url="https://github.com/example/test-repo.git",
            task_id=existing_task_id,
            created_at=existing_created_at
        )
        
        # Act
        execution_id = orchestrator.handle_task(task_def)
        
        # Assert
        assert task_def.task_id == existing_task_id  # Preserved
        assert task_def.created_at == existing_created_at  # Preserved
        assert execution_id != existing_task_id  # Execution ID is different 