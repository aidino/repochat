"""
Unit Tests for Task 4.1: CLI Interface

Tests for TEAM Interaction & Tasking CLI implementation.
Covers TaskInitiationModule and CLIInterface functionality.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from click.testing import CliRunner

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from teams.interaction_tasking.task_initiation_module import TaskInitiationModule
from teams.interaction_tasking.cli_interface import CLIInterface, cli
from shared.models.task_definition import TaskDefinition
from shared.models.project_data_context import ProjectDataContext


class TestTaskInitiationModule:
    """Test cases for TaskInitiationModule."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.task_initiation = TaskInitiationModule()
    
    def test_create_scan_project_task_success(self):
        """Test successful creation of scan project task."""
        repository_url = "https://github.com/user/repo.git"
        
        task_def = self.task_initiation.create_scan_project_task(repository_url)
        
        assert isinstance(task_def, TaskDefinition)
        assert task_def.repository_url == repository_url
        assert task_def.task_id is not None
        assert task_def.task_id.startswith("scan-project-")
        assert task_def.created_at is not None
        assert isinstance(task_def.created_at, datetime)
    
    def test_create_scan_project_task_with_custom_id(self):
        """Test creation with custom task ID."""
        repository_url = "https://github.com/user/repo.git"
        custom_id = "custom-task-123"
        
        task_def = self.task_initiation.create_scan_project_task(repository_url, custom_id)
        
        assert task_def.task_id == custom_id
        assert task_def.repository_url == repository_url
    
    def test_create_scan_project_task_empty_url(self):
        """Test error handling for empty repository URL."""
        with pytest.raises(ValueError, match="Repository URL cannot be empty"):
            self.task_initiation.create_scan_project_task("")
        
        with pytest.raises(ValueError, match="Repository URL cannot be empty"):
            self.task_initiation.create_scan_project_task("   ")
    
    def test_create_scan_project_task_invalid_url_format(self):
        """Test error handling for invalid URL format."""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com/repo.git",
            "just-text",
            "http:/",  # Malformed
        ]
        
        for invalid_url in invalid_urls:
            with pytest.raises(ValueError, match="Invalid repository URL format"):
                self.task_initiation.create_scan_project_task(invalid_url)
    
    def test_create_scan_project_task_valid_url_formats(self):
        """Test acceptance of various valid URL formats."""
        valid_urls = [
            "https://github.com/user/repo.git",
            "http://gitlab.com/user/repo.git",
            "git@github.com:user/repo.git",
            "https://bitbucket.org/user/repo.git"
        ]
        
        for valid_url in valid_urls:
            task_def = self.task_initiation.create_scan_project_task(valid_url)
            assert task_def.repository_url == valid_url
    
    def test_create_review_pr_task_placeholder(self):
        """Test PR review task creation (placeholder functionality)."""
        repository_url = "https://github.com/user/repo.git"
        pr_id = "123"
        
        task_def = self.task_initiation.create_review_pr_task(repository_url, pr_id)
        
        assert isinstance(task_def, TaskDefinition)
        assert task_def.repository_url == repository_url
        assert task_def.task_id.startswith("review-pr-")
        assert task_def.created_at is not None
    
    def test_create_review_pr_task_empty_inputs(self):
        """Test PR review task with empty inputs."""
        with pytest.raises(ValueError, match="Repository URL cannot be empty"):
            self.task_initiation.create_review_pr_task("", "123")
        
        with pytest.raises(ValueError, match="PR ID cannot be empty"):
            self.task_initiation.create_review_pr_task("https://github.com/user/repo.git", "")
    
    def test_validate_repository_url(self):
        """Test repository URL validation method."""
        # Valid URLs
        assert self.task_initiation.validate_repository_url("https://github.com/user/repo.git")
        assert self.task_initiation.validate_repository_url("http://gitlab.com/user/repo.git")
        assert self.task_initiation.validate_repository_url("git@github.com:user/repo.git")
        
        # Invalid URLs
        assert not self.task_initiation.validate_repository_url("")
        assert not self.task_initiation.validate_repository_url("   ")
        assert not self.task_initiation.validate_repository_url("not-a-url")
        assert not self.task_initiation.validate_repository_url("ftp://example.com/repo.git")
    
    def test_get_module_stats(self):
        """Test module statistics retrieval."""
        stats = self.task_initiation.get_module_stats()
        
        assert stats['module'] == 'TaskInitiationModule'
        assert stats['version'] == '1.0.0'
        assert 'scan_project' in stats['supported_tasks']
        assert 'review_pr_placeholder' in stats['supported_tasks']
        assert stats['features']['url_validation'] is True
        assert stats['features']['task_id_generation'] is True
        assert stats['features']['llm_config_integration'] is False


