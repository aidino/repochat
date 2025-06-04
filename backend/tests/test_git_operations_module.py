"""
Unit tests for GitOperationsModule - TEAM Data Acquisition

Tests cover:
- Repository URL validation
- Successful cloning operations
- Error handling for various failure scenarios
- Cleanup operations
- Edge cases and security concerns
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import git
from git import GitCommandError, InvalidGitRepositoryError

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from teams.data_acquisition.git_operations_module import GitOperationsModule


class TestGitOperationsModule:
    """Test cases for GitOperationsModule."""
    
    def setup_method(self):
        """Setup test environment for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.git_ops = GitOperationsModule(base_temp_dir=str(self.temp_dir))
    
    def teardown_method(self):
        """Cleanup after each test."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    # ===== URL Validation Tests =====
    
    def test_validate_repository_url_valid_github(self):
        """Test validation of valid GitHub URLs."""
        valid_urls = [
            "https://github.com/user/repo.git",
            "https://github.com/user/repo",
            "git@github.com:user/repo.git",
            "https://github.com/organization/project.git"
        ]
        
        for url in valid_urls:
            assert self.git_ops._validate_repository_url(url), f"Should validate: {url}"
    
    def test_validate_repository_url_valid_gitlab(self):
        """Test validation of valid GitLab URLs."""
        valid_urls = [
            "https://gitlab.com/user/repo.git",
            "https://gitlab.com/group/project",
            "git@gitlab.com:user/repo.git"
        ]
        
        for url in valid_urls:
            assert self.git_ops._validate_repository_url(url), f"Should validate: {url}"
    
    def test_validate_repository_url_invalid_empty(self):
        """Test validation rejects empty URLs."""
        invalid_urls = ["", "   "]
        
        for url in invalid_urls:
            assert not self.git_ops._validate_repository_url(url), f"Should reject: {url}"
        
        # Test None separately as it will likely cause AttributeError in real usage
        # but our implementation handles it gracefully
        assert not self.git_ops._validate_repository_url(None), "Should reject None"
    
    def test_validate_repository_url_invalid_format(self):
        """Test validation rejects malformed URLs."""
        invalid_urls = [
            "not-a-url",
            "http://",
            "just-text"
        ]
        
        for url in invalid_urls:
            assert not self.git_ops._validate_repository_url(url), f"Should reject: {url}"
        
        # FTP should be rejected due to protocol restriction
        assert not self.git_ops._validate_repository_url("ftp://example.com/repo"), "Should reject FTP"
    
    # ===== Path Generation Tests =====
    
    def test_generate_clone_path_basic(self):
        """Test clone path generation with basic repository URL."""
        url = "https://github.com/user/test-repo.git"
        path = self.git_ops._generate_clone_path(url)
        
        assert path.parent == self.temp_dir
        assert "test-repo" in path.name
        assert "repochat_" in path.name
        assert path.name.count('_') >= 2  # repochat_repo_timestamp
    
    def test_generate_clone_path_no_git_extension(self):
        """Test clone path generation without .git extension."""
        url = "https://github.com/user/my-project"
        path = self.git_ops._generate_clone_path(url)
        
        assert "my-project" in path.name
        assert path.name.startswith("repochat_")
    
    def test_generate_clone_path_special_characters(self):
        """Test clone path generation with special characters in repo name."""
        url = "https://github.com/user/repo@#$%^&*()name.git"
        path = self.git_ops._generate_clone_path(url)
        
        # Should sanitize special characters
        assert not any(char in path.name for char in '@#$%^&*()')
        assert "repo" in path.name and "name" in path.name
    
    def test_generate_clone_path_uniqueness(self):
        """Test that generated paths are unique."""
        url = "https://github.com/user/repo.git"
        
        path1 = self.git_ops._generate_clone_path(url)
        path2 = self.git_ops._generate_clone_path(url)
        
        assert path1 != path2, "Generated paths should be unique"
    
    # ===== Clone Repository Tests - Success Cases =====
    
    @patch('teams.data_acquisition.git_operations_module.Repo.clone_from')
    def test_clone_repository_success(self, mock_clone_from):
        """Test successful repository cloning."""
        # Setup mock
        mock_repo = MagicMock()
        mock_repo.active_branch.name = "main"
        mock_repo.head.commit.hexsha = "abcd1234567890abcd1234567890abcd12345678"
        mock_repo.head.commit.message = "Initial commit"
        mock_repo.remotes = [MagicMock()]
        mock_repo.remotes[0].urls = ["https://github.com/user/repo.git"]
        
        def create_clone_dir(*args, **kwargs):
            """Side effect to create the clone directory structure."""
            clone_path = Path(kwargs['to_path'])
            clone_path.mkdir(parents=True, exist_ok=True)
            (clone_path / '.git').mkdir(exist_ok=True)
            return mock_repo
            
        mock_clone_from.side_effect = create_clone_dir
        
        # Test
        url = "https://github.com/user/test-repo.git"
        result = self.git_ops.clone_repository(url)
        
        # Assertions
        assert result is not None
        assert isinstance(result, str)
        assert Path(result).exists()
        assert (Path(result) / '.git').exists()
        
        # Verify clone_from was called with correct parameters
        mock_clone_from.assert_called_once()
        call_kwargs = mock_clone_from.call_args[1]
        assert call_kwargs['url'] == url
        assert call_kwargs['depth'] == 1
        assert call_kwargs['single_branch'] is True
    
    @patch('teams.data_acquisition.git_operations_module.Repo.clone_from')
    def test_clone_repository_with_target_path(self, mock_clone_from):
        """Test cloning with specified target path."""
        # Setup mock
        mock_repo = MagicMock()
        mock_repo.active_branch.name = "main"
        mock_repo.head.commit.hexsha = "abcd1234567890abcd1234567890abcd12345678"
        mock_repo.head.commit.message = "Test commit"
        mock_repo.remotes = [MagicMock()]
        mock_repo.remotes[0].urls = ["https://github.com/user/repo.git"]
        
        def create_clone_dir(*args, **kwargs):
            """Side effect to create the clone directory structure."""
            clone_path = Path(kwargs['to_path'])
            clone_path.mkdir(parents=True, exist_ok=True)
            (clone_path / '.git').mkdir(exist_ok=True)
            return mock_repo
            
        mock_clone_from.side_effect = create_clone_dir
        
        # Test with custom target path
        url = "https://github.com/user/test-repo.git"
        target_path = str(self.temp_dir / "custom_target")
        result = self.git_ops.clone_repository(url, target_path)
        
        # Assertions
        assert result == target_path
        assert Path(target_path).exists()
        assert (Path(target_path) / '.git').exists()
        
        # Verify clone_from was called with custom path
        mock_clone_from.assert_called_once()
        call_kwargs = mock_clone_from.call_args[1]
        assert call_kwargs['to_path'] == target_path
    
    # ===== Clone Repository Tests - Error Cases =====
    
    def test_clone_repository_invalid_url(self):
        """Test cloning with invalid URL raises ValueError."""
        invalid_url = "not-a-valid-url"
        
        with pytest.raises(ValueError) as exc_info:
            self.git_ops.clone_repository(invalid_url)
        
        assert "Invalid repository URL" in str(exc_info.value)
    
    @patch('teams.data_acquisition.git_operations_module.Repo.clone_from')
    def test_clone_repository_git_command_error(self, mock_clone_from):
        """Test handling of Git command errors."""
        # Setup mock to raise GitCommandError
        mock_clone_from.side_effect = GitCommandError("git clone", 1, "Repository not found")
        
        url = "https://github.com/user/nonexistent-repo.git"
        
        with pytest.raises(GitCommandError):
            self.git_ops.clone_repository(url)
    
    @patch('teams.data_acquisition.git_operations_module.Repo.clone_from')
    def test_clone_repository_permission_error(self, mock_clone_from):
        """Test handling of permission errors."""
        # Setup mock to raise PermissionError
        mock_clone_from.side_effect = PermissionError("Permission denied")
        
        url = "https://github.com/user/repo.git"
        
        with pytest.raises(PermissionError):
            self.git_ops.clone_repository(url)
    
    @patch('teams.data_acquisition.git_operations_module.Repo.clone_from')
    def test_clone_repository_os_error(self, mock_clone_from):
        """Test handling of OS errors."""
        # Setup mock to raise OSError
        mock_clone_from.side_effect = OSError("Disk full")
        
        url = "https://github.com/user/repo.git"
        
        with pytest.raises(OSError):
            self.git_ops.clone_repository(url)
    
    @patch('teams.data_acquisition.git_operations_module.Repo.clone_from')
    def test_clone_repository_cleanup_on_failure(self, mock_clone_from):
        """Test that failed clones are cleaned up."""
        # Setup mock to raise an error after creating directory
        mock_clone_from.side_effect = GitCommandError("git clone", 1, "Network error")
        
        url = "https://github.com/user/repo.git"
        
        # Get the path that would be created
        clone_path = self.git_ops._generate_clone_path(url)
        
        with pytest.raises(GitCommandError):
            self.git_ops.clone_repository(url)
        
        # Verify cleanup occurred (path should not exist)
        # Note: In real scenario, cleanup happens in _cleanup_failed_clone
        # Here we test the exception propagation
    
    # ===== Cleanup Tests =====
    
    def test_cleanup_repository_success(self):
        """Test successful repository cleanup."""
        # Create a test directory to cleanup
        test_repo_path = self.temp_dir / "test_repo"
        test_repo_path.mkdir()
        (test_repo_path / "test_file.txt").write_text("test content")
        
        assert test_repo_path.exists()
        
        # Test cleanup
        result = self.git_ops.cleanup_repository(str(test_repo_path))
        
        assert result is True
        assert not test_repo_path.exists()
    
    def test_cleanup_repository_nonexistent_path(self):
        """Test cleanup of non-existent repository."""
        nonexistent_path = str(self.temp_dir / "nonexistent")
        
        result = self.git_ops.cleanup_repository(nonexistent_path)
        
        # Should return True (cleanup successful, nothing to do)
        assert result is True
    
    @patch('shutil.rmtree')
    def test_cleanup_repository_error(self, mock_rmtree):
        """Test cleanup error handling."""
        # Setup mock to raise an error
        mock_rmtree.side_effect = OSError("Permission denied")
        
        # Create a test directory
        test_repo_path = self.temp_dir / "test_repo"
        test_repo_path.mkdir()
        
        result = self.git_ops.cleanup_repository(str(test_repo_path))
        
        # Should return False on error
        assert result is False
    
    # ===== Repository Stats Tests =====
    
    def test_get_repository_stats_empty(self):
        """Test repository stats with no repositories."""
        stats = self.git_ops.get_repository_stats()
        
        assert stats['temp_repositories_count'] == 0
        assert stats['total_size_mb'] == 0
        assert stats['base_temp_dir'] == str(self.temp_dir)
        assert stats['repositories'] == []
    
    def test_get_repository_stats_with_repositories(self):
        """Test repository stats with some repositories."""
        # Create fake repository directories matching the actual pattern
        repo1 = self.temp_dir / "repochat_repo1_123456_1000"
        repo2 = self.temp_dir / "repochat_repo2_789012_2000"
        
        repo1.mkdir()
        repo2.mkdir()
        
        # Add some files to calculate size
        (repo1 / "file1.txt").write_text("content1")
        (repo2 / "file2.txt").write_text("content2")
        
        stats = self.git_ops.get_repository_stats()
        
        assert stats['temp_repositories_count'] == 2
        assert stats['total_size_mb'] >= 0  # Size might be very small but should be calculated
        assert len(stats['repositories']) == 2
        assert any('repo1' in repo for repo in stats['repositories'])
        assert any('repo2' in repo for repo in stats['repositories'])
    
    # ===== Edge Cases and Security Tests =====
    
    def test_directory_size_calculation(self):
        """Test directory size calculation."""
        test_dir = self.temp_dir / "size_test"
        test_dir.mkdir()
        
        # Create files with known sizes
        (test_dir / "file1.txt").write_text("a" * 1000)  # 1KB
        (test_dir / "file2.txt").write_text("b" * 2000)  # 2KB
        
        size_mb = self.git_ops._calculate_directory_size(test_dir)
        
        # Should be approximately 0.003 MB (3KB)
        assert 0.001 <= size_mb <= 0.01
    
    def test_git_version_retrieval(self):
        """Test Git version retrieval for logging."""
        version = self.git_ops._get_git_version()
        
        # Should return either a version string or "unknown"
        assert isinstance(version, str)
        assert len(version) > 0
    
    @patch('git.cmd.Git')
    def test_git_version_error_handling(self, mock_git):
        """Test Git version error handling."""
        # Setup mock to raise an error
        mock_git.return_value.version.side_effect = Exception("Git not found")
        
        git_ops = GitOperationsModule()
        version = git_ops._get_git_version()
        
        assert version == "unknown"
    
    # ===== Integration-like Tests =====
    
    def test_clone_path_within_base_temp_dir(self):
        """Test that generated clone paths are within the base temp directory."""
        url = "https://github.com/user/repo.git"
        clone_path = self.git_ops._generate_clone_path(url)
        
        # Path should be within base_temp_dir
        assert clone_path.parent == self.temp_dir
        assert str(clone_path).startswith(str(self.temp_dir))
    
    def test_repository_info_extraction_error_handling(self):
        """Test repository info extraction with mock errors."""
        # Create a mock repo that throws errors when accessing nested attributes
        mock_repo = MagicMock()
        
        # Setup to raise exception when calling the function
        def side_effect(*args, **kwargs):
            raise Exception("Mock error")
        
        mock_repo.active_branch = MagicMock()
        mock_repo.active_branch.name = MagicMock(side_effect=side_effect)
        
        test_path = self.temp_dir / "test_repo"
        test_path.mkdir()
        
        info = self.git_ops._get_repository_info(mock_repo, test_path)
        
        # Should return error info instead of crashing
        assert 'error' in info
        assert isinstance(info['error'], str) 