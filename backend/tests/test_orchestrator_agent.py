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
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition
from shared.models.project_data_context import ProjectDataContext


class TestOrchestratorAgent:
    """Test suite for OrchestratorAgent class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = OrchestratorAgent()
        
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'agent'):
            try:
                self.agent.shutdown()
            except:
                pass  # Ignore shutdown errors in tests

    def test_orchestrator_agent_initialization_expected_use(self):
        """Test normal OrchestratorAgent initialization."""
        # Act
        assert self.agent.agent_id is not None
        assert len(self.agent.agent_id) == 36  # UUID length
        assert self.agent._is_initialized is True
        assert isinstance(self.agent._active_tasks, dict)
        assert len(self.agent._active_tasks) == 0
        assert str(self.agent).startswith("OrchestratorAgent(id=")
        assert "initialized=True" in str(self.agent)
    
    def test_orchestrator_agent_with_custom_id(self):
        """Test OrchestratorAgent initialization with custom agent ID."""
        # Arrange
        custom_id = "test-agent-123"
        
        # Act
        agent = OrchestratorAgent(agent_id=custom_id)
        
        # Assert
        assert agent.agent_id == custom_id
        assert agent._is_initialized is True
    
    def test_handle_task_expected_use(self):
        """Test handling a valid task - expected use case."""
        # Arrange
        task_def = TaskDefinition(repository_url="https://github.com/example/test-repo.git")
        
        # Act
        execution_id = self.agent.handle_task(task_def)
        
        # Assert
        assert execution_id is not None
        assert len(execution_id) == 36  # UUID length
        assert task_def.task_id == execution_id
        assert task_def.created_at is not None
        
        # Check task was stored
        task_info = self.agent.get_task_status(execution_id)
        assert task_info is not None
        assert task_info['status'] == 'completed'  # Task 1.3: LanguageIdentifierModule integration
        assert task_info['definition'] == task_def
        
        # Check repository cloning và language identification was attempted
        assert 'repository_path' in task_info  # Should have repository path
        assert 'detected_languages' in task_info  # Should have detected languages
    
    def test_handle_task_edge_case_empty_repository_url(self):
        """Test handling task with empty repository URL - edge case."""
        # Arrange
        task_def = TaskDefinition(repository_url="")
        
        # Act - Should handle error gracefully and continue processing
        execution_id = self.agent.handle_task(task_def)
        
        # Assert
        assert execution_id is not None
        task_info = self.agent.get_task_status(execution_id)
        assert task_info['status'] == 'completed'  # Task still completes despite error
        assert len(task_info['errors']) > 0  # Should have recorded the error
        assert task_info['repository_path'] is None  # No repository path due to error
        assert 'detected_languages' in task_info  # Should still have detected_languages field (empty)
    
    def test_handle_task_invalid_repository_url(self):
        """Test handling task with invalid repository URL."""
        # Arrange
        task_def = TaskDefinition(repository_url="not-a-valid-url")
        
        # Act - Should handle error gracefully and continue processing
        execution_id = self.agent.handle_task(task_def)
        
        # Assert
        assert execution_id is not None
        task_info = self.agent.get_task_status(execution_id)
        assert task_info['status'] == 'completed'  # Task still completes despite error
        assert len(task_info['errors']) > 0  # Should have recorded the error
        assert task_info['repository_path'] is None  # No repository path due to error
        assert 'detected_languages' in task_info  # Should still have detected_languages field (empty)
    
    @patch('teams.data_acquisition.git_operations_module.GitOperationsModule.clone_repository')
    def test_handle_task_clone_failure_continues_processing(self, mock_clone):
        """Test that clone failures don't stop task processing."""
        # Arrange
        task_def = TaskDefinition(repository_url="https://github.com/example/test-repo.git")
        
        # Setup mock to raise GitCommandError
        from git import GitCommandError
        mock_clone.side_effect = GitCommandError("git clone", 1, "Repository not found")
        
        # Act
        execution_id = self.agent.handle_task(task_def)
        
        # Assert
        assert execution_id is not None
        task_info = self.agent.get_task_status(execution_id)
        assert task_info is not None
        assert task_info['status'] == 'completed'  # Task still completes despite clone failure
        assert task_info.get('repository_path') is None  # No repository path due to failure
        assert len(task_info['errors']) > 0  # Should have error logged
    
    def test_handle_task_failure_case_not_initialized(self):
        """Test handling task when agent is not initialized - failure case."""
        # Arrange
        self.agent._is_initialized = False  # Force uninitialized state
        task_def = TaskDefinition(repository_url="https://github.com/example/test-repo.git")
        
        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            self.agent.handle_task(task_def)
        
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
        task_def = TaskDefinition(repository_url="https://github.com/example/test-repo.git")
        execution_id = self.agent.handle_task(task_def)
        
        # Act
        status = self.agent.get_task_status(execution_id)
        
        # Assert
        assert status is not None
        assert status['status'] == 'completed'  # Task 1.3: LanguageIdentifierModule integration
        assert status['definition'] == task_def
        assert 'created_at' in status
        assert 'repository_path' in status  # Should have repository path info
    
    def test_get_task_status_nonexistent_task(self):
        """Test getting status of non-existent task."""
        # Arrange
        fake_id = str(uuid.uuid4())
        
        # Act
        status = self.agent.get_task_status(fake_id)
        
        # Assert
        assert status is None
    
    def test_shutdown_with_active_tasks(self):
        """Test shutdown behavior with active tasks."""
        # Arrange
        task_def1 = TaskDefinition(repository_url="https://github.com/example/test-repo1.git")
        task_def2 = TaskDefinition(repository_url="https://github.com/example/test-repo2.git")
        
        # Add some active tasks
        self.agent.handle_task(task_def1)
        self.agent.handle_task(task_def2)
        
        # Act
        self.agent.shutdown()
        
        # Assert
        assert self.agent._is_initialized is False
    
    def test_shutdown_no_active_tasks(self):
        """Test shutdown behavior with no active tasks."""
        # Arrange
        # Act
        self.agent.shutdown()
        
        # Assert
        assert self.agent._is_initialized is False
    
    def test_task_definition_metadata_set_automatically(self):
        """Test that task metadata is set automatically when task_id and created_at are None."""
        # Arrange
        task_def = TaskDefinition(repository_url="https://github.com/example/test-repo.git")
        
        # Verify initial state
        assert task_def.task_id is None
        assert task_def.created_at is None
        
        # Act
        execution_id = self.agent.handle_task(task_def)
        
        # Assert
        assert task_def.task_id == execution_id
        assert task_def.created_at is not None
    
    def test_task_definition_metadata_preserved_when_set(self):
        """Test that existing task metadata is preserved."""
        # Arrange
        existing_task_id = "existing-task-123"
        existing_created_at = datetime(2025, 6, 4, 10, 0, 0)
        
        task_def = TaskDefinition(
            repository_url="https://github.com/example/test-repo.git",
            task_id=existing_task_id,
            created_at=existing_created_at
        )
        
        # Act
        execution_id = self.agent.handle_task(task_def)
        
        # Assert
        assert task_def.task_id == existing_task_id  # Preserved
        assert task_def.created_at == existing_created_at  # Preserved
        assert execution_id != existing_task_id  # Execution ID is different
    
    def test_orchestrator_has_git_operations_module(self):
        """Test that orchestrator properly initializes GitOperationsModule."""
        # Arrange & Act
        assert hasattr(self.agent, 'git_operations')
        assert self.agent.git_operations is not None
        from teams.data_acquisition.git_operations_module import GitOperationsModule
        assert isinstance(self.agent.git_operations, GitOperationsModule)
    
    def test_orchestrator_has_language_identifier_module(self):
        """Test that orchestrator properly initializes LanguageIdentifierModule."""
        # Arrange & Act
        assert hasattr(self.agent, 'language_identifier')
        assert self.agent.language_identifier is not None
        from teams.data_acquisition.language_identifier_module import LanguageIdentifierModule
        assert isinstance(self.agent.language_identifier, LanguageIdentifierModule)
    
    def test_get_agent_stats_includes_data_acquisition_modules(self):
        """Test that agent stats reflect TEAM Data Acquisition modules integration."""
        # Arrange
        # Act
        stats = self.agent.get_agent_stats()
        
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
    
    def test_handle_scan_project_task_success(self):
        """Test successful scan project task execution."""
        task_def = TaskDefinition(repository_url="https://github.com/octocat/Hello-World.git")
        
        with patch.object(self.agent.pat_handler, 'request_pat_if_needed') as mock_pat, \
             patch.object(self.agent.git_operations, 'clone_repository') as mock_clone, \
             patch.object(self.agent.language_identifier, 'identify_languages') as mock_lang, \
             patch.object(self.agent.data_preparation, 'create_project_context') as mock_data_prep, \
             patch.object(self.agent.pat_handler, 'clear_pat_cache') as mock_clear:
            
            # Setup mocks
            mock_pat.return_value = None  # Public repo, no PAT needed
            mock_clone.return_value = "/tmp/test_repo_path"
            mock_lang.return_value = ["python", "javascript"]
            
            mock_context = ProjectDataContext(
                cloned_code_path="/tmp/test_repo_path",
                detected_languages=["python", "javascript"],
                repository_url=task_def.repository_url
            )
            mock_data_prep.return_value = mock_context
            
            # Execute
            result = self.agent.handle_scan_project_task(task_def)
            
            # Verify
            assert isinstance(result, ProjectDataContext)
            assert result.cloned_code_path == "/tmp/test_repo_path"
            assert result.detected_languages == ["python", "javascript"]
            assert result.repository_url == task_def.repository_url
            
            # Verify method calls
            mock_pat.assert_called_once_with(task_def.repository_url)
            mock_clone.assert_called_once_with(
                repository_url=task_def.repository_url,
                pat=None
            )
            mock_lang.assert_called_once_with(repository_path="/tmp/test_repo_path")
            mock_data_prep.assert_called_once_with(
                cloned_code_path="/tmp/test_repo_path",
                detected_languages=["python", "javascript"],
                repository_url=task_def.repository_url
            )
            # PAT cache should not be cleared for public repos (no PAT)
            mock_clear.assert_not_called()
    
    def test_handle_scan_project_task_with_pat(self):
        """Test scan project task with private repository requiring PAT."""
        task_def = TaskDefinition(repository_url="https://github.private.company.com/team/repo.git")
        
        with patch.object(self.agent.pat_handler, 'request_pat_if_needed') as mock_pat, \
             patch.object(self.agent.git_operations, 'clone_repository') as mock_clone, \
             patch.object(self.agent.language_identifier, 'identify_languages') as mock_lang, \
             patch.object(self.agent.data_preparation, 'create_project_context') as mock_data_prep, \
             patch.object(self.agent.pat_handler, 'clear_pat_cache') as mock_clear:
            
            # Setup mocks
            test_pat = "ghp_test_token_12345"
            mock_pat.return_value = test_pat
            mock_clone.return_value = "/tmp/private_repo_path"
            mock_lang.return_value = ["java", "kotlin"]
            
            mock_context = ProjectDataContext(
                cloned_code_path="/tmp/private_repo_path",
                detected_languages=["java", "kotlin"],
                repository_url=task_def.repository_url
            )
            mock_data_prep.return_value = mock_context
            
            # Execute
            result = self.agent.handle_scan_project_task(task_def)
            
            # Verify
            assert isinstance(result, ProjectDataContext)
            assert result.cloned_code_path == "/tmp/private_repo_path"
            assert result.detected_languages == ["java", "kotlin"]
            
            # Verify PAT was used
            mock_clone.assert_called_once_with(
                repository_url=task_def.repository_url,
                pat=test_pat
            )
            
            # Verify PAT cache was cleared for security
            mock_clear.assert_called_once()
    
    def test_handle_scan_project_task_not_initialized(self):
        """Test scan project task fails when agent not initialized."""
        agent = OrchestratorAgent()
        agent._is_initialized = False
        
        task_def = TaskDefinition(repository_url="https://github.com/test/repo.git")
        
        with pytest.raises(RuntimeError, match="not initialized"):
            agent.handle_scan_project_task(task_def)
        
        agent.shutdown()
    
    def test_handle_scan_project_task_clone_failure(self):
        """Test scan project task handles clone failure gracefully."""
        task_def = TaskDefinition(repository_url="https://github.com/nonexistent/repo.git")
        
        with patch.object(self.agent.pat_handler, 'request_pat_if_needed') as mock_pat, \
             patch.object(self.agent.git_operations, 'clone_repository') as mock_clone, \
             patch.object(self.agent.pat_handler, 'clear_pat_cache') as mock_clear:
            
            mock_pat.return_value = None
            mock_clone.side_effect = Exception("Repository not found")
            
            with pytest.raises(Exception, match="Repository not found"):
                self.agent.handle_scan_project_task(task_def)
            
            # PAT cache should still be cleared on error
            mock_clear.assert_not_called()  # No PAT was provided
    
    def test_handle_scan_project_task_with_pat_error_clears_cache(self):
        """Test that PAT cache is cleared even when error occurs."""
        task_def = TaskDefinition(repository_url="https://github.private.company.com/team/repo.git")
        
        with patch.object(self.agent.pat_handler, 'request_pat_if_needed') as mock_pat, \
             patch.object(self.agent.git_operations, 'clone_repository') as mock_clone, \
             patch.object(self.agent.pat_handler, 'clear_pat_cache') as mock_clear:
            
            test_pat = "ghp_test_token_12345"
            mock_pat.return_value = test_pat
            mock_clone.side_effect = Exception("Clone failed")
            
            with pytest.raises(Exception, match="Clone failed"):
                self.agent.handle_scan_project_task(task_def)
            
            # PAT cache should be cleared even on error
            mock_clear.assert_called_once()
    
    def test_handle_scan_project_task_language_identification_failure(self):
        """Test scan project task handles language identification failure."""
        task_def = TaskDefinition(repository_url="https://github.com/test/repo.git")
        
        with patch.object(self.agent.pat_handler, 'request_pat_if_needed') as mock_pat, \
             patch.object(self.agent.git_operations, 'clone_repository') as mock_clone, \
             patch.object(self.agent.language_identifier, 'identify_languages') as mock_lang:
            
            mock_pat.return_value = None
            mock_clone.return_value = "/tmp/test_repo"
            mock_lang.side_effect = Exception("Language identification failed")
            
            with pytest.raises(Exception, match="Language identification failed"):
                self.agent.handle_scan_project_task(task_def)
    
    def test_handle_scan_project_task_data_preparation_failure(self):
        """Test scan project task handles data preparation failure."""
        task_def = TaskDefinition(repository_url="https://github.com/test/repo.git")
        
        with patch.object(self.agent.pat_handler, 'request_pat_if_needed') as mock_pat, \
             patch.object(self.agent.git_operations, 'clone_repository') as mock_clone, \
             patch.object(self.agent.language_identifier, 'identify_languages') as mock_lang, \
             patch.object(self.agent.data_preparation, 'create_project_context') as mock_data_prep:
            
            mock_pat.return_value = None
            mock_clone.return_value = "/tmp/test_repo"
            mock_lang.return_value = ["python"]
            mock_data_prep.side_effect = Exception("Data preparation failed")
            
            with pytest.raises(Exception, match="Data preparation failed"):
                self.agent.handle_scan_project_task(task_def)
    
    def test_handle_scan_project_task_comprehensive_logging(self):
        """Test that scan project task logs all steps properly."""
        task_def = TaskDefinition(repository_url="https://github.com/octocat/Hello-World.git")
        
        with patch.object(self.agent.pat_handler, 'request_pat_if_needed') as mock_pat, \
             patch.object(self.agent.git_operations, 'clone_repository') as mock_clone, \
             patch.object(self.agent.language_identifier, 'identify_languages') as mock_lang, \
             patch.object(self.agent.data_preparation, 'create_project_context') as mock_data_prep:
            
            mock_pat.return_value = None
            mock_clone.return_value = "/tmp/test_repo"
            mock_lang.return_value = ["python", "javascript"]
            
            mock_context = ProjectDataContext(
                cloned_code_path="/tmp/test_repo",
                detected_languages=["python", "javascript"],
                repository_url=task_def.repository_url
            )
            mock_data_prep.return_value = mock_context
            
            with patch.object(self.agent.logger, 'info') as mock_log_info:
                result = self.agent.handle_scan_project_task(task_def)
                
                # Verify logging calls were made for each step
                log_calls = [call.args[0] for call in mock_log_info.call_args_list]
                
                assert any("Starting scan project task" in call for call in log_calls)
                assert any("Step 1: Checking PAT requirements" in call for call in log_calls)
                assert any("Step 2: Cloning repository" in call for call in log_calls)
                assert any("Step 3: Identifying programming languages" in call for call in log_calls)
                assert any("Step 4: Creating ProjectDataContext" in call for call in log_calls)
                assert any("ProjectDataContext created successfully" in call for call in log_calls)
                assert any("Scan project task completed successfully" in call for call in log_calls)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 