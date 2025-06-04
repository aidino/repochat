"""
PAT Handler Module for TEAM Data Acquisition

Handles Personal Access Token (PAT) management for private repositories.
Implements Task 1.6 (F1.6) requirements.

Security Note: PATs will NOT be stored persistently. They are only used
during the current session and cleared from memory after use.
"""

import re
import getpass
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from shared.utils.logging_config import (
    get_logger, 
    log_function_entry, 
    log_function_exit
)


class PATHandlerModule:
    """
    Module to handle Personal Access Token requests and management.
    
    Features:
    - Detect private repositories requiring authentication
    - Request PAT from user when needed
    - Secure PAT handling (no persistent storage)
    - Support for different Git hosting platforms
    """
    
    def __init__(self):
        """Initialize the PAT Handler Module."""
        self.logger = get_logger("data_acquisition.pat_handler")
        self._pat_cache: Dict[str, str] = {}  # Temporary session cache
        
        # Patterns to identify potentially private repositories
        self._private_indicators = [
            'private',
            'internal',
            'enterprise',
            'corp',
            'company'
        ]
        
        self.logger.info("PAT Handler Module initialized")
    
    def request_pat_if_needed(self, repository_url: str) -> Optional[str]:
        """
        Request PAT from user if repository appears to be private.
        
        Args:
            repository_url: URL of the repository
            
        Returns:
            PAT string if needed and provided, None otherwise
        """
        log_function_entry(self.logger, "request_pat_if_needed", repository_url=repository_url)
        
        self.logger.info(f"Checking if PAT is needed for repository: {repository_url}")
        
        # Check if repository is likely private
        is_private = self._is_private_repository(repository_url)
        
        if not is_private:
            self.logger.info("Repository appears to be public, no PAT needed")
            log_function_exit(self.logger, "request_pat_if_needed", result="not_needed")
            return None
        
        self.logger.warning(f"Repository appears to be private: {repository_url}")
        
        # Check if we already have a PAT for this host in session cache
        host = self._extract_host(repository_url)
        if host in self._pat_cache:
            self.logger.info(f"Using cached PAT for host: {host}")
            log_function_exit(self.logger, "request_pat_if_needed", result="cached_pat")
            return self._pat_cache[host]
        
        # Request PAT from user
        pat = self._request_pat_from_user(repository_url, host)
        
        if pat:
            # Cache PAT for this session (same host)
            self._pat_cache[host] = pat
            self.logger.info(f"PAT obtained and cached for host: {host}")
            log_function_exit(self.logger, "request_pat_if_needed", result="pat_obtained")
            return pat
        else:
            self.logger.warning("No PAT provided by user")
            log_function_exit(self.logger, "request_pat_if_needed", result="no_pat_provided")
            return None
    
    def _is_private_repository(self, repository_url: str) -> bool:
        """
        Determine if repository is likely private based on URL patterns.
        
        Args:
            repository_url: URL to check
            
        Returns:
            True if repository appears private
        """
        log_function_entry(self.logger, "_is_private_repository", repository_url=repository_url)
        
        # Handle None and empty cases
        if repository_url is None or not repository_url or not repository_url.strip():
            self.logger.debug("Repository URL is None or empty")
            log_function_exit(self.logger, "_is_private_repository", result=False)
            return False
        
        url_lower = repository_url.lower()
        
        # Check for private indicators in URL
        for indicator in self._private_indicators:
            if indicator in url_lower:
                self.logger.debug(f"Found private indicator '{indicator}' in URL")
                log_function_exit(self.logger, "_is_private_repository", result=True)
                return True
        
        # Check for enterprise/internal domains
        try:
            parsed = urlparse(repository_url)
            host = parsed.netloc.lower()
            
            # Common patterns for private repositories
            private_patterns = [
                r'.*\.corp\..*',  # Corporate domains
                r'.*\.internal\..*',  # Internal domains
                r'.*\.company\..*',  # Company domains
                r'git\..*\..*',  # Private Git servers
                r'gitlab\..*\..*'  # Private GitLab instances
            ]
            
            for pattern in private_patterns:
                if re.match(pattern, host):
                    self.logger.debug(f"Host matches private pattern: {pattern}")
                    log_function_exit(self.logger, "_is_private_repository", result=True)
                    return True
                    
        except Exception as e:
            self.logger.warning(f"Error parsing URL for private detection: {e}")
        
        # Check for SSH URLs (git@host:repo format)
        if repository_url.startswith('git@'):
            # SSH URLs often indicate private repositories
            self.logger.debug("SSH URL detected, likely private")
            log_function_exit(self.logger, "_is_private_repository", result=True)
            return True
        
        self.logger.debug("No private indicators found")
        log_function_exit(self.logger, "_is_private_repository", result=False)
        return False
    
    def _extract_host(self, repository_url: str) -> str:
        """
        Extract host from repository URL.
        
        Args:
            repository_url: Repository URL
            
        Returns:
            Host string
        """
        try:
            if not repository_url or not repository_url.strip():
                return "unknown"
                
            if repository_url.startswith('git@'):
                # SSH format: git@host:user/repo
                parts = repository_url.split('@')
                if len(parts) > 1:
                    host_part = parts[1].split(':')
                    if len(host_part) > 0:
                        return host_part[0]
                return "unknown"
            else:
                # HTTP/HTTPS format
                parsed = urlparse(repository_url)
                return parsed.netloc if parsed.netloc else "unknown"
        except Exception as e:
            self.logger.warning(f"Error extracting host from URL: {e}")
            return "unknown"
    
    def _request_pat_from_user(self, repository_url: str, host: str) -> Optional[str]:
        """
        Request PAT from user through console input.
        
        Args:
            repository_url: Repository URL
            host: Extracted host
            
        Returns:
            PAT if provided, None otherwise
        """
        log_function_entry(self.logger, "_request_pat_from_user", repository_url=repository_url, host=host)
        
        self.logger.warning(f"Private repository detected: {repository_url}")
        
        print("\n" + "="*60)
        print("🔐 PRIVATE REPOSITORY ACCESS REQUIRED")
        print("="*60)
        print(f"Repository: {repository_url}")
        print(f"Host: {host}")
        print("\nThis repository appears to be private and requires authentication.")
        print("Please provide a Personal Access Token (PAT) with repository access.")
        print("\nNote: Your PAT will only be used for this session and will not be stored.")
        print("="*60)
        
        try:
            # Request PAT with secure input (hidden)
            pat = getpass.getpass("Enter your Personal Access Token (PAT): ").strip()
            
            if pat:
                self.logger.info("PAT provided by user", extra={
                    'extra_data': {
                        'host': host,
                        'pat_length': len(pat),
                        'repository_url': repository_url
                    }
                })
                print("✅ PAT received. Proceeding with repository access...")
                log_function_exit(self.logger, "_request_pat_from_user", result="pat_provided")
                return pat
            else:
                print("❌ No PAT provided. Proceeding without authentication (may fail)...")
                self.logger.warning("User provided empty PAT")
                log_function_exit(self.logger, "_request_pat_from_user", result="empty_pat")
                return None
                
        except KeyboardInterrupt:
            print("\n❌ PAT input cancelled by user")
            self.logger.info("PAT input cancelled by user")
            log_function_exit(self.logger, "_request_pat_from_user", result="cancelled")
            return None
        except Exception as e:
            print(f"\n❌ Error reading PAT: {e}")
            self.logger.error(f"Error reading PAT from user: {e}")
            log_function_exit(self.logger, "_request_pat_from_user", result="error")
            return None
    
    def clear_pat_cache(self) -> None:
        """
        Clear all cached PATs from memory for security.
        Should be called after task completion.
        """
        log_function_entry(self.logger, "clear_pat_cache")
        
        cached_count = len(self._pat_cache)
        self._pat_cache.clear()
        
        self.logger.info(f"Cleared {cached_count} PATs from cache for security")
        log_function_exit(self.logger, "clear_pat_cache", result=f"cleared_{cached_count}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about PAT handling.
        
        Returns:
            Dictionary with PAT handler statistics
        """
        return {
            'cached_hosts': len(self._pat_cache),
            'cached_host_list': list(self._pat_cache.keys())
        }
    
    def __str__(self) -> str:
        return f"PATHandlerModule(cached_hosts={len(self._pat_cache)})" 