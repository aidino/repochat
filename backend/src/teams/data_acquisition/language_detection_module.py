"""
Mock Language Detection Module for Full Workflow Demo

Simple implementation to detect programming languages
in a directory based on file extensions.
"""

import os
import logging
from typing import List, Dict, Set
from pathlib import Path


class LanguageDetectionModule:
    """Mock language detection for identifying programming languages."""
    
    def __init__(self):
        """Initialize language detection module."""
        self.logger = logging.getLogger(f"repochat.data_acquisition.lang_detection")
        
        # File extension to language mapping
        self.extension_map = {
            '.java': 'java',
            '.py': 'python',
            '.kt': 'kotlin',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.dart': 'dart',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.swift': 'swift'
        }
    
    def detect_languages_in_directory(self, directory_path: str) -> List[str]:
        """
        Detect programming languages in a directory.
        
        Args:
            directory_path: Path to directory to analyze
            
        Returns:
            List of detected programming language names
        """
        try:
            if not os.path.exists(directory_path):
                self.logger.error(f"Directory does not exist: {directory_path}")
                return []
            
            detected_languages: Set[str] = set()
            file_count = 0
            
            # Walk through directory
            for root, dirs, files in os.walk(directory_path):
                # Skip hidden directories and common non-source directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                    'node_modules', 'target', 'build', '.git', '__pycache__', 'dist'
                ]]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    
                    file_path = Path(file)
                    extension = file_path.suffix.lower()
                    
                    if extension in self.extension_map:
                        detected_languages.add(self.extension_map[extension])
                        file_count += 1
            
            detected_list = sorted(list(detected_languages))
            
            self.logger.info(f"Detected {len(detected_list)} languages from {file_count} files")
            self.logger.info(f"Languages: {detected_list}")
            
            return detected_list
            
        except Exception as e:
            self.logger.error(f"Language detection error: {e}")
            return []
    
    def get_file_count_by_language(self, directory_path: str) -> Dict[str, int]:
        """
        Get file count statistics by programming language.
        
        Args:
            directory_path: Path to directory to analyze
            
        Returns:
            Dictionary mapping language names to file counts
        """
        try:
            if not os.path.exists(directory_path):
                return {}
            
            language_counts: Dict[str, int] = {}
            
            for root, dirs, files in os.walk(directory_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                    'node_modules', 'target', 'build', '.git', '__pycache__', 'dist'
                ]]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    
                    file_path = Path(file)
                    extension = file_path.suffix.lower()
                    
                    if extension in self.extension_map:
                        language = self.extension_map[extension]
                        language_counts[language] = language_counts.get(language, 0) + 1
            
            return language_counts
            
        except Exception as e:
            self.logger.error(f"File count analysis error: {e}")
            return {} 