class TestCLIInterface:
    """Test cases for CLIInterface."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.cli_interface = CLIInterface()
    
    @patch('teams.interaction_tasking.cli_interface.OrchestratorAgent')
    def test_scan_project_command_success(self, mock_orchestrator_class):
        """Test successful scan project command execution."""
        # Mock orchestrator and its methods
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Mock project context result
        mock_project_context = ProjectDataContext(
            repository_url="https://github.com/user/repo.git",
            cloned_code_path="/tmp/test_repo",
            detected_languages=["java", "python"],
            primary_language="java",
            language_count=2,
            has_languages=True
        )
        mock_orchestrator.handle_scan_project_task.return_value = mock_project_context
        mock_orchestrator.get_agent_stats.return_value = {
            'statistics': {'successful_tasks': 1},
            'uptime_seconds': 5.0
        }
        
        # Execute command
        result = self.cli_interface.scan_project_command(
            "https://github.com/user/repo.git", 
            verbose=True
        )
        
        # Verify results
        assert result is not None
        assert result.repository_url == "https://github.com/user/repo.git"
        assert result.primary_language == "java"
        assert len(result.detected_languages) == 2
        
        # Verify orchestrator was called correctly
        mock_orchestrator_class.assert_called_once()
        mock_orchestrator.handle_scan_project_task.assert_called_once()
        mock_orchestrator.shutdown.assert_called_once()
    
    @patch('teams.interaction_tasking.cli_interface.OrchestratorAgent')
    def test_scan_project_command_orchestrator_error(self, mock_orchestrator_class):
        """Test scan project command with orchestrator error."""
        # Mock orchestrator to raise exception
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.handle_scan_project_task.side_effect = Exception("Network error")
        
        # Execute command
        result = self.cli_interface.scan_project_command(
            "https://github.com/user/repo.git"
        )
        
        # Should return None on error
        assert result is None
    
    def test_scan_project_command_invalid_url(self):
        """Test scan project command with invalid URL."""
        result = self.cli_interface.scan_project_command("invalid-url")
        
        # Should return None due to ValueError
        assert result is None


class TestCLICommands:
    """Test cases for CLI commands using Click testing."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help message."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "RepoChat v1.0" in result.output
        assert "AI Repository Analysis Assistant" in result.output
    
    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert "1.0.0" in result.output
    
    def test_scan_project_help(self):
        """Test scan-project command help."""
        result = self.runner.invoke(cli, ['scan-project', '--help'])
        
        assert result.exit_code == 0
        assert "Quét và phân tích một repository Git" in result.output
        assert "REPOSITORY_URL" in result.output
    
    @patch('teams.interaction_tasking.cli_interface.CLIInterface.scan_project_command')
    def test_scan_project_command_execution(self, mock_scan_command):
        """Test scan-project command execution."""
        # Mock successful execution
        mock_project_context = ProjectDataContext(
            repository_url="https://github.com/user/repo.git",
            cloned_code_path="/tmp/test_repo",
            detected_languages=["java"],
            primary_language="java",
            language_count=1,
            has_languages=True
        )
        mock_scan_command.return_value = mock_project_context
        
        result = self.runner.invoke(cli, [
            'scan-project', 
            'https://github.com/user/repo.git'
        ])
        
        assert result.exit_code == 0
        mock_scan_command.assert_called_once_with(
            'https://github.com/user/repo.git', 
            False  # verbose=False by default
        )
    
    @patch('teams.interaction_tasking.cli_interface.CLIInterface.scan_project_command')
    def test_scan_project_command_verbose(self, mock_scan_command):
        """Test scan-project command with verbose flag."""
        mock_scan_command.return_value = Mock()
        
        result = self.runner.invoke(cli, [
            'scan-project', 
            'https://github.com/user/repo.git',
            '--verbose'
        ])
        
        assert result.exit_code == 0
        mock_scan_command.assert_called_once_with(
            'https://github.com/user/repo.git', 
            True  # verbose=True
        )
    
    @patch('teams.interaction_tasking.cli_interface.CLIInterface.scan_project_command')
    def test_scan_project_command_failure(self, mock_scan_command):
        """Test scan-project command failure."""
        # Mock failed execution
        mock_scan_command.return_value = None
        
        result = self.runner.invoke(cli, [
            'scan-project', 
            'https://github.com/user/repo.git'
        ])
        
        assert result.exit_code == 1  # Should exit with error code
    
    def test_review_pr_placeholder(self):
        """Test review-pr command placeholder."""
        result = self.runner.invoke(cli, [
            'review-pr',
            'https://github.com/user/repo.git',
            '123'
        ])
        
        assert result.exit_code == 0
        assert "Task 4.2" in result.output
        assert "Repository: https://github.com/user/repo.git" in result.output
        assert "PR ID: 123" in result.output
    
    def test_status_command(self):
        """Test status command."""
        result = self.runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert "RepoChat v1.0" in result.output
        assert "Phase 1: Data Acquisition - COMPLETED" in result.output
        assert "Phase 2: Code Knowledge Graph - COMPLETED" in result.output
        assert "Phase 3: Code Analysis & LLM - COMPLETED" in result.output
        assert "Phase 4: CLI Interface - IN PROGRESS" in result.output
        assert "scan-project" in result.output


