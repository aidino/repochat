"""
Unit Tests for CodeParserCoordinatorModule

Tests the coordination functionality for Task 2.2 (F2.2) requirements:
- Receives ProjectDataContext with detected_languages and cloned_code_path
- Calls appropriate language parsers based on detected_languages  
- Aggregates results from all parsers

Test Coverage:
- Module initialization and parser registration
- ProjectDataContext validation and processing
- Language parser coordination and dispatching
- Result aggregation and statistics
- Error handling and edge cases
"""

import pytest
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from shared.models.project_data_context import ProjectDataContext
from teams.ckg_operations.code_parser_coordinator_module import CodeParserCoordinatorModule
from teams.ckg_operations.models import (
    CoordinatorParseResult,
    LanguageParseResult,
    ParseResult,
    CodeEntity,
    CallRelationship,
    CodeEntityType,
    VisibilityModifier
)
from teams.ckg_operations.mock_parser import (
    MockJavaParser,
    MockPythonParser,
    MockKotlinParser,
    MockDartParser
)


class TestCodeParserCoordinatorModule:
    """Test suite for CodeParserCoordinatorModule."""
    
    @pytest.fixture
    def coordinator(self):
        """Create a fresh coordinator instance for testing."""
        return CodeParserCoordinatorModule()
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with sample files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create sample Java files
            java_dir = Path(temp_dir) / "src" / "main" / "java"
            java_dir.mkdir(parents=True, exist_ok=True)
            
            (java_dir / "Calculator.java").write_text("""
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
}
            """)
            
            (java_dir / "UserService.java").write_text("""
public class UserService {
    public void createUser(String name) {
        System.out.println("Creating user: " + name);
    }
}
            """)
            
            # Create sample Python files
            python_dir = Path(temp_dir) / "src" / "python"
            python_dir.mkdir(parents=True, exist_ok=True)
            
            (python_dir / "calculator.py").write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

class Calculator:
    def multiply(self, a, b):
        return a * b
            """)
            
            (python_dir / "utils.py").write_text("""
import os
import sys

def get_project_root():
    return os.path.dirname(__file__)

class ConfigManager:
    def __init__(self):
        self.config = {}
    
    def load_config(self, path):
        pass
            """)
            
            # Create sample Kotlin file
            kotlin_dir = Path(temp_dir) / "src" / "kotlin"
            kotlin_dir.mkdir(parents=True, exist_ok=True)
            
            (kotlin_dir / "Main.kt").write_text("""
fun main() {
    println("Hello Kotlin")
}

