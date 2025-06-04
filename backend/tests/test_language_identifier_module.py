"""
Unit tests for LanguageIdentifierModule - TEAM Data Acquisition

Tests cover:
- Language identification from file extensions
- Configuration file detection
- Statistical analysis and scoring
- Error handling for various scenarios
- Edge cases and comprehensive coverage
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from teams.data_acquisition.language_identifier_module import LanguageIdentifierModule


class TestLanguageIdentifierModule:
    """Test cases for LanguageIdentifierModule."""
    
    def setup_method(self):
        """Setup test environment for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.lang_identifier = LanguageIdentifierModule()
    
    def teardown_method(self):
        """Cleanup after each test."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_file(self, relative_path: str, content: str = "test content"):
        """Helper method to create test files."""
        file_path = self.temp_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path
    
    # ===== Initialization Tests =====
    
    def test_initialization(self):
        """Test LanguageIdentifierModule initialization."""
        assert self.lang_identifier is not None
        assert hasattr(self.lang_identifier, '_extension_mapping')
        assert hasattr(self.lang_identifier, '_config_files')
        assert hasattr(self.lang_identifier, '_ignore_directories')
        
        # Check some key mappings exist
        assert '.py' in self.lang_identifier._extension_mapping
        assert '.java' in self.lang_identifier._extension_mapping
        assert '.js' in self.lang_identifier._extension_mapping
        assert 'python' in self.lang_identifier._config_files
    
    # ===== Basic Language Detection Tests =====
    
    def test_identify_languages_python_project(self):
        """Test identifying Python project."""
        # Create Python files
        self._create_test_file("main.py", "print('Hello World')")
        self._create_test_file("utils.py", "def helper(): pass")
        self._create_test_file("requirements.txt", "requests==2.25.1")
        self._create_test_file("setup.py", "from setuptools import setup")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Assertions
        assert 'python' in languages
        assert isinstance(languages, list)
    
    def test_identify_languages_java_project(self):
        """Test identifying Java project."""
        # Create Java files
        self._create_test_file("src/main/java/Main.java", "public class Main {}")
        self._create_test_file("src/test/java/TestMain.java", "@Test public void test() {}")
        self._create_test_file("pom.xml", "<project></project>")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Assertions
        assert 'java' in languages
    
    def test_identify_languages_javascript_project(self):
        """Test identifying JavaScript project."""
        # Create JavaScript files
        self._create_test_file("index.js", "console.log('Hello');")
        self._create_test_file("components/App.jsx", "import React from 'react';")
        self._create_test_file("package.json", '{"name": "test-app"}')
        self._create_test_file("webpack.config.js", "module.exports = {};")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Assertions
        assert 'javascript' in languages
    
    def test_identify_languages_typescript_project(self):
        """Test identifying TypeScript project."""
        # Create TypeScript files
        self._create_test_file("src/index.ts", "interface User { name: string; }")
        self._create_test_file("src/components/App.tsx", "export const App = () => <div/>;")
        self._create_test_file("tsconfig.json", '{"compilerOptions": {}}')
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Assertions
        assert 'typescript' in languages
    
    def test_identify_languages_mixed_project(self):
        """Test identifying mixed language project."""
        # Create files for multiple languages
        self._create_test_file("backend/main.py", "# Python backend")
        self._create_test_file("frontend/app.js", "// JavaScript frontend")
        self._create_test_file("mobile/lib/main.dart", "// Dart mobile app")
        self._create_test_file("requirements.txt", "django==3.2")
        self._create_test_file("package.json", '{"scripts": {}}')
        self._create_test_file("pubspec.yaml", "name: mobile_app")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Assertions
        assert len(languages) >= 2
        assert 'python' in languages
        assert 'javascript' in languages or 'dart' in languages
    
    # ===== Configuration File Detection Tests =====
    
    def test_config_file_detection_python(self):
        """Test Python configuration file detection."""
        # Create Python config files
        self._create_test_file("requirements.txt", "requests==2.25.1")
        self._create_test_file("setup.py", "from setuptools import setup")
        self._create_test_file("pyproject.toml", "[tool.poetry]")
        self._create_test_file("__init__.py", "")
        
        # Test detailed analysis
        results = self.lang_identifier.get_detailed_analysis(str(self.temp_dir))
        
        # Assertions
        config_files = results['detailed_analysis']['config_files_found']
        assert 'python' in config_files
        python_configs = config_files['python']
        assert 'requirements.txt' in python_configs
        assert 'setup.py' in python_configs
    
    def test_config_file_detection_java(self):
        """Test Java configuration file detection."""
        # Create Java config files
        self._create_test_file("pom.xml", "<project></project>")
        self._create_test_file("build.gradle", "apply plugin: 'java'")
        self._create_test_file("gradle.properties", "org.gradle.jvmargs=-Xmx2048m")
        
        # Test detailed analysis
        results = self.lang_identifier.get_detailed_analysis(str(self.temp_dir))
        
        # Assertions
        config_files = results['detailed_analysis']['config_files_found']
        assert 'java' in config_files
        java_configs = config_files['java']
        assert 'pom.xml' in java_configs
        assert 'build.gradle' in java_configs
    
    def test_config_file_detection_dart(self):
        """Test Dart configuration file detection."""
        # Create Dart config files
        self._create_test_file("pubspec.yaml", "name: flutter_app")
        self._create_test_file("pubspec.lock", "# Generated by pub")
        self._create_test_file("analysis_options.yaml", "analyzer:")
        
        # Test detailed analysis
        results = self.lang_identifier.get_detailed_analysis(str(self.temp_dir))
        
        # Assertions
        config_files = results['detailed_analysis']['config_files_found']
        assert 'dart' in config_files
        dart_configs = config_files['dart']
        assert 'pubspec.yaml' in dart_configs
    
    # ===== Edge Cases Tests =====
    
    def test_identify_languages_empty_directory(self):
        """Test language identification on empty directory."""
        # Test with empty directory
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Assertions
        assert isinstance(languages, list)
        assert len(languages) == 0
    
    def test_identify_languages_only_ignored_files(self):
        """Test with only ignored files."""
        # Create only ignored files
        self._create_test_file("app.min.js", "// Minified")
        self._create_test_file("types.d.ts", "// Declaration file")
        self._create_test_file("source.map", "// Source map")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Should not detect languages from ignored files
        assert len(languages) == 0
    
    def test_identify_languages_ignored_directories(self):
        """Test that ignored directories are skipped."""
        # Create files in ignored directories
        self._create_test_file("node_modules/package/index.js", "// Should be ignored")
        self._create_test_file("__pycache__/module.py", "// Should be ignored")
        self._create_test_file(".git/config", "// Should be ignored")
        
        # Create valid files
        self._create_test_file("src/main.py", "print('hello')")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Should only detect from valid files
        assert 'python' in languages
        assert len(languages) == 1
    
    def test_identify_languages_with_subdirectories(self):
        """Test language identification with nested subdirectories."""
        # Create nested structure
        self._create_test_file("src/main/java/com/example/Main.java", "public class Main {}")
        self._create_test_file("src/test/java/com/example/TestMain.java", "@Test void test() {}")
        self._create_test_file("frontend/src/components/App.js", "export default App;")
        self._create_test_file("backend/api/views.py", "from django.http import HttpResponse")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Should detect all languages
        assert 'java' in languages
        assert 'javascript' in languages
        assert 'python' in languages
    
    # ===== Error Handling Tests =====
    
    def test_identify_languages_nonexistent_path(self):
        """Test handling of non-existent path."""
        nonexistent_path = str(self.temp_dir / "nonexistent")
        
        with pytest.raises(ValueError) as exc_info:
            self.lang_identifier.identify_languages(nonexistent_path)
        
        assert "does not exist" in str(exc_info.value)
    
    def test_identify_languages_file_not_directory(self):
        """Test handling when path is a file, not directory."""
        # Create a file
        test_file = self._create_test_file("test.py", "print('hello')")
        
        with pytest.raises(ValueError) as exc_info:
            self.lang_identifier.identify_languages(str(test_file))
        
        assert "not a directory" in str(exc_info.value)
    
    @patch('builtins.open')
    def test_file_reading_permission_error(self, mock_open):
        """Test handling of permission errors when reading files."""
        # Setup mock to raise PermissionError
        mock_open.side_effect = PermissionError("Permission denied")
        
        # Create test file
        self._create_test_file("test.py", "print('hello')")
        
        # Should not crash, just skip the problematic file
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Should still detect Python based on extension
        assert 'python' in languages
    
    # ===== Statistical Analysis Tests =====
    
    def test_detailed_analysis_statistics(self):
        """Test detailed statistical analysis."""
        # Create project with known file counts
        self._create_test_file("main.py", "print('hello')")
        self._create_test_file("utils.py", "def helper(): pass")
        self._create_test_file("app.js", "console.log('hi');")
        self._create_test_file("style.css", "body { margin: 0; }")
        self._create_test_file("README.md", "# Project")
        
        # Test detailed analysis
        results = self.lang_identifier.get_detailed_analysis(str(self.temp_dir))
        
        # Check structure
        assert 'primary_languages' in results
        assert 'detailed_analysis' in results
        assert 'summary' in results
        
        # Check detailed analysis structure
        analysis = results['detailed_analysis']
        assert 'language_file_counts' in analysis
        assert 'language_percentages' in analysis
        assert 'total_files_analyzed' in analysis
        
        # Check file counts
        file_counts = analysis['language_file_counts']
        assert file_counts['python'] == 2
        assert file_counts['javascript'] == 1
        assert file_counts['css'] == 1
        assert file_counts['markdown'] == 1
        
        # Check percentages add up correctly
        percentages = analysis['language_percentages']
        total_percentage = sum(percentages.values())
        assert 95 <= total_percentage <= 105  # Allow for rounding
    
    def test_language_scoring_with_config_files(self):
        """Test that config files boost language scores."""
        # Create Python project with config files
        self._create_test_file("main.py", "print('hello')")
        self._create_test_file("requirements.txt", "requests==2.25.1")
        self._create_test_file("setup.py", "from setuptools import setup")
        
        # Create JavaScript file without config
        self._create_test_file("script.js", "console.log('hi');")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Python should be ranked higher due to config files
        assert languages[0] == 'python'
        assert 'javascript' in languages
    
    def test_line_counting_functionality(self):
        """Test line counting for code analysis."""
        # Create files with known line counts
        python_content = "\n".join([
            "import os",
            "import sys",
            "",
            "def main():",
            "    print('Hello World')",
            "    return 0",
            "",
            "if __name__ == '__main__':",
            "    main()"
        ])
        self._create_test_file("main.py", python_content)
        
        # Test detailed analysis
        results = self.lang_identifier.get_detailed_analysis(str(self.temp_dir))
        
        # Check line counts
        line_counts = results['detailed_analysis']['language_line_counts']
        assert 'python' in line_counts
        assert line_counts['python'] == 9  # Should count all lines including empty
    
    # ===== Comprehensive Language Support Tests =====
    
    def test_web_development_languages(self):
        """Test detection of web development languages."""
        # Create web development files
        self._create_test_file("index.html", "<html></html>")
        self._create_test_file("style.css", "body { margin: 0; }")
        self._create_test_file("style.scss", "$color: blue;")
        self._create_test_file("app.vue", "<template></template>")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Check detection
        detected_web_langs = [lang for lang in languages if lang in ['html', 'css', 'scss', 'vue']]
        assert len(detected_web_langs) >= 2
    
    def test_mobile_development_languages(self):
        """Test detection of mobile development languages."""
        # Create mobile files
        self._create_test_file("lib/main.dart", "void main() {}")
        self._create_test_file("ios/Runner/AppDelegate.swift", "import UIKit")
        self._create_test_file("android/MainActivity.java", "public class MainActivity {}")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Check mobile languages detected
        mobile_langs = [lang for lang in languages if lang in ['dart', 'swift', 'java']]
        assert len(mobile_langs) >= 2
    
    def test_system_programming_languages(self):
        """Test detection of system programming languages."""
        # Create system programming files
        self._create_test_file("main.c", "#include <stdio.h>")
        self._create_test_file("utils.cpp", "#include <iostream>")
        self._create_test_file("lib.rs", "fn main() {}")
        self._create_test_file("server.go", "package main")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Check system languages detected
        system_langs = [lang for lang in languages if lang in ['c', 'cpp', 'rust', 'go']]
        assert len(system_langs) >= 2
    
    # ===== Primary Language Extraction Tests =====
    
    def test_primary_language_threshold(self):
        """Test that languages below threshold are filtered out."""
        # Create project with one dominant language and few minority files
        for i in range(10):
            self._create_test_file(f"module_{i}.py", f"# Python file {i}")
        
        # Add single files of other languages
        self._create_test_file("script.js", "// Single JS file")
        self._create_test_file("style.css", "/* Single CSS file */")
        
        # Test
        languages = self.lang_identifier.identify_languages(str(self.temp_dir))
        
        # Python should dominate, others might be filtered out
        assert 'python' in languages
        assert languages[0] == 'python'  # Should be first
    
    def test_get_detailed_analysis_comprehensive(self):
        """Test comprehensive detailed analysis output."""
        # Create a realistic project structure
        self._create_test_file("src/main.py", "# Main application")
        self._create_test_file("src/utils.py", "# Utilities")
        self._create_test_file("tests/test_main.py", "# Tests")
        self._create_test_file("requirements.txt", "pytest==6.0")
        self._create_test_file("setup.py", "from setuptools import setup")
        self._create_test_file("README.md", "# Documentation")
        
        # Test
        results = self.lang_identifier.get_detailed_analysis(str(self.temp_dir))
        
        # Validate structure
        assert all(key in results for key in ['primary_languages', 'detailed_analysis', 'summary'])
        
        # Validate summary
        summary = results['summary']
        assert 'total_languages_detected' in summary
        assert 'primary_languages_count' in summary
        assert 'has_config_files' in summary
        assert summary['has_config_files'] is True  # Should detect Python config files
        
        # Validate primary languages
        assert 'python' in results['primary_languages'] 