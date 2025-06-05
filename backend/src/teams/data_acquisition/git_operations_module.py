"""
GitOperationsModule - TEAM Data Acquisition

Handles Git repository operations including shallow cloning for RepoChat v1.0.
Provides secure and robust repository cloning functionality with comprehensive logging.
Enhanced with Personal Access Token (PAT) support for private repositories.
"""

import os
import tempfile
import shutil
import time
import re
from typing import Optional, Dict, Any, List
from pathlib import Path
from urllib.parse import urlparse
import random

import git
from git import Repo, InvalidGitRepositoryError, GitCommandError

from shared.utils.logging_config import (
    get_logger,
    log_function_entry, 
    log_function_exit,
    log_performance_metric
)
from shared.models.project_data_context import PRDiffInfo


class GitOperationsModule:
    """
    Module for handling Git repository operations.
    
    Provides functionality to clone repositories safely with comprehensive
    error handling and logging for debugging and monitoring.
    Enhanced with Personal Access Token (PAT) support for private repositories.
    """
    
    def __init__(self, base_temp_dir: Optional[str] = None):
        """
        Initialize GitOperationsModule.
        
        Args:
            base_temp_dir: Base directory for temporary files. If None, uses system temp.
        """
        self.logger = get_logger("data_acquisition.git_operations")
        self.base_temp_dir = Path(base_temp_dir) if base_temp_dir else Path(tempfile.gettempdir())
        
        log_function_entry(self.logger, "__init__", base_temp_dir=base_temp_dir)
        
        # Ensure base temp directory exists
        self.base_temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"GitOperationsModule initialized", extra={
            'extra_data': {
                'base_temp_dir': str(self.base_temp_dir),
                'git_version': self._get_git_version()
            }
        })
        
        log_function_exit(self.logger, "__init__", result="success")
    
    def _get_git_version(self) -> str:
        """Get Git version for logging purposes."""
        try:
            return git.cmd.Git().version()
        except Exception as e:
            self.logger.warning(f"Could not get Git version: {e}")
            return "unknown"
    
    def _validate_repository_url(self, repository_url: str) -> bool:
        """
        Validate repository URL format.
        
        Args:
            repository_url: URL to validate
            
        Returns:
            True if URL appears valid, False otherwise
        """
        log_function_entry(self.logger, "_validate_repository_url", repository_url=repository_url)
        
        # Handle None case
        if repository_url is None:
            self.logger.warning("Repository URL is None")
            log_function_exit(self.logger, "_validate_repository_url", result=False)
            return False
            
        if not repository_url or not repository_url.strip():
            self.logger.warning("Repository URL is empty")
            log_function_exit(self.logger, "_validate_repository_url", result=False)
            return False
        
        # Handle SSH URLs (git@host:path format)
        if repository_url.startswith('git@'):
            # SSH URL format: git@github.com:user/repo.git
            if ':' in repository_url and '/' in repository_url:
                log_function_exit(self.logger, "_validate_repository_url", result=True)
                return True
            else:
                self.logger.warning(f"Invalid SSH URL format: {repository_url}")
                log_function_exit(self.logger, "_validate_repository_url", result=False)
                return False
        
        # Basic URL validation for HTTP/HTTPS
        try:
            parsed = urlparse(repository_url)
            if not parsed.scheme or not parsed.netloc:
                self.logger.warning(f"Invalid URL format: {repository_url}")
                log_function_exit(self.logger, "_validate_repository_url", result=False)
                return False
            
            # Only allow Git-friendly protocols
            if parsed.scheme not in ['http', 'https', 'git']:
                self.logger.warning(f"Unsupported protocol {parsed.scheme}: {repository_url}")
                log_function_exit(self.logger, "_validate_repository_url", result=False)
                return False
            
            # Check for common Git hosting patterns
            valid_patterns = [
                'github.com', 'gitlab.com', 'bitbucket.org',
                'git.', '.git', 'codecommit'
            ]
            
            url_lower = repository_url.lower()
            is_git_url = any(pattern in url_lower for pattern in valid_patterns)
            
            if not is_git_url:
                self.logger.info(f"URL doesn't match common Git patterns but proceeding: {repository_url}")
            
            log_function_exit(self.logger, "_validate_repository_url", result=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating URL: {e}", exc_info=True)
            log_function_exit(self.logger, "_validate_repository_url", result=False)
            return False
    
    def _build_authenticated_url(self, repository_url: str, pat: str) -> str:
        """
        Build authenticated URL with PAT for private repositories.
        
        Args:
            repository_url: Original repository URL
            pat: Personal Access Token
            
        Returns:
            Authenticated URL with embedded PAT
        """
        log_function_entry(self.logger, "_build_authenticated_url", repository_url=repository_url)
        
        # Don't process SSH URLs - they use SSH key authentication
        if repository_url.startswith('git@'):
            self.logger.info("SSH URL detected, returning original URL (PAT not applicable)")
            log_function_exit(self.logger, "_build_authenticated_url", result="ssh_unchanged")
            return repository_url
        
        try:
            parsed = urlparse(repository_url)
            
            # Build authenticated URL for HTTPS
            if parsed.scheme in ['http', 'https']:
                # Format: https://token@host/path
                authenticated_url = f"{parsed.scheme}://{pat}@{parsed.netloc}{parsed.path}"
                
                self.logger.info("Built authenticated URL with PAT", extra={
                    'extra_data': {
                        'original_host': parsed.netloc,
                        'scheme': parsed.scheme,
                        'pat_length': len(pat)
                    }
                })
                
                log_function_exit(self.logger, "_build_authenticated_url", result="authenticated_url_built")
                return authenticated_url
            else:
                self.logger.warning(f"Unsupported scheme for PAT authentication: {parsed.scheme}")
                log_function_exit(self.logger, "_build_authenticated_url", result="unsupported_scheme")
                return repository_url
                
        except Exception as e:
            self.logger.error(f"Error building authenticated URL: {e}", exc_info=True)
            log_function_exit(self.logger, "_build_authenticated_url", result="error")
            return repository_url
    
    def _generate_clone_path(self, repository_url: str) -> Path:
        """
        Generate a unique temporary directory path for cloning.
        
        Args:
            repository_url: Repository URL to generate path for
            
        Returns:
            Path object for clone directory
        """
        # Extract repository name from URL
        repo_name = repository_url.split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        # Sanitize repository name for file system
        safe_repo_name = "".join(c for c in repo_name if c.isalnum() or c in ('-', '_')).strip()
        if not safe_repo_name:
            safe_repo_name = "repo"
        
        # Generate unique directory name with high-resolution timestamp + random
        timestamp = int(time.time() * 1000000)  # microseconds for better uniqueness
        random_suffix = random.randint(1000, 9999)
        clone_dir_name = f"repochat_{safe_repo_name}_{timestamp}_{random_suffix}"
        
        clone_path = self.base_temp_dir / clone_dir_name
        
        self.logger.debug(f"Generated clone path: {clone_path}", extra={
            'extra_data': {
                'repository_url': repository_url,
                'repo_name': repo_name,
                'safe_repo_name': safe_repo_name,
                'clone_path': str(clone_path)
            }
        })
        
        return clone_path
    
    def clone_repository(self, repository_url: str, target_path: Optional[str] = None, pat: Optional[str] = None) -> Optional[str]:
        """
        Clone a Git repository with shallow clone (--depth 1) for efficiency.
        Enhanced with Personal Access Token (PAT) support for private repositories.
        
        Args:
            repository_url: URL of the repository to clone
            target_path: Optional target directory path. If None, auto-generates temp path.
            pat: Optional Personal Access Token for private repositories
            
        Returns:
            Path to the cloned repository directory on success, None on failure
            
        Raises:
            ValueError: If repository_url is invalid
            GitCommandError: If Git operation fails
        """
        start_time = time.time()
        log_function_entry(
            self.logger, 
            "clone_repository", 
            repository_url=repository_url,
            target_path=target_path,
            has_pat=pat is not None
        )
        
        self.logger.info(f"Starting repository clone: {repository_url}", extra={
            'extra_data': {
                'has_pat': pat is not None,
                'target_path': target_path
            }
        })
        
        # Validation
        if not self._validate_repository_url(repository_url):
            error_msg = f"Invalid repository URL: {repository_url}"
            self.logger.error(error_msg)
            log_function_exit(self.logger, "clone_repository", result="validation_error")
            raise ValueError(error_msg)
        
        # Determine clone path
        if target_path:
            clone_path = Path(target_path)
        else:
            clone_path = self._generate_clone_path(repository_url)
        
        # Prepare URL for cloning (with PAT if provided)
        clone_url = repository_url
        if pat:
            clone_url = self._build_authenticated_url(repository_url, pat)
            self.logger.info("Using PAT for repository authentication")
        
        try:
            # Ensure target directory doesn't exist
            if clone_path.exists():
                self.logger.warning(f"Target path already exists, removing: {clone_path}")
                shutil.rmtree(clone_path)
            
            # Ensure parent directory exists
            clone_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Cloning repository to: {clone_path}", extra={
                'extra_data': {
                    'repository_url': repository_url,  # Log original URL (not with PAT)
                    'clone_path': str(clone_path),
                    'method': 'shallow_clone',
                    'authenticated': pat is not None
                }
            })
            
            # Perform shallow clone (--depth 1)
            clone_start_time = time.time()
            
            repo = Repo.clone_from(
                url=clone_url,  # Use potentially authenticated URL
                to_path=str(clone_path),
                depth=1,  # Shallow clone for efficiency
                branch=None,  # Clone default branch
                single_branch=True  # Only clone single branch
            )
            
            clone_duration = time.time() - clone_start_time
            
            # Verify clone was successful
            if not clone_path.exists() or not (clone_path / '.git').exists():
                raise GitCommandError("Clone completed but repository structure not found")
            
            # Get repository information
            repo_info = self._get_repository_info(repo, clone_path)
            
            log_performance_metric(
                self.logger,
                "repository_clone_time",
                clone_duration * 1000,
                "ms",
                repository_url=repository_url,
                clone_size_mb=repo_info.get('size_mb', 0),
                authenticated=pat is not None
            )
            
            self.logger.info(f"Repository cloned successfully: {clone_path}", extra={
                'extra_data': {
                    'repository_url': repository_url,
                    'clone_path': str(clone_path),
                    'clone_duration_ms': clone_duration * 1000,
                    'repository_info': repo_info,
                    'authenticated': pat is not None
                }
            })
            
            # Clear PAT from memory immediately after use
            if pat:
                pat = None  # Clear PAT reference
                self.logger.debug("PAT cleared from memory after use")
            
            total_duration = time.time() - start_time
            log_function_exit(
                self.logger, 
                "clone_repository", 
                result=str(clone_path), 
                execution_time=total_duration
            )
            
            return str(clone_path)
            
        except GitCommandError as e:
            error_msg = f"Git operation failed for {repository_url}: {e}"
            self.logger.error(error_msg, exc_info=True, extra={
                'extra_data': {
                    'repository_url': repository_url,
                    'clone_path': str(clone_path),
                    'error_type': 'GitCommandError',
                    'git_error': str(e)
                }
            })
            
            # Cleanup on failure
            self._cleanup_failed_clone(clone_path)
            
            log_function_exit(self.logger, "clone_repository", result="git_error")
            raise
            
        except PermissionError as e:
            error_msg = f"Permission denied accessing {clone_path}: {e}"
            self.logger.error(error_msg, exc_info=True, extra={
                'extra_data': {
                    'repository_url': repository_url,
                    'clone_path': str(clone_path),
                    'error_type': 'PermissionError'
                }
            })
            
            log_function_exit(self.logger, "clone_repository", result="permission_error")
            raise
            
        except OSError as e:
            error_msg = f"Filesystem error during clone: {e}"
            self.logger.error(error_msg, exc_info=True, extra={
                'extra_data': {
                    'repository_url': repository_url,
                    'clone_path': str(clone_path),
                    'error_type': 'OSError'
                }
            })
            
            self._cleanup_failed_clone(clone_path)
            
            log_function_exit(self.logger, "clone_repository", result="filesystem_error")
            raise
            
        except Exception as e:
            error_msg = f"Unexpected error during clone: {e}"
            self.logger.error(error_msg, exc_info=True, extra={
                'extra_data': {
                    'repository_url': repository_url,
                    'clone_path': str(clone_path),
                    'error_type': type(e).__name__
                }
            })
            
            self._cleanup_failed_clone(clone_path)
            
            log_function_exit(self.logger, "clone_repository", result="unexpected_error")
            raise
    
    def _get_repository_info(self, repo: Repo, clone_path: Path) -> Dict[str, Any]:
        """
        Extract basic repository information for logging.
        
        Args:
            repo: GitPython Repo object
            clone_path: Path to cloned repository
            
        Returns:
            Dictionary with repository information
        """
        try:
            info = {
                'default_branch': repo.active_branch.name if repo.active_branch else 'unknown',
                'commit_hash': repo.head.commit.hexsha[:8] if repo.head.commit else 'unknown',
                'commit_message': repo.head.commit.message.strip()[:100] if repo.head.commit else 'unknown',
                'size_mb': self._calculate_directory_size(clone_path)
            }
            
            # Get remote URL (cleaned)
            if repo.remotes:
                remote_url = list(repo.remotes[0].urls)[0]
                info['remote_url'] = remote_url
            
            return info
            
        except Exception as e:
            self.logger.warning(f"Could not extract repository info: {e}")
            return {'error': str(e)}
    
    def _calculate_directory_size(self, path: Path) -> float:
        """Calculate directory size in MB."""
        try:
            total_size = sum(
                f.stat().st_size for f in path.rglob('*') if f.is_file()
            )
            return round(total_size / (1024 * 1024), 4)  # More precision for small files
        except Exception:
            return 0.0
    
    def _cleanup_failed_clone(self, clone_path: Path) -> None:
        """
        Clean up failed clone directory.
        
        Args:
            clone_path: Path to clean up
        """
        try:
            if clone_path.exists():
                shutil.rmtree(clone_path)
                self.logger.info(f"Cleaned up failed clone directory: {clone_path}")
        except Exception as e:
            self.logger.warning(f"Could not clean up failed clone directory {clone_path}: {e}")
    
    def cleanup_repository(self, repository_path: str) -> bool:
        """
        Clean up cloned repository directory.
        
        Args:
            repository_path: Path to repository to clean up
            
        Returns:
            True if cleanup successful, False otherwise
        """
        start_time = time.time()
        log_function_entry(self.logger, "cleanup_repository", repository_path=repository_path)
        
        try:
            repo_path = Path(repository_path)
            
            if not repo_path.exists():
                self.logger.warning(f"Repository path does not exist: {repository_path}")
                log_function_exit(self.logger, "cleanup_repository", result=True)
                return True
            
            # Calculate size before cleanup for metrics
            size_mb = self._calculate_directory_size(repo_path)
            
            shutil.rmtree(repo_path)
            
            log_performance_metric(
                self.logger,
                "repository_cleanup_size",
                size_mb,
                "mb",
                repository_path=repository_path
            )
            
            self.logger.info(f"Repository cleaned up successfully: {repository_path}", extra={
                'extra_data': {
                    'repository_path': repository_path,
                    'size_mb': size_mb,
                    'cleanup_duration_ms': (time.time() - start_time) * 1000
                }
            })
            
            log_function_exit(self.logger, "cleanup_repository", result=True, execution_time=time.time() - start_time)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup repository {repository_path}: {e}", exc_info=True)
            log_function_exit(self.logger, "cleanup_repository", result=False, execution_time=time.time() - start_time)
            return False
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """
        Get statistics about temporary repositories.
        
        Returns:
            Dictionary with repository statistics
        """
        try:
            temp_repos = list(self.base_temp_dir.glob("repochat_*"))
            total_size = sum(self._calculate_directory_size(path) for path in temp_repos if path.is_dir())
            
            stats = {
                'temp_repositories_count': len(temp_repos),
                'total_size_mb': round(total_size, 2),
                'base_temp_dir': str(self.base_temp_dir),
                'repositories': [str(path.name) for path in temp_repos if path.is_dir()]
            }
            
            self.logger.debug("Repository statistics", extra={'extra_data': stats})
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get repository stats: {e}", exc_info=True)
            return {'error': str(e)}
    
    # Task 3.7: PR Diff Extraction Methods
    
    def extract_pr_diff(self, repository_path: str, pr_id: Optional[str] = None, 
                       base_branch: str = "main", head_branch: Optional[str] = None,
                       diff_file_path: Optional[str] = None) -> PRDiffInfo:
        """
        Extract PR diff information cho Task 3.7.
        
        Args:
            repository_path: Path to cloned repository
            pr_id: PR ID hoặc number (for metadata)
            base_branch: Base branch name (default: main)
            head_branch: Head branch name (nếu None sẽ dùng current branch)
            diff_file_path: Path to diff file (alternative to Git diff)
            
        Returns:
            PRDiffInfo: Structured diff information
        """
        start_time = time.time()
        log_function_entry(
            self.logger,
            "extract_pr_diff",
            repository_path=repository_path,
            pr_id=pr_id,
            base_branch=base_branch,
            head_branch=head_branch
        )
        
        try:
            # Initialize PRDiffInfo
            pr_diff_info = PRDiffInfo(
                pr_id=pr_id,
                base_branch=base_branch,
                head_branch=head_branch
            )
            
            if diff_file_path and os.path.exists(diff_file_path):
                # Option 1: Parse provided diff file
                self.logger.info(f"Parsing diff from file: {diff_file_path}")
                pr_diff_info = self._parse_diff_file(diff_file_path, pr_diff_info)
                
            else:
                # Option 2: Extract diff from Git repository
                self.logger.info(f"Extracting diff from Git repository: {repository_path}")
                pr_diff_info = self._extract_git_diff(repository_path, pr_diff_info)
            
            # Parse function changes từ diff
            pr_diff_info.function_changes = self._extract_function_changes(pr_diff_info)
            
            extraction_time = time.time() - start_time
            
            self.logger.info("PR diff extraction completed", extra={
                'extra_data': {
                    'pr_id': pr_id,
                    'changed_files_count': len(pr_diff_info.changed_files),
                    'function_changes_count': len(pr_diff_info.function_changes),
                    'extraction_time_ms': extraction_time * 1000,
                    'base_branch': base_branch,
                    'head_branch': head_branch
                }
            })
            
            log_performance_metric(
                self.logger,
                "pr_diff_extraction_time",
                extraction_time * 1000,
                "ms",
                pr_id=pr_id,
                files_count=len(pr_diff_info.changed_files)
            )
            
            log_function_exit(
                self.logger,
                "extract_pr_diff",
                result="success",
                execution_time=extraction_time
            )
            
            return pr_diff_info
            
        except Exception as e:
            error_msg = f"Error extracting PR diff: {e}"
            self.logger.error(error_msg, exc_info=True, extra={
                'extra_data': {
                    'repository_path': repository_path,
                    'pr_id': pr_id,
                    'error_type': type(e).__name__
                }
            })
            
            log_function_exit(
                self.logger,
                "extract_pr_diff",
                result="error",
                execution_time=time.time() - start_time
            )
            raise
    
    def _extract_git_diff(self, repository_path: str, pr_diff_info: PRDiffInfo) -> PRDiffInfo:
        """
        Extract diff từ Git repository.
        
        Args:
            repository_path: Path to repository
            pr_diff_info: PRDiffInfo object to populate
            
        Returns:
            Updated PRDiffInfo object
        """
        try:
            repo = Repo(repository_path)
            
            # Determine head branch
            if not pr_diff_info.head_branch:
                pr_diff_info.head_branch = repo.active_branch.name
            
            # Get diff between base and head
            base_commit = repo.commit(pr_diff_info.base_branch)
            head_commit = repo.commit(pr_diff_info.head_branch)
            
            # Get raw diff
            diff = repo.git.diff(base_commit, head_commit)
            pr_diff_info.raw_diff = diff
            
            # Get changed files
            changed_items = base_commit.diff(head_commit)
            pr_diff_info.changed_files = [item.a_path or item.b_path for item in changed_items]
            
            # Parse detailed file changes
            pr_diff_info.file_changes = self._parse_file_changes(changed_items)
            
            self.logger.debug(f"Extracted Git diff: {len(pr_diff_info.changed_files)} files changed")
            
            return pr_diff_info
            
        except Exception as e:
            self.logger.error(f"Error extracting Git diff: {e}", exc_info=True)
            # Return empty diff info for graceful handling
            return pr_diff_info
    
    def _parse_diff_file(self, diff_file_path: str, pr_diff_info: PRDiffInfo) -> PRDiffInfo:
        """
        Parse diff từ file.
        
        Args:
            diff_file_path: Path to diff file
            pr_diff_info: PRDiffInfo object to populate
            
        Returns:
            Updated PRDiffInfo object
        """
        try:
            with open(diff_file_path, 'r', encoding='utf-8') as f:
                diff_content = f.read()
            
            pr_diff_info.raw_diff = diff_content
            
            # Parse changed files từ diff
            pr_diff_info.changed_files = self._parse_changed_files_from_diff(diff_content)
            
            # Parse file changes
            pr_diff_info.file_changes = self._parse_file_changes_from_diff(diff_content)
            
            self.logger.debug(f"Parsed diff file: {len(pr_diff_info.changed_files)} files changed")
            
            return pr_diff_info
            
        except Exception as e:
            self.logger.error(f"Error parsing diff file: {e}", exc_info=True)
            return pr_diff_info
    
    def _parse_changed_files_from_diff(self, diff_content: str) -> List[str]:
        """
        Parse changed files từ raw diff content.
        
        Args:
            diff_content: Raw diff content
            
        Returns:
            List of changed file paths
        """
        changed_files = []
        
        # Pattern for diff headers: "diff --git a/file b/file"
        file_pattern = r'^diff --git a/(.+?) b/(.+?)$'
        
        for line in diff_content.split('\n'):
            match = re.match(file_pattern, line)
            if match:
                # Usually a_path and b_path are same unless renamed
                file_path = match.group(2)
                if file_path not in changed_files:
                    changed_files.append(file_path)
        
        return changed_files
    
    def _parse_file_changes(self, changed_items) -> Dict[str, Dict[str, Any]]:
        """
        Parse detailed file changes từ GitPython diff items.
        
        Args:
            changed_items: GitPython diff items
            
        Returns:
            Dictionary with file change details
        """
        file_changes = {}
        
        for item in changed_items:
            file_path = item.a_path or item.b_path
            
            change_info = {
                'change_type': item.change_type,  # A(dded), M(odified), D(eleted), R(enamed)
                'added_lines': 0,
                'deleted_lines': 0,
                'chunks': []
            }
            
            # Try to get line counts
            try:
                if item.diff:
                    diff_text = item.diff.decode('utf-8', errors='ignore')
                    added, deleted = self._count_diff_lines(diff_text)
                    change_info['added_lines'] = added
                    change_info['deleted_lines'] = deleted
            except Exception as e:
                self.logger.debug(f"Could not parse diff for {file_path}: {e}")
            
            file_changes[file_path] = change_info
        
        return file_changes
    
    def _parse_file_changes_from_diff(self, diff_content: str) -> Dict[str, Dict[str, Any]]:
        """
        Parse file changes từ raw diff content.
        
        Args:
            diff_content: Raw diff content
            
        Returns:
            Dictionary with file change details
        """
        file_changes = {}
        current_file = None
        
        for line in diff_content.split('\n'):
            # Check for file header
            if line.startswith('diff --git'):
                match = re.match(r'^diff --git a/(.+?) b/(.+?)$', line)
                if match:
                    current_file = match.group(2)
                    file_changes[current_file] = {
                        'change_type': 'M',  # Default to modified
                        'added_lines': 0,
                        'deleted_lines': 0,
                        'chunks': []
                    }
            
            elif current_file and line.startswith('+') and not line.startswith('+++'):
                file_changes[current_file]['added_lines'] += 1
            elif current_file and line.startswith('-') and not line.startswith('---'):
                file_changes[current_file]['deleted_lines'] += 1
        
        return file_changes
    
    def _count_diff_lines(self, diff_text: str) -> tuple:
        """
        Count added and deleted lines từ diff text.
        
        Args:
            diff_text: Diff text content
            
        Returns:
            Tuple of (added_lines, deleted_lines)
        """
        added = 0
        deleted = 0
        
        for line in diff_text.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                added += 1
            elif line.startswith('-') and not line.startswith('---'):
                deleted += 1
        
        return added, deleted
    
    def _extract_function_changes(self, pr_diff_info: PRDiffInfo) -> List[Dict[str, Any]]:
        """
        Extract function/method changes từ PR diff.
        
        Args:
            pr_diff_info: PRDiffInfo with raw diff
            
        Returns:
            List of function changes
        """
        function_changes = []
        
        if not pr_diff_info.raw_diff:
            return function_changes
        
        try:
            # Simple heuristic để tìm function changes
            # Tìm patterns như "def function_name", "function function_name", "class ClassName" etc.
            
            function_patterns = [
                r'^\+.*def\s+(\w+)\s*\(',     # Python functions  
                r'^\+.*function\s+(\w+)\s*\(',  # JavaScript functions
                r'^\+.*class\s+(\w+)\s*[{:]',   # Class definitions
                r'^\+.*public\s+\w+\s+(\w+)\s*\(',  # Java methods
                r'^\+.*private\s+\w+\s+(\w+)\s*\(',  # Java methods
                r'^\+.*protected\s+\w+\s+(\w+)\s*\(',  # Java methods
            ]
            
            current_file = None
            lines = pr_diff_info.raw_diff.split('\n')
            
            for i, line in enumerate(lines):
                # Track current file
                if line.startswith('diff --git'):
                    match = re.match(r'^diff --git a/(.+?) b/(.+?)$', line)
                    if match:
                        current_file = match.group(2)
                
                # Look for function changes
                if current_file and line.startswith('+'):
                    for pattern in function_patterns:
                        match = re.search(pattern, line)
                        if match:
                            function_name = match.group(1)
                            
                            function_changes.append({
                                'file': current_file,
                                'function_name': function_name,
                                'change_type': 'added',
                                'line_number': i + 1,
                                'line_content': line[1:].strip()  # Remove + prefix
                            })
                            break
                
                # Look for deleted functions
                elif current_file and line.startswith('-'):
                    for pattern in function_patterns:
                        # Replace + with - for deleted functions
                        deleted_pattern = pattern.replace('^\\+', '^\\-')
                        match = re.search(deleted_pattern, line)
                        if match:
                            function_name = match.group(1)
                            
                            function_changes.append({
                                'file': current_file,
                                'function_name': function_name,
                                'change_type': 'deleted',
                                'line_number': i + 1,
                                'line_content': line[1:].strip()  # Remove - prefix
                            })
                            break
            
            self.logger.debug(f"Extracted {len(function_changes)} function changes")
            
        except Exception as e:
            self.logger.error(f"Error extracting function changes: {e}", exc_info=True)
        
        return function_changes