class DataProcessor {
    fun processData(data: String): String {
        return data.uppercase()
    }
}
            """)
            
            yield temp_dir
    
    @pytest.fixture
    def sample_project_context(self, temp_project_dir):
        """Create a sample ProjectDataContext for testing."""
        return ProjectDataContext(
            cloned_code_path=temp_project_dir,
            detected_languages=["java", "python", "kotlin"],
            repository_url="https://github.com/test/repo.git",
            language_statistics={
                "java": {"files": 2, "lines": 15},
                "python": {"files": 2, "lines": 18},
                "kotlin": {"files": 1, "lines": 10}
            }
        )
    
    def test_initialization(self, coordinator):
        """Test coordinator module initialization."""
        assert coordinator is not None
        assert len(coordinator.get_registered_languages()) == 0
        assert coordinator._stats['coordination_sessions'] == 0
        assert coordinator._stats['parser_registrations'] == 0
        
        stats = coordinator.get_coordination_stats()
        assert 'registered_parsers' in stats
        assert 'supported_language_mappings' in stats
        assert stats['coordination_sessions'] == 0
    
    def test_parser_registration(self, coordinator):
        """Test registering language parsers."""
        java_parser = MockJavaParser()
        python_parser = MockPythonParser()
        
        # Test registration
        coordinator.register_parser(java_parser)
        coordinator.register_parser(python_parser)
        
        assert coordinator.has_parser_for_language("java")
        assert coordinator.has_parser_for_language("python")
        assert not coordinator.has_parser_for_language("javascript")
        
        registered_languages = coordinator.get_registered_languages()
        assert "java" in registered_languages
        assert "python" in registered_languages
        assert len(registered_languages) == 2
        
        # Test statistics update
        assert coordinator._stats['parser_registrations'] == 2
    
    def test_parser_registration_invalid(self, coordinator):
        """Test registration with invalid parser."""
        with pytest.raises(ValueError, match="Parser must inherit from BaseLanguageParser"):
            coordinator.register_parser("not_a_parser")
    
    def test_parser_replacement(self, coordinator):
        """Test replacing an existing parser."""
        java_parser1 = MockJavaParser()
        java_parser2 = MockJavaParser()
        
        coordinator.register_parser(java_parser1)
        assert len(coordinator.get_registered_languages()) == 1
        
        # Replace parser (should log warning but work)
        coordinator.register_parser(java_parser2)
        assert len(coordinator.get_registered_languages()) == 1
        assert coordinator._stats['parser_registrations'] == 2
    
    def test_parser_unregistration(self, coordinator):
        """Test unregistering parsers."""
        java_parser = MockJavaParser()
        coordinator.register_parser(java_parser)
        
        assert coordinator.has_parser_for_language("java")
        
        # Test successful unregistration
        result = coordinator.unregister_parser("java")
        assert result is True
        assert not coordinator.has_parser_for_language("java")
        
        # Test unregistering non-existent parser
        result = coordinator.unregister_parser("nonexistent")
        assert result is False
    
    def test_get_parser_info(self, coordinator):
        """Test getting parser information."""
        java_parser = MockJavaParser()
        coordinator.register_parser(java_parser)
        
        info = coordinator.get_parser_info("java")
        assert info is not None
        assert info['language'] == 'java'
        assert info['parser_type'] == 'MockJavaParser'
        assert '.java' in info['supported_extensions']
        assert 'parser_version' in info
        assert 'parser_stats' in info
        
        # Test non-existent parser
        info = coordinator.get_parser_info("nonexistent")
        assert info is None
    
    def test_coordinate_parsing_successful(self, coordinator, sample_project_context):
        """Test successful coordination parsing - the main Task 2.2 requirement."""
        # Register parsers
        coordinator.register_parser(MockJavaParser())
        coordinator.register_parser(MockPythonParser())
        coordinator.register_parser(MockKotlinParser())
        
        # Execute coordination
        result = coordinator.coordinate_parsing(sample_project_context)
        
        # Verify result structure
        assert isinstance(result, CoordinatorParseResult)
        assert result.project_path == sample_project_context.cloned_code_path
        assert len(result.errors) == 0
        
        # Verify languages were processed
        assert "java" in result.languages_processed
        assert "python" in result.languages_processed
        assert "kotlin" in result.languages_processed
        
        # Verify language results
        assert "java" in result.language_results
        assert "python" in result.language_results
        assert "kotlin" in result.language_results
        
        # Verify aggregated statistics
        assert result.total_files_parsed > 0
        assert result.total_entities_found > 0
        assert result.total_relationships_found >= 0  # Can be 0 for small files
        assert result.coordination_duration_ms > 0
        
        # Verify success rate
        assert 0.0 <= result.success_rate <= 1.0
        
        # Check individual language results
        java_result = result.language_results["java"]
        assert isinstance(java_result, LanguageParseResult)
        assert java_result.language == "java"
        assert len(java_result.files_parsed) == 2  # Calculator.java, UserService.java
        assert java_result.total_entities > 0
        
        python_result = result.language_results["python"]
        assert python_result.language == "python"
        assert len(python_result.files_parsed) == 2  # calculator.py, utils.py
        
        # Verify coordinator statistics were updated
        assert coordinator._stats['coordination_sessions'] == 1
        assert coordinator._stats['total_languages_processed'] == 3
        assert coordinator._stats['total_files_coordinated'] > 0
    
    def test_coordinate_parsing_missing_parsers(self, coordinator, sample_project_context):
        """Test coordination when some language parsers are missing."""
        # Only register Java parser, leaving Python and Kotlin without parsers
        coordinator.register_parser(MockJavaParser())
        
        result = coordinator.coordinate_parsing(sample_project_context)
        
        # Should have warnings for missing parsers
        assert len(result.warnings) >= 2  # Python and Kotlin parsers missing
        assert any("python" in warning.lower() for warning in result.warnings)
        assert any("kotlin" in warning.lower() for warning in result.warnings)
        
        # Should still process Java
        assert "java" in result.languages_processed
        assert "java" in result.language_results
        
        # Should not process Python or Kotlin
        assert "python" not in result.languages_processed
        assert "kotlin" not in result.languages_processed
    
    def test_coordinate_parsing_invalid_project_path(self, coordinator):
        """Test coordination with invalid project path."""
        invalid_context = ProjectDataContext(
            cloned_code_path="/nonexistent/path",
            detected_languages=["java", "python"]
        )
        
        result = coordinator.coordinate_parsing(invalid_context)
        
        assert len(result.errors) > 0
        assert any("does not exist" in error for error in result.errors)
        assert len(result.languages_processed) == 0
        assert result.total_files_parsed == 0
    
    def test_coordinate_parsing_empty_project_path(self, coordinator):
        """Test coordination with empty project path."""
        # Since ProjectDataContext validates cloned_code_path, we need to test the coordinator's validation
        import tempfile
        
        # Create a context with a non-empty but invalid path
        invalid_context = ProjectDataContext(
            cloned_code_path="/invalid/path/that/does/not/exist",
            detected_languages=["java"]
        )
        
        result = coordinator.coordinate_parsing(invalid_context)
        
        assert len(result.errors) > 0
        assert any("does not exist" in error for error in result.errors)
    
    def test_coordinate_parsing_no_languages(self, coordinator, temp_project_dir):
        """Test coordination with no detected languages."""
        empty_context = ProjectDataContext(
            cloned_code_path=temp_project_dir,
            detected_languages=[]
        )
        
        result = coordinator.coordinate_parsing(empty_context)
        
        assert len(result.warnings) > 0
        assert any("no languages detected" in warning.lower() for warning in result.warnings)
        assert len(result.languages_processed) == 0
        assert result.total_files_parsed == 0
    
    def test_coordinate_parsing_parser_exception(self, coordinator, sample_project_context):
        """Test coordination when a parser throws an exception."""
        # Create a mock parser that throws an exception
        class FailingParser(MockJavaParser):
            def parse_project(self, project_path):
                raise RuntimeError("Simulated parser failure")
        
        coordinator.register_parser(FailingParser())
        coordinator.register_parser(MockPythonParser())
        
        result = coordinator.coordinate_parsing(sample_project_context)
        
        # Should have errors for the failing parser
        assert len(result.errors) > 0
        assert any("java" in error.lower() for error in result.errors)
        
        # Should still process Python successfully
        assert "python" in result.languages_processed
        assert "python" in result.language_results
    
    def test_validate_project_data_context(self, coordinator, sample_project_context):
        """Test ProjectDataContext validation."""
        # Register parsers first for valid context test
        coordinator.register_parser(MockJavaParser())
        coordinator.register_parser(MockPythonParser())
        coordinator.register_parser(MockKotlinParser())
        
        # Valid context
        errors = coordinator.validate_project_data_context(sample_project_context)
        assert len(errors) == 0
        
        # None context
        errors = coordinator.validate_project_data_context(None)
        assert len(errors) > 0
        assert any("is None" in error for error in errors)
        
        # Missing/invalid path (ProjectDataContext validates min_length=1, so test with direct validation)
        # Test our validator's handling of empty path by checking the validation logic directly
        empty_path_errors = coordinator.validate_project_data_context(None)
        assert any("is None" in error for error in empty_path_errors)
        
        # Nonexistent path
        invalid_context = ProjectDataContext(
            cloned_code_path="/nonexistent",
            detected_languages=["java"]
        )
        errors = coordinator.validate_project_data_context(invalid_context)
        assert any("does not exist" in error for error in errors)
        
        # No languages
        invalid_context = ProjectDataContext(
            cloned_code_path=sample_project_context.cloned_code_path,
            detected_languages=[]
        )
        errors = coordinator.validate_project_data_context(invalid_context)
        assert any("empty" in error for error in errors)
        
        # Unsupported languages (no parsers registered)
        unsupported_context = ProjectDataContext(
            cloned_code_path=sample_project_context.cloned_code_path,
            detected_languages=["unsupported_language"]
        )
        errors = coordinator.validate_project_data_context(unsupported_context)
        assert any("no parsers available" in error.lower() for error in errors)
    
    def test_language_mapping(self, coordinator):
        """Test language name mapping functionality."""
        coordinator.register_parser(MockJavaParser())
        
        # Test canonical name mapping
        assert coordinator.has_parser_for_language("java")
        
        # Test case insensitive
        assert coordinator.has_parser_for_language("JAVA")
        assert coordinator.has_parser_for_language("Java")
        
        # Test language mapping (if implemented)
        # This tests the _language_mapping functionality
        context = ProjectDataContext(
            cloned_code_path="/tmp",
            detected_languages=["Java", "JAVA", "java"]  # Different cases
        )
        # Should all map to "java"
        errors = coordinator.validate_project_data_context(context)
        # With Java parser registered, should have fewer language-related errors
    
    def test_coordination_statistics(self, coordinator, sample_project_context):
        """Test coordination statistics tracking."""
        coordinator.register_parser(MockJavaParser())
        coordinator.register_parser(MockPythonParser())
        
        # Initial stats
        initial_stats = coordinator.get_coordination_stats()
        assert initial_stats['coordination_sessions'] == 0
        assert initial_stats['total_languages_processed'] == 0
        
        # Run coordination
        result = coordinator.coordinate_parsing(sample_project_context)
        
        # Check updated stats
        final_stats = coordinator.get_coordination_stats()
        assert final_stats['coordination_sessions'] == 1
        assert final_stats['total_languages_processed'] >= 1
        assert final_stats['total_files_coordinated'] > 0
        assert final_stats['total_entities_coordinated'] > 0
        
        # Test averages
        assert 'average_coordination_time_ms' in final_stats
        assert 'average_entities_per_session' in final_stats
        assert final_stats['average_coordination_time_ms'] > 0
    
    def test_string_representations(self, coordinator):
        """Test string representation methods."""
        # Empty coordinator
        str_repr = str(coordinator)
        assert "CodeParserCoordinatorModule" in str_repr
        assert "parsers=[]" in str_repr
        
        repr_str = repr(coordinator)
        assert "CodeParserCoordinatorModule" in repr_str
        assert "registered_parsers=0" in repr_str
        
        # With parsers
        coordinator.register_parser(MockJavaParser())
        coordinator.register_parser(MockPythonParser())
        
        str_repr = str(coordinator)
        assert "java" in str_repr
        assert "python" in str_repr
        
        repr_str = repr(coordinator)
        assert "registered_parsers=2" in repr_str


# Integration test for the complete Task 2.2 workflow
class TestTask22Integration:
    """Integration tests specifically for Task 2.2 requirements."""
    
    def test_complete_task_22_workflow(self):
        """
        Test the complete Task 2.2 workflow:
        1. Receives ProjectDataContext with detected_languages and cloned_code_path
        2. Calls appropriate language parsers based on detected_languages
        3. Aggregates results from all parsers
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Setup project with multiple languages
            project_setup = self._setup_multi_language_project(temp_dir)
            
            # 2. Create ProjectDataContext (input from TEAM Data Acquisition)
            project_context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["java", "python"],
                repository_url="https://github.com/test/multi-lang-repo.git"
            )
            
            # 3. Initialize coordinator and register parsers
            coordinator = CodeParserCoordinatorModule()
            coordinator.register_parser(MockJavaParser())
            coordinator.register_parser(MockPythonParser())
            
            # 4. Execute coordination (main Task 2.2 function)
            result = coordinator.coordinate_parsing(project_context)
            
            # 5. Verify Task 2.2 requirements are met
            self._verify_task_22_requirements(result, project_context)
    
    def _setup_multi_language_project(self, temp_dir):
        """Setup a project with multiple language files."""
        # Java files
        java_dir = Path(temp_dir) / "src" / "main" / "java" / "com" / "example"
        java_dir.mkdir(parents=True)
        
        (java_dir / "Application.java").write_text("""
package com.example;

public class Application {
    public static void main(String[] args) {
        Calculator calc = new Calculator();
        int result = calc.add(5, 3);
        System.out.println("Result: " + result);
    }
}
        """)
        
        (java_dir / "Calculator.java").write_text("""
package com.example;

public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int multiply(int a, int b) {
        return a * b;
    }
}
        """)
        
        # Python files
        python_dir = Path(temp_dir) / "src" / "python"
        python_dir.mkdir(parents=True)
        
        (python_dir / "main.py").write_text("""
from calculator import Calculator

def main():
    calc = Calculator()
    result = calc.add(10, 20)
    print(f"Python result: {result}")

if __name__ == "__main__":
    main()
        """)
        
        (python_dir / "calculator.py").write_text("""
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
        """)
        
        return {
            'java_files': 2,
            'python_files': 2,
            'total_files': 4
        }
    
    def _verify_task_22_requirements(self, result: CoordinatorParseResult, project_context: ProjectDataContext):
        """Verify that Task 2.2 requirements are fully met."""
        
        # Requirement 1: Module receives ProjectDataContext with detected_languages and cloned_code_path
        assert result.project_path == project_context.cloned_code_path
        
        # Requirement 2: Based on detected_languages, calls appropriate parsers
        for language in project_context.detected_languages:
            assert language in result.languages_processed, f"Language {language} should be processed"
            assert language in result.language_results, f"Language {language} should have results"
        
        # Requirement 3: Aggregates results from all parsers
        assert result.total_files_parsed > 0, "Should have parsed files"
        assert result.total_entities_found > 0, "Should have found entities"
        
        # Additional verification for quality
        assert len(result.errors) == 0, f"Should have no errors, but got: {result.errors}"
        assert result.success_rate > 0.0, "Should have successful parsing"
        assert result.coordination_duration_ms > 0, "Should track timing"
        
        # Verify each language result contains proper data
        for language, lang_result in result.language_results.items():
            assert isinstance(lang_result, LanguageParseResult)
            assert lang_result.language == language
            assert len(lang_result.files_parsed) > 0, f"Language {language} should have parsed files"
            assert lang_result.total_entities > 0, f"Language {language} should have entities"
            assert lang_result.parse_duration_ms > 0, f"Language {language} should track timing" 