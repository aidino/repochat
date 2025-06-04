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
        assert task_info['status'] == 'completed'  # Task 1.3: LanguageIdentifierModule integration
        assert task_info['definition'] == task_def
        
        # Check repository cloning và language identification was attempted
        assert 'repository_path' in task_info  # Should have repository path
        assert 'detected_languages' in task_info  # Should have detected languages
    
    def test_handle_task_edge_case_empty_repository_url(self):
        """Test handling task with empty repository URL - edge case."""
        # Arrange
        orchestrator = OrchestratorAgent()
        task_def = TaskDefinition(repository_url="")
        
        # Act - Should handle error gracefully and continue processing
        execution_id = orchestrator.handle_task(task_def)
        
        # Assert
        assert execution_id is not None
        task_info = orchestrator.get_task_status(execution_id)
        assert task_info['status'] == 'completed'  # Task still completes despite error
        assert len(task_info['errors']) > 0  # Should have recorded the error
        assert task_info['repository_path'] is None  # No repository path due to error
        assert 'detected_languages' in task_info  # Should still have detected_languages field (empty)
    
    def test_handle_task_invalid_repository_url(self):
        """Test handling task with invalid repository URL."""
        # Arrange
        orchestrator = OrchestratorAgent()
        task_def = TaskDefinition(repository_url="not-a-valid-url")
        
        # Act - Should handle error gracefully and continue processing
        execution_id = orchestrator.handle_task(task_def)
        
        # Assert
        assert execution_id is not None
        task_info = orchestrator.get_task_status(execution_id)
        assert task_info['status'] == 'completed'  # Task still completes despite error
        assert len(task_info['errors']) > 0  # Should have recorded the error
        assert task_info['repository_path'] is None  # No repository path due to error
        assert 'detected_languages' in task_info  # Should still have detected_languages field (empty)
    
    @patch('teams.data_acquisition.git_operations_module.GitOperationsModule.clone_repository')
    def test_handle_task_clone_failure_continues_processing(self, mock_clone):
        """Test that clone failures don't stop task processing."""
        # Arrange
        orchestrator = OrchestratorAgent()
        task_def = TaskDefinition(repository_url="https://github.com/example/test-repo.git")
        
        # Setup mock to raise GitCommandError
        from git import GitCommandError
        mock_clone.side_effect = GitCommandError("git clone", 1, "Repository not found")
        
        # Act
        execution_id = orchestrator.handle_task(task_def)
        
        # Assert
        assert execution_id is not None
        task_info = orchestrator.get_task_status(execution_id)
        assert task_info is not None
        assert task_info['status'] == 'completed'  # Task still completes despite clone failure
        assert task_info.get('repository_path') is None  # No repository path due to failure
        assert len(task_info['errors']) > 0  # Should have error logged
    
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
        assert status['status'] == 'completed'  # Task 1.3: LanguageIdentifierModule integration
        assert status['definition'] == task_def
        assert 'created_at' in status
        assert 'repository_path' in status  # Should have repository path info
    
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
    
    def test_orchestrator_has_git_operations_module(self):
        """Test that orchestrator properly initializes GitOperationsModule."""
        # Arrange & Act
        orchestrator = OrchestratorAgent()
        
        # Assert
        assert hasattr(orchestrator, 'git_operations')
        assert orchestrator.git_operations is not None
        from teams.data_acquisition.git_operations_module import GitOperationsModule
        assert isinstance(orchestrator.git_operations, GitOperationsModule)
    
    def test_orchestrator_has_language_identifier_module(self):
        """Test that orchestrator properly initializes LanguageIdentifierModule."""
        # Arrange & Act
        orchestrator = OrchestratorAgent()
        
        # Assert
        assert hasattr(orchestrator, 'language_identifier')
        assert orchestrator.language_identifier is not None
        from teams.data_acquisition.language_identifier_module import LanguageIdentifierModule
        assert isinstance(orchestrator.language_identifier, LanguageIdentifierModule)
    
    def test_get_agent_stats_includes_data_acquisition_modules(self):
        """Test that agent stats reflect TEAM Data Acquisition modules integration."""
        # Arrange
        orchestrator = OrchestratorAgent()
        
        # Act
        stats = orchestrator.get_agent_stats()
        
        # Assert
        assert stats is not None
        assert 'agent_id' in stats
        assert 'is_initialized' in stats
        assert stats['is_initialized'] is True
        # Should be initialized with both GitOperationsModule và LanguageIdentifierModule
    
    @patch('teams.data_acquisition.git_operations_module.GitOperationsModule.__init__')
    def test_initialization_failure_git_operations(self, mock_git_init):
        """Test agent initialization failure when GitOperationsModule fails."""
        # Arrange
        mock_git_init.side_effect = Exception("Git operations initialization failed")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            OrchestratorAgent()
        
        assert "Git operations initialization failed" in str(exc_info.value) 