class TestIntegrationCLI:
    """Integration tests for CLI with mocked dependencies."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.runner = CliRunner()
    
    @patch('teams.interaction_tasking.cli_interface.OrchestratorAgent')
    def test_end_to_end_scan_project(self, mock_orchestrator_class):
        """Test end-to-end scan project workflow."""
        # Setup mocks
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        mock_project_context = ProjectDataContext(
            repository_url="https://github.com/spring-projects/spring-petclinic.git",
            cloned_code_path="/tmp/spring_petclinic",
            detected_languages=["java", "html"],
            primary_language="java",
            language_count=2,
            has_languages=True
        )
        mock_orchestrator.handle_scan_project_task.return_value = mock_project_context
        mock_orchestrator.get_agent_stats.return_value = {
            'statistics': {'successful_tasks': 1},
            'uptime_seconds': 10.5
        }
        
        # Execute CLI command
        result = self.runner.invoke(cli, [
            'scan-project',
            'https://github.com/spring-projects/spring-petclinic.git',
            '--verbose'
        ])
        
        # Verify success
        assert result.exit_code == 0
        assert "Bắt đầu quét dự án" in result.output
        assert "spring-petclinic.git" in result.output
        assert "hoàn thành thành công" in result.output
        assert "java, html" in result.output
        assert "Ngôn ngữ chính: java" in result.output
        
        # Verify orchestrator interaction
        mock_orchestrator_class.assert_called_once()
        mock_orchestrator.handle_scan_project_task.assert_called_once()
        
        # Verify task definition
        call_args = mock_orchestrator.handle_scan_project_task.call_args[0]
        task_def = call_args[0]
        assert isinstance(task_def, TaskDefinition)
        assert task_def.repository_url == "https://github.com/spring-projects/spring-petclinic.git"
        assert task_def.task_id.startswith("scan-project-")


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 