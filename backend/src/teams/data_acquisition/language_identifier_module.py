"""
LanguageIdentifierModule - TEAM Data Acquisition

Identifies programming languages in cloned repositories based on file extensions,
configuration files, and statistical analysis for RepoChat v1.0.
"""

import os
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from collections import defaultdict, Counter
import json

from shared.utils.logging_config import (
    get_logger,
    log_function_entry, 
    log_function_exit,
    log_performance_metric
)


class LanguageIdentifierModule:
    """
    Module for identifying programming languages in code repositories.
    
    Provides comprehensive language detection based on:
    - File extensions analysis
    - Configuration files detection  
    - Statistical analysis with percentages
    - Comprehensive error handling and logging
    """
    
    def __init__(self):
        """Initialize LanguageIdentifierModule with language mappings."""
        self.logger = get_logger("data_acquisition.language_identifier")
        
        log_function_entry(self.logger, "__init__")
        
        # File extension to language mapping
        self._extension_mapping = {
            # Web Development
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript', 
            '.tsx': 'typescript',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less',
            '.vue': 'vue',
            
            # Python
            '.py': 'python',
            '.pyx': 'python',
            '.pyi': 'python',
            '.pyw': 'python',
            
            # Java/JVM Languages
            '.java': 'java',
            '.kt': 'kotlin',
            '.kts': 'kotlin',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.groovy': 'groovy',
            
            # Mobile Development
            '.dart': 'dart',
            '.swift': 'swift',
            '.m': 'objective-c',
            '.mm': 'objective-c',
            
            # C/C++ Family
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.hpp': 'cpp',
            '.hxx': 'cpp',
            
            # .NET
            '.cs': 'csharp',
            '.vb': 'vb.net',
            '.fs': 'fsharp',
            
            # Other Popular Languages
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.pl': 'perl',
            '.r': 'r',
            '.R': 'r',
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.fish': 'shell',
            '.ps1': 'powershell',
            '.lua': 'lua',
            
            # Configuration & Data
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            
            # Documentation
            '.md': 'markdown',
            '.rst': 'restructuredtext',
            '.tex': 'latex',
        }
        
        # Configuration files for language detection
        self._config_files = {
            'python': [
                'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 
                'poetry.lock', 'conda.yml', 'environment.yml', '__init__.py'
            ],
            'javascript': [
                'package.json', 'package-lock.json', 'yarn.lock', 'webpack.config.js',
                'babel.config.js', '.babelrc', 'tsconfig.json', 'jest.config.js'
            ],
            'typescript': [
                'tsconfig.json', 'tslint.json', 'angular.json', 'nest-cli.json'
            ],
            'java': [
                'pom.xml', 'build.gradle', 'gradle.properties', 'settings.gradle',
                'build.xml', 'ivy.xml', 'maven-wrapper.properties'
            ],
            'kotlin': [
                'build.gradle.kts', 'settings.gradle.kts', 'gradle.properties'
            ],
            'dart': [
                'pubspec.yaml', 'pubspec.lock', 'analysis_options.yaml'
            ],
            'swift': [
                'Package.swift', 'Podfile', 'Podfile.lock', 'Cartfile', 
                'project.pbxproj', '*.xcodeproj', '*.xcworkspace'
            ],
            'go': [
                'go.mod', 'go.sum', 'Gopkg.toml', 'Gopkg.lock', 'glide.yaml'
            ],
            'rust': [
                'Cargo.toml', 'Cargo.lock'
            ],
            'ruby': [
                'Gemfile', 'Gemfile.lock', 'Rakefile', '*.gemspec'
            ],
            'php': [
                'composer.json', 'composer.lock', 'phpunit.xml', 'artisan'
            ],
            'csharp': [
                '*.csproj', '*.sln', '*.vbproj', 'nuget.config', 'packages.config'
            ],
            'cpp': [
                'CMakeLists.txt', 'Makefile', 'configure', 'configure.ac',
                'meson.build', 'conanfile.txt', 'vcpkg.json'
            ],
            'c': [
                'Makefile', 'configure', 'configure.ac', 'CMakeLists.txt'
            ]
        }
        
        # Common directories to ignore during analysis
        self._ignore_directories = {
            '.git', '.svn', '.hg', '.bzr',  # Version control
            'node_modules', '__pycache__', '.pytest_cache',  # Dependencies/Cache
            'build', 'dist', 'target', 'bin', 'obj',  # Build outputs
            '.idea', '.vscode', '.vs',  # IDE files
            'coverage', '.coverage', '.nyc_output',  # Coverage reports
            'vendor', 'deps', 'packages',  # Dependencies
            '.gradle', '.maven',  # Build tool caches
            'logs', 'log', 'tmp', 'temp',  # Temporary files
        }
        
        # File patterns to ignore
        self._ignore_file_patterns = {
            '.min.js', '.min.css',  # Minified files
            '.d.ts',  # TypeScript declaration files (for analysis purposes)
            '.map',  # Source maps
            '.lock',  # Lock files (counted separately)
        }
        
        self.logger.info("LanguageIdentifierModule initialized", extra={
            'extra_data': {
                'supported_languages': len(set(self._extension_mapping.values())),
                'file_extensions': len(self._extension_mapping),
                'config_file_patterns': sum(len(files) for files in self._config_files.values())
            }
        })
        
        log_function_exit(self.logger, "__init__", result="success")
    
    def identify_languages(self, repository_path: str) -> List[str]:
        """
        Identify programming languages in the given repository.
        
        Args:
            repository_path: Path to the cloned repository directory
            
        Returns:
            List of detected programming languages, sorted by frequency
            
        Raises:
            ValueError: If repository path is invalid
            OSError: If unable to read repository contents
        """
        start_time = time.time()
        
        log_function_entry(self.logger, "identify_languages", repository_path=repository_path)
        
        self.logger.info(f"Starting language identification for: {repository_path}")
        
        # Validation
        repo_path = Path(repository_path)
        if not repo_path.exists():
            error_msg = f"Repository path does not exist: {repository_path}"
            self.logger.error(error_msg)
            log_function_exit(self.logger, "identify_languages", result="path_not_found")
            raise ValueError(error_msg)
        
        if not repo_path.is_dir():
            error_msg = f"Repository path is not a directory: {repository_path}"
            self.logger.error(error_msg)
            log_function_exit(self.logger, "identify_languages", result="not_directory")
            raise ValueError(error_msg)
        
        try:
            # Perform comprehensive analysis
            analysis_results = self._analyze_repository(repo_path)
            
            # Extract detected languages sorted by frequency
            detected_languages = self._extract_primary_languages(analysis_results)
            
            execution_time = time.time() - start_time
            
            log_performance_metric(
                self.logger,
                "language_identification_time",
                execution_time * 1000,
                "ms",
                repository_path=repository_path,
                languages_count=len(detected_languages)
            )
            
            self.logger.info(f"Language identification completed", extra={
                'extra_data': {
                    'repository_path': repository_path,
                    'detected_languages': detected_languages,
                    'analysis_results': analysis_results,
                    'execution_time_ms': execution_time * 1000
                }
            })
            
            log_function_exit(
                self.logger, 
                "identify_languages", 
                result=detected_languages, 
                execution_time=execution_time
            )
            
            return detected_languages
            
        except PermissionError as e:
            error_msg = f"Permission denied reading repository: {e}"
            self.logger.error(error_msg, exc_info=True)
            log_function_exit(self.logger, "identify_languages", result="permission_error")
            raise OSError(error_msg)
            
        except OSError as e:
            error_msg = f"Error reading repository contents: {e}"
            self.logger.error(error_msg, exc_info=True)
            log_function_exit(self.logger, "identify_languages", result="os_error")
            raise
            
        except Exception as e:
            error_msg = f"Unexpected error during language identification: {e}"
            self.logger.error(error_msg, exc_info=True)
            log_function_exit(self.logger, "identify_languages", result="unexpected_error")
            raise
    
    def _analyze_repository(self, repo_path: Path) -> Dict[str, any]:
        """
        Perform comprehensive repository analysis.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with analysis results
        """
        analysis_start = time.time()
        
        # Initialize counters
        language_file_counts = defaultdict(int)
        language_line_counts = defaultdict(int)
        config_files_found = defaultdict(list)
        total_files = 0
        total_lines = 0
        
        self.logger.debug(f"Starting repository analysis: {repo_path}")
        
        # Walk through repository
        for root, dirs, files in os.walk(repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in self._ignore_directories]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip ignored file patterns
                if any(pattern in file.lower() for pattern in self._ignore_file_patterns):
                    continue
                
                total_files += 1
                
                # Analyze file extension
                extension = file_path.suffix.lower()
                if extension in self._extension_mapping:
                    language = self._extension_mapping[extension]
                    language_file_counts[language] += 1
                    
                    # Count lines for programming languages (not config/docs)
                    if language in ['python', 'java', 'javascript', 'typescript', 'kotlin', 
                                   'dart', 'swift', 'cpp', 'c', 'csharp', 'go', 'rust', 'ruby', 'php']:
                        try:
                            line_count = self._count_lines(file_path)
                            language_line_counts[language] += line_count
                            total_lines += line_count
                        except Exception as e:
                            self.logger.warning(f"Could not count lines in {file_path}: {e}")
                
                # Check for configuration files
                self._check_config_files(file, config_files_found)
        
        # Calculate percentages
        language_percentages = {}
        if total_files > 0:
            for language, count in language_file_counts.items():
                language_percentages[language] = round((count / total_files) * 100, 2)
        
        analysis_time = time.time() - analysis_start
        
        results = {
            'language_file_counts': dict(language_file_counts),
            'language_line_counts': dict(language_line_counts),
            'language_percentages': language_percentages,
            'config_files_found': dict(config_files_found),
            'total_files_analyzed': total_files,
            'total_lines_counted': total_lines,
            'analysis_time_ms': analysis_time * 1000
        }
        
        self.logger.debug(f"Repository analysis completed", extra={
            'extra_data': results
        })
        
        return results
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file safely."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            # Try with different encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return sum(1 for _ in f)
                except Exception:
                    continue
            return 0
    
    def _check_config_files(self, filename: str, config_files_found: Dict) -> None:
        """Check if file matches known configuration patterns."""
        filename_lower = filename.lower()
        
        for language, config_patterns in self._config_files.items():
            for pattern in config_patterns:
                pattern_lower = pattern.lower()
                
                # Exact match
                if filename_lower == pattern_lower:
                    config_files_found[language].append(filename)
                    break
                    
                # Pattern with wildcards
                elif '*' in pattern_lower:
                    import fnmatch
                    if fnmatch.fnmatch(filename_lower, pattern_lower):
                        config_files_found[language].append(filename)
                        break
    
    def _extract_primary_languages(self, analysis_results: Dict) -> List[str]:
        """
        Extract primary programming languages from analysis results.
        
        Args:
            analysis_results: Results from repository analysis
            
        Returns:
            List of languages sorted by significance
        """
        language_scores = {}
        
        # Score based on file counts (weight: 40%)
        file_counts = analysis_results['language_file_counts']
        if file_counts:
            max_files = max(file_counts.values())
            for language, count in file_counts.items():
                language_scores[language] = (count / max_files) * 0.4
        
        # Score based on line counts (weight: 40%)
        line_counts = analysis_results['language_line_counts']
        if line_counts:
            max_lines = max(line_counts.values())
            # Only add line count scoring if max_lines > 0 to avoid division by zero
            if max_lines > 0:
                for language, count in line_counts.items():
                    current_score = language_scores.get(language, 0)
                    language_scores[language] = current_score + (count / max_lines) * 0.4
        
        # Bonus for configuration files (weight: 20%)
        config_files = analysis_results['config_files_found']
        for language, files in config_files.items():
            if files:  # Has config files
                current_score = language_scores.get(language, 0)
                language_scores[language] = current_score + 0.2
        
        # Filter out non-programming languages for primary list (including web development)
        programming_languages = {
            'python', 'java', 'javascript', 'typescript', 'kotlin', 'dart', 
            'swift', 'cpp', 'c', 'csharp', 'go', 'rust', 'ruby', 'php',
            'scala', 'clojure', 'groovy', 'objective-c', 'vb.net', 'fsharp',
            'perl', 'r', 'shell', 'powershell', 'lua',
            # Include web development languages
            'html', 'css', 'scss', 'sass', 'less', 'vue'
        }
        
        # Sort by score and filter
        primary_languages = [
            lang for lang, score in sorted(
                language_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            if lang in programming_languages and score > 0.1  # Minimum 10% threshold
        ]
        
        self.logger.debug(f"Primary languages extracted", extra={
            'extra_data': {
                'language_scores': language_scores,
                'primary_languages': primary_languages,
                'threshold': 0.1
            }
        })
        
        return primary_languages
    
    def get_detailed_analysis(self, repository_path: str) -> Dict[str, any]:
        """
        Get detailed language analysis including statistics.
        
        Args:
            repository_path: Path to repository
            
        Returns:
            Detailed analysis results
        """
        log_function_entry(self.logger, "get_detailed_analysis", repository_path=repository_path)
        
        repo_path = Path(repository_path)
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repository_path}")
        
        analysis_results = self._analyze_repository(repo_path)
        primary_languages = self._extract_primary_languages(analysis_results)
        
        detailed_results = {
            'primary_languages': primary_languages,
            'detailed_analysis': analysis_results,
            'summary': {
                'total_languages_detected': len(analysis_results['language_file_counts']),
                'primary_languages_count': len(primary_languages),
                'has_config_files': len(analysis_results['config_files_found']) > 0,
                'repository_path': repository_path
            }
        }
        
        log_function_exit(self.logger, "get_detailed_analysis", result="success")
        return detailed_results 