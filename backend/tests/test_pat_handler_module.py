"""
Unit tests for PATHandlerModule

Tests Task 1.6 (F1.6) implementation for Personal Access Token handling.
"""

import pytest
from unittest.mock import patch, MagicMock
from teams.data_acquisition.pat_handler_module import PATHandlerModule


class TestPATHandlerModule:
    """Test suite for PATHandlerModule."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pat_handler = PATHandlerModule()
    
    def test_init(self):
        """Test PATHandlerModule initialization."""
        assert self.pat_handler is not None
        assert hasattr(self.pat_handler, 'logger')
        assert hasattr(self.pat_handler, '_pat_cache')
        assert hasattr(self.pat_handler, '_private_indicators')
        assert len(self.pat_handler._pat_cache) == 0
    
    def test_is_private_repository_public_github(self):
        """Test that public GitHub URLs are identified as public."""
        url = "https://github.com/octocat/Hello-World.git"
        result = self.pat_handler._is_private_repository(url)
        assert result is False
    
    def test_is_private_repository_private_keyword(self):
        """Test that URLs with 'private' keyword are identified as private."""
        url = "https://github.com/company/private-repo.git"
        result = self.pat_handler._is_private_repository(url)
        assert result is True
    
    def test_is_private_repository_corporate_domain(self):
        """Test that corporate domains are identified as private."""
        url = "https://git.corp.company.com/team/repo.git"
        result = self.pat_handler._is_private_repository(url)
        assert result is True
    
    def test_is_private_repository_ssh_url(self):
        """Test that SSH URLs are identified as potentially private."""
        url = "git@github.com:user/repo.git"
        result = self.pat_handler._is_private_repository(url)
        assert result is True
    
    def test_is_private_repository_internal_domain(self):
        """Test that internal domains are identified as private."""
        url = "https://gitlab.internal.company.com/team/repo.git"
        result = self.pat_handler._is_private_repository(url)
        assert result is True
    
    def test_is_private_repository_enterprise_github(self):
        """Test that enterprise GitHub is identified as private."""
        url = "https://github.enterprise.company.com/team/repo.git"
        result = self.pat_handler._is_private_repository(url)
        assert result is True
    
    def test_extract_host_https_url(self):
        """Test host extraction from HTTPS URL."""
        url = "https://github.com/user/repo.git"
        result = self.pat_handler._extract_host(url)
        assert result == "github.com"
    
    def test_extract_host_ssh_url(self):
        """Test host extraction from SSH URL."""
        url = "git@gitlab.com:user/repo.git"
        result = self.pat_handler._extract_host(url)
        assert result == "gitlab.com"
    
    def test_extract_host_invalid_url(self):
        """Test host extraction from invalid URL."""
        url = "invalid-url"
        result = self.pat_handler._extract_host(url)
        assert result == "unknown"
    
    def test_extract_host_empty_url(self):
        """Test host extraction from empty URL."""
        url = ""
        result = self.pat_handler._extract_host(url)
        assert result == "unknown"
    
    def test_extract_host_none_url(self):
        """Test host extraction from None URL."""
        url = None
        result = self.pat_handler._extract_host(url)
        assert result == "unknown"
    
    @patch('builtins.input', return_value='test_pat_123')
    @patch('getpass.getpass', return_value='test_pat_123')
    def test_request_pat_from_user_success(self, mock_getpass, mock_input):
        """Test successful PAT request from user."""
        url = "https://github.enterprise.company.com/team/repo.git"
        host = "github.enterprise.company.com"
        result = self.pat_handler._request_pat_from_user(url, host)
        assert result == 'test_pat_123'
        mock_getpass.assert_called_once()
    
    @patch('getpass.getpass', return_value='')
    def test_request_pat_from_user_empty_pat(self, mock_getpass):
        """Test PAT request when user provides empty PAT."""
        url = "https://github.enterprise.company.com/team/repo.git"
        host = "github.enterprise.company.com"
        result = self.pat_handler._request_pat_from_user(url, host)
        assert result is None
        mock_getpass.assert_called_once()
    
    @patch('getpass.getpass', side_effect=KeyboardInterrupt())
    def test_request_pat_from_user_cancelled(self, mock_getpass):
        """Test PAT request when user cancels input."""
        url = "https://github.enterprise.company.com/team/repo.git"
        host = "github.enterprise.company.com"
        result = self.pat_handler._request_pat_from_user(url, host)
        assert result is None
        mock_getpass.assert_called_once()
    
    @patch('getpass.getpass', side_effect=Exception("Input error"))
    def test_request_pat_from_user_error(self, mock_getpass):
        """Test PAT request when an error occurs."""
        url = "https://github.enterprise.company.com/team/repo.git"
        host = "github.enterprise.company.com"
        result = self.pat_handler._request_pat_from_user(url, host)
        assert result is None
        mock_getpass.assert_called_once()
    
    def test_request_pat_if_needed_public_repo(self):
        """Test that no PAT is requested for public repositories."""
        url = "https://github.com/octocat/Hello-World.git"
        result = self.pat_handler.request_pat_if_needed(url)
        assert result is None
    
    @patch.object(PATHandlerModule, '_request_pat_from_user', return_value='test_pat_456')
    def test_request_pat_if_needed_private_repo_success(self, mock_request):
        """Test successful PAT request for private repository."""
        url = "https://github.private.company.com/team/repo.git"
        result = self.pat_handler.request_pat_if_needed(url)
        assert result == 'test_pat_456'
        mock_request.assert_called_once()
        
        # Verify PAT is cached
        host = "github.private.company.com"
        assert host in self.pat_handler._pat_cache
        assert self.pat_handler._pat_cache[host] == 'test_pat_456'
    
    @patch.object(PATHandlerModule, '_request_pat_from_user', return_value='cached_pat')
    def test_request_pat_if_needed_cached_pat(self, mock_request):
        """Test that cached PAT is used for same host."""
        url = "https://github.private.company.com/team/repo.git"
        host = "github.private.company.com"
        
        # Pre-populate cache
        self.pat_handler._pat_cache[host] = 'cached_pat_123'
        
        result = self.pat_handler.request_pat_if_needed(url)
        assert result == 'cached_pat_123'
        
        # Should not request new PAT
        mock_request.assert_not_called()
    
    @patch.object(PATHandlerModule, '_request_pat_from_user', return_value=None)
    def test_request_pat_if_needed_private_repo_no_pat(self, mock_request):
        """Test when user doesn't provide PAT for private repository."""
        url = "https://git.internal.company.com/team/repo.git"
        result = self.pat_handler.request_pat_if_needed(url)
        assert result is None
        mock_request.assert_called_once()
    
    def test_clear_pat_cache(self):
        """Test PAT cache clearing."""
        # Populate cache
        self.pat_handler._pat_cache['host1'] = 'pat1'
        self.pat_handler._pat_cache['host2'] = 'pat2'
        assert len(self.pat_handler._pat_cache) == 2
        
        # Clear cache
        self.pat_handler.clear_pat_cache()
        assert len(self.pat_handler._pat_cache) == 0
    
    def test_get_stats_empty_cache(self):
        """Test statistics with empty cache."""
        stats = self.pat_handler.get_stats()
        assert stats['cached_hosts'] == 0
        assert stats['cached_host_list'] == []
    
    def test_get_stats_with_cached_pats(self):
        """Test statistics with cached PATs."""
        self.pat_handler._pat_cache['github.com'] = 'pat1'
        self.pat_handler._pat_cache['gitlab.com'] = 'pat2'
        
        stats = self.pat_handler.get_stats()
        assert stats['cached_hosts'] == 2
        assert 'github.com' in stats['cached_host_list']
        assert 'gitlab.com' in stats['cached_host_list']
    
    def test_str_representation(self):
        """Test string representation of PATHandlerModule."""
        result = str(self.pat_handler)
        assert 'PATHandlerModule' in result
        assert 'cached_hosts=0' in result
        
        # Add some cached PATs
        self.pat_handler._pat_cache['host1'] = 'pat1'
        result = str(self.pat_handler)
        assert 'cached_hosts=1' in result
    
    def test_private_indicators_coverage(self):
        """Test that all private indicators work correctly."""
        test_cases = [
            ("https://repo.private.com/team/repo.git", True),
            ("https://internal.company.com/repo.git", True),
            ("https://enterprise.github.com/repo.git", True),
            ("https://git.corp.company.com/repo.git", True),
            ("https://company.internal.domain.com/repo.git", True),
            ("https://github.com/public/repo.git", False),
            ("https://gitlab.com/user/repo.git", False)
        ]
        
        for url, expected in test_cases:
            result = self.pat_handler._is_private_repository(url)
            assert result == expected, f"URL {url} should be {'private' if expected else 'public'}"
    
    def test_url_validation_edge_cases(self):
        """Test URL validation edge cases."""
        edge_cases = [
            (None, False),
            ("", False),
            ("   ", False),
            ("not-a-url", False),
            ("ftp://invalid.com/repo", False),
            ("file:///local/path", False)
        ]
        
        for url, expected_result in edge_cases:
            result = self.pat_handler._is_private_repository(url)
            # Should handle gracefully and return False for invalid URLs
            assert result == expected_result, f"URL {url} should return {expected_result}, got {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 