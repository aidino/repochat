"""
Unit Tests for Task 4.2: PR Review Functionality

Tests the implementation of PR review features including:
- TaskDefinition with PR support
- TaskInitiationModule PR review functionality
- OrchestratorAgent PR handling
- CLI interface PR review command
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from shared.models.task_definition import TaskDefinition, TaskType
from teams.interaction_tasking.task_initiation_module import TaskInitiationModule
from orchestrator.orchestrator_agent import OrchestratorAgent
from teams.interaction_tasking.cli_interface import CLIInterface, cli
from shared.models.project_data_context import ProjectDataContext

from click.testing import CliRunner


class TestTaskDefinitionPRSupport:
    """Test TaskDefinition model with PR support (Task 4.2)."""
    
    def test_task_definition_scan_project_creation(self):
        """Test creating scan project TaskDefinition."""
        task_def = TaskDefinition(
            repository_url="https://github.com/user/repo.git",
            task_type=TaskType.SCAN_PROJECT,
            task_id="test-scan-123"
        )
        
        assert task_def.repository_url == "https://github.com/user/repo.git"
        assert task_def.task_type == TaskType.SCAN_PROJECT
        assert task_def.task_id == "test-scan-123"
        assert task_def.is_project_scan_task()
        assert not task_def.is_pr_review_task()
        assert task_def.pr_id is None
        assert task_def.pr_url is None
        assert task_def.get_pr_identifier() is None
    
    def test_task_definition_pr_review_with_id(self):
        """Test creating PR review TaskDefinition with PR ID."""
        task_def = TaskDefinition(
            repository_url="https://github.com/user/repo.git",
            task_type=TaskType.REVIEW_PR,
            pr_id="123",
            task_id="test-pr-123"
        )
        
        assert task_def.repository_url == "https://github.com/user/repo.git"
        assert task_def.task_type == TaskType.REVIEW_PR
        assert task_def.pr_id == "123"
        assert task_def.pr_url is None
        assert task_def.is_pr_review_task()
        assert not task_def.is_project_scan_task()
        assert task_def.get_pr_identifier() == "123"
    
    def test_task_definition_pr_review_with_url(self):
        """Test creating PR review TaskDefinition with PR URL."""
        pr_url = "https://github.com/user/repo/pull/456"
        task_def = TaskDefinition(
            repository_url="https://github.com/user/repo.git",
            task_type=TaskType.REVIEW_PR,
            pr_url=pr_url,
            task_id="test-pr-456"
        )
        
        assert task_def.repository_url == "https://github.com/user/repo.git"
        assert task_def.task_type == TaskType.REVIEW_PR
        assert task_def.pr_id is None
        assert task_def.pr_url == pr_url
        assert task_def.is_pr_review_task()
        assert task_def.get_pr_identifier() == "456"  # Extracted from URL
    
    def test_task_definition_pr_url_extraction_github(self):
        """Test PR ID extraction from GitHub URLs."""
        task_def = TaskDefinition(
            repository_url="https://github.com/user/repo.git",
            task_type=TaskType.REVIEW_PR,
            pr_url="https://github.com/user/repo/pull/789"
        )
        
        assert task_def.get_pr_identifier() == "789"
    
    def test_task_definition_pr_url_extraction_gitlab(self):
        """Test PR ID extraction from GitLab URLs."""
        task_def = TaskDefinition(
            repository_url="https://gitlab.com/user/repo.git",
            task_type=TaskType.REVIEW_PR,
            pr_url="https://gitlab.com/user/repo/-/merge_requests/101"
        )
        
        assert task_def.get_pr_identifier() == "101"
    
    def test_task_definition_pr_validation_error(self):
        """Test validation error when PR info is missing for review_pr task."""
        with pytest.raises(ValueError, match="Either pr_id or pr_url must be provided"):
            TaskDefinition(
                repository_url="https://github.com/user/repo.git",
                task_type=TaskType.REVIEW_PR
            )
    
    def test_task_definition_string_representation(self):
        """Test string representation for different task types."""
        # Scan project
        scan_task = TaskDefinition(
            repository_url="https://github.com/user/repo.git",
            task_type=TaskType.SCAN_PROJECT,
            task_id="scan-123"
        )
        assert "type=scan_project" in str(scan_task)
        assert "repo=https://github.com/user/repo.git" in str(scan_task)
        
        # PR review
        pr_task = TaskDefinition(
            repository_url="https://github.com/user/repo.git",
            task_type=TaskType.REVIEW_PR,
            pr_id="456",
            task_id="pr-456"
        )
        assert "type=review_pr" in str(pr_task)
        assert "pr=456" in str(pr_task)


class TestTaskInitiationModulePRReview:
    """Test TaskInitiationModule PR review functionality (Task 4.2)."""
    
    def setUp(self):
        self.task_initiation = TaskInitiationModule()
    
    def test_create_review_pr_task_with_id(self):
        """Test creating PR review task with PR ID."""
        self.setUp()
        repository_url = "https://github.com/user/repo.git"
        pr_id = "123"
        
        task_def = self.task_initiation.create_review_pr_task(repository_url, pr_id)
        
        assert task_def.repository_url == repository_url
        assert task_def.task_type == TaskType.REVIEW_PR
        assert task_def.pr_id == pr_id
        assert task_def.pr_url is None
        assert task_def.get_pr_identifier() == pr_id
        assert task_def.task_id is not None
        assert task_def.task_id.startswith("review-pr-")
    
    def test_create_review_pr_task_with_url(self):
        """Test creating PR review task with PR URL."""
        self.setUp()
        repository_url = "https://github.com/user/repo.git"
        pr_url = "https://github.com/user/repo/pull/456"
        
        task_def = self.task_initiation.create_review_pr_task(repository_url, pr_url)
        
        assert task_def.repository_url == repository_url
        assert task_def.task_type == TaskType.REVIEW_PR
        assert task_def.pr_id is None
        assert task_def.pr_url == pr_url
        assert task_def.get_pr_identifier() == "456"
    
    def test_create_review_pr_task_validation_errors(self):
        """Test validation errors in PR review task creation."""
        self.setUp()
        
        # Empty repository URL
        with pytest.raises(ValueError, match="Repository URL cannot be empty"):
            self.task_initiation.create_review_pr_task("", "123")
        
        # Empty PR identifier
        with pytest.raises(ValueError, match="PR identifier cannot be empty"):
            self.task_initiation.create_review_pr_task("https://github.com/user/repo.git", "")
        
        # Invalid repository URL
        with pytest.raises(ValueError, match="Invalid repository URL format"):
            self.task_initiation.create_review_pr_task("invalid-url", "123")
    
    def test_validate_pr_identifier(self):
        """Test PR identifier validation."""
        self.setUp()
        
        # Valid numeric ID
        assert self.task_initiation.validate_pr_identifier("123")
        
        # Valid GitHub URL
        assert self.task_initiation.validate_pr_identifier("https://github.com/user/repo/pull/456")
        
        # Valid GitLab URL
        assert self.task_initiation.validate_pr_identifier("https://gitlab.com/user/repo/-/merge_requests/789")
        
        # Invalid cases
        assert not self.task_initiation.validate_pr_identifier("")
        assert not self.task_initiation.validate_pr_identifier("invalid")
        assert not self.task_initiation.validate_pr_identifier("https://invalid-url")
    
    def test_is_pr_url_detection(self):
        """Test PR URL detection."""
        self.setUp()
        
        # GitHub URL
        assert self.task_initiation._is_pr_url("https://github.com/user/repo/pull/123")
        
        # GitLab URL
        assert self.task_initiation._is_pr_url("https://gitlab.com/user/repo/-/merge_requests/456")
        
        # Not PR URLs
        assert not self.task_initiation._is_pr_url("123")
        assert not self.task_initiation._is_pr_url("https://github.com/user/repo")
        assert not self.task_initiation._is_pr_url("invalid")
    
    def test_module_stats_updated(self):
        """Test module stats reflect Task 4.2 updates."""
        self.setUp()
        stats = self.task_initiation.get_module_stats()
        
        assert stats['version'] == '1.0.1'
        assert 'scan_project' in stats['supported_tasks']
        assert 'review_pr' in stats['supported_tasks']
        assert stats['features']['pr_url_parsing'] is True
        assert stats['features']['pr_id_extraction'] is True
        assert TaskType.SCAN_PROJECT.value in stats['task_types']
        assert TaskType.REVIEW_PR.value in stats['task_types']


class TestOrchestratorAgentPRReview:
    """Test OrchestratorAgent PR review handling (Task 4.2)."""
    
    @patch('orchestrator.orchestrator_agent.GitOperationsModule')
    @patch('orchestrator.orchestrator_agent.LanguageIdentifierModule')
    @patch('orchestrator.orchestrator_agent.DataPreparationModule')
    @patch('orchestrator.orchestrator_agent.PATHandlerModule')
    @patch('orchestrator.orchestrator_agent.TeamCKGOperationsFacade')
    @patch('orchestrator.orchestrator_agent.TeamLLMServices')
    def test_handle_review_pr_task(self, mock_llm, mock_ckg, mock_pat, mock_data_prep, mock_lang_id, mock_git):
        """Test PR review task handling in OrchestratorAgent."""
        # Setup mocks
        mock_git_instance = Mock()
        mock_git.return_value = mock_git_instance
        mock_git_instance.clone_repository.return_value = "/tmp/test_repo"
        
        mock_lang_instance = Mock()
        mock_lang_id.return_value = mock_lang_instance
        mock_lang_instance.identify_languages.return_value = ["python", "javascript"]
        
        mock_data_instance = Mock()
        mock_data_prep.return_value = mock_data_instance
        mock_project_context = ProjectDataContext(
            repository_url="https://github.com/user/repo.git",
            cloned_code_path="/tmp/test_repo",
            detected_languages=["python", "javascript"],
            primary_language="python",
            language_count=2,
            has_languages=True
        )
        mock_data_instance.create_project_context.return_value = mock_project_context
        
        mock_pat_instance = Mock()
        mock_pat.return_value = mock_pat_instance
        mock_pat_instance.request_pat_if_needed.return_value = None
        
        # Create orchestrator and initialize
        orchestrator = OrchestratorAgent()
        orchestrator._initialize()
        
        # Create PR review task
        pr_task = TaskDefinition(
            repository_url="https://github.com/user/repo.git",
            task_type=TaskType.REVIEW_PR,
            pr_id="123",
            task_id="test-pr-123"
        )
        
        # Execute PR review
        result = orchestrator.handle_review_pr_task(pr_task)
        
        # Verify result
        assert result == mock_project_context
        assert result.repository_url == "https://github.com/user/repo.git"
        assert result.detected_languages == ["python", "javascript"]
        
        # Verify method calls
        mock_git_instance.clone_repository.assert_called_once()
        mock_lang_instance.identify_languages.assert_called_once_with(repository_path="/tmp/test_repo")
        mock_data_instance.create_project_context.assert_called_once()
    
    def test_handle_review_pr_task_validation_errors(self):
        """Test validation errors in PR review task handling."""
        orchestrator = OrchestratorAgent()
        orchestrator._initialize()
        
        # Non-PR review task
        scan_task = TaskDefinition(
            repository_url="https://github.com/user/repo.git",
            task_type=TaskType.SCAN_PROJECT,
            task_id="scan-123"
        )
        
        with pytest.raises(ValueError, match="Task definition is not a PR review task"):
            orchestrator.handle_review_pr_task(scan_task)
        
        # PR task without PR identifier - should fail at creation level now
        with pytest.raises(ValueError, match="Either pr_id or pr_url must be provided"):
            invalid_pr_task = TaskDefinition(
                repository_url="https://github.com/user/repo.git",
                task_type=TaskType.REVIEW_PR,
                task_id="invalid-pr"
            )


class TestCLIInterfacePRReview:
    """Test CLI interface PR review functionality (Task 4.2)."""
    
    def setUp(self):
        self.runner = CliRunner()
    
    @patch('teams.interaction_tasking.cli_interface.OrchestratorAgent')
    @patch('teams.interaction_tasking.cli_interface.TaskInitiationModule')
    def test_execute_review_pr_success(self, mock_task_init_class, mock_orchestrator_class):
        """Test successful PR review execution."""
        # Setup mocks
        mock_task_init = Mock()
        mock_task_init_class.return_value = mock_task_init
        
        mock_pr_task = TaskDefinition(
            repository_url="https://github.com/user/repo.git",
            task_type=TaskType.REVIEW_PR,
            pr_id="123",
            task_id="test-pr-123"
        )
        mock_task_init.create_review_pr_task.return_value = mock_pr_task
        
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_project_context = ProjectDataContext(
            repository_url="https://github.com/user/repo.git",
            cloned_code_path="/tmp/test_repo",
            detected_languages=["python"],
            primary_language="python",
            language_count=1,
            has_languages=True
        )
        mock_orchestrator.handle_review_pr_task.return_value = mock_project_context
        
        # Create CLI interface and execute
        cli_interface = CLIInterface()
        result = cli_interface.execute_review_pr("https://github.com/user/repo.git", "123", verbose=False)
        
        # Verify success
        assert result['status'] == 'success'
        assert result['pr_identifier'] == "123"
        assert 'execution_time' in result
        assert result['task_definition'] == mock_pr_task
        
        # Verify method calls
        mock_task_init.create_review_pr_task.assert_called_once_with("https://github.com/user/repo.git", "123")
        mock_orchestrator.handle_review_pr_task.assert_called_once_with(mock_pr_task)
    
    def test_review_pr_cli_command(self):
        """Test review-pr CLI command."""
        self.setUp()
        
        with patch('teams.interaction_tasking.cli_interface.CLIInterface') as mock_cli_class:
            mock_cli = Mock()
            mock_cli_class.return_value = mock_cli
            mock_cli.execute_review_pr.return_value = {'status': 'success'}
            
            result = self.runner.invoke(cli, [
                'review-pr',
                'https://github.com/user/repo.git',
                '123'
            ])
            
            assert result.exit_code == 0
            mock_cli.execute_review_pr.assert_called_once()
    
    def test_review_pr_cli_help(self):
        """Test review-pr command help."""
        self.setUp()
        result = self.runner.invoke(cli, ['review-pr', '--help'])
        
        assert result.exit_code == 0
        assert "Review và phân tích một Pull Request" in result.output
        assert "REPOSITORY_URL" in result.output
        assert "PR_IDENTIFIER" in result.output


class TestIntegrationPRReview:
    """Integration tests for PR review functionality."""
    
    def setUp(self):
        self.runner = CliRunner()
    
    @patch('teams.interaction_tasking.cli_interface.OrchestratorAgent')
    @patch('teams.interaction_tasking.cli_interface.TaskInitiationModule')
    def test_end_to_end_pr_review(self, mock_task_init_class, mock_orchestrator_class):
        """Test end-to-end PR review workflow."""
        self.setUp()
        
        # Setup task initiation mock
        mock_task_init = Mock()
        mock_task_init_class.return_value = mock_task_init
        
        mock_pr_task = TaskDefinition(
            repository_url="https://github.com/user/repo.git",
            task_type=TaskType.REVIEW_PR,
            pr_id="456",
            task_id="test-pr-456"
        )
        mock_task_init.create_review_pr_task.return_value = mock_pr_task
        
        # Setup orchestrator mock
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_project_context = ProjectDataContext(
            repository_url="https://github.com/user/repo.git",
            cloned_code_path="/tmp/test_repo",
            detected_languages=["java", "python"],
            primary_language="java",
            language_count=2,
            has_languages=True
        )
        mock_orchestrator.handle_review_pr_task.return_value = mock_project_context
        mock_orchestrator.get_agent_stats.return_value = {
            'statistics': {'successful_tasks': 1},
            'uptime_seconds': 5.2
        }
        
        # Execute CLI command
        result = self.runner.invoke(cli, [
            'review-pr',
            'https://github.com/user/repo.git',
            '456',
            '--verbose'
        ])
        
        # Debug output if failed
        if result.exit_code != 0:
            print(f"CLI failed with exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
        
        # Verify success
        assert result.exit_code == 0
        assert "Review Pull Request hoàn thành thành công" in result.output
        assert "Pull Request: #456" in result.output
        
        # Verify method calls
        mock_task_init.create_review_pr_task.assert_called_once_with("https://github.com/user/repo.git", "456")
        mock_orchestrator.handle_review_pr_task.assert_called_once_with(mock_pr_task)


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 