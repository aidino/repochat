"""
Unit tests for DataPreparationModule

Tests the DataPreparationModule functionality including:
- ProjectDataContext creation from individual parameters
- Context creation from module results
- Input validation and error handling
- Statistics tracking and module management
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Dict, List, Any
import time
import uuid

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from teams.data_acquisition.data_preparation_module import DataPreparationModule
from shared.models.project_data_context import ProjectDataContext


class TestDataPreparationModule:
    """Test suite for DataPreparationModule"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.module = DataPreparationModule()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures after each test method"""
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test DataPreparationModule initialization"""
        module = DataPreparationModule()
        
        assert hasattr(module, 'logger')
        assert hasattr(module, 'module_id')
        assert module.module_id.startswith('data_prep_')
        assert module.contexts_created == 0
        assert module.total_preparation_time == 0.0
    
    def test_create_project_context_basic(self):
        """Test basic ProjectDataContext creation"""
        languages = ["python", "javascript"]
        
        context = self.module.create_project_context(
            cloned_code_path=self.temp_dir,
            detected_languages=languages
        )
        
        assert isinstance(context, ProjectDataContext)
        assert context.cloned_code_path == self.temp_dir
        assert context.detected_languages == languages
        assert context.repository_url is None
        assert isinstance(context.repository_stats, dict)
        assert isinstance(context.language_statistics, dict)
        assert isinstance(context.analysis_timestamp, datetime)
        assert context.acquisition_duration_ms is not None
        assert context.acquisition_duration_ms > 0
        
        # Check module statistics
        assert self.module.contexts_created == 1
        assert self.module.total_preparation_time > 0
    
    def test_create_project_context_with_all_optional_fields(self):
        """Test ProjectDataContext creation with all optional fields"""
        languages = ["python", "java"]
        repo_url = "https://github.com/test/repo.git"
        repo_stats = {"size": 1024, "commits": 42, "branches": 3}
        lang_stats = {"python": {"lines": 500, "files": 10}}
        
        context = self.module.create_project_context(
            cloned_code_path=self.temp_dir,
            detected_languages=languages,
            repository_url=repo_url,
            repository_stats=repo_stats,
            language_statistics=lang_stats
        )
        
        assert context.cloned_code_path == self.temp_dir
        assert context.detected_languages == languages
        assert context.repository_url == repo_url
        assert context.repository_stats == repo_stats
        assert context.language_statistics == lang_stats
        assert isinstance(context.analysis_timestamp, datetime)
        assert context.acquisition_duration_ms is not None
    
    def test_create_project_context_validation_errors(self):
        """Test input validation for create_project_context"""
        languages = ["python"]
        
        # Test empty path
        with pytest.raises(ValueError, match="cloned_code_path must be a non-empty string"):
            self.module.create_project_context(
                cloned_code_path="",
                detected_languages=languages
            )
        
        # Test None path
        with pytest.raises(ValueError, match="cloned_code_path must be a non-empty string"):
            self.module.create_project_context(
                cloned_code_path=None,
                detected_languages=languages
            )
        
        # Test invalid languages type
        with pytest.raises(ValueError, match="detected_languages must be a list"):
            self.module.create_project_context(
                cloned_code_path=self.temp_dir,
                detected_languages="python"
            )
        
        # Test non-string path
        with pytest.raises(ValueError, match="cloned_code_path must be a non-empty string"):
            self.module.create_project_context(
                cloned_code_path=123,
                detected_languages=languages
            )
    
    def test_create_context_from_modules_string_results(self):
        """Test creating context from simple module results (strings/lists)"""
        git_result = self.temp_dir
        lang_result = ["python", "javascript"]
        
        context = self.module.create_context_from_modules(
            git_operations_result=git_result,
            language_identifier_result=lang_result
        )
        
        assert isinstance(context, ProjectDataContext)
        assert context.cloned_code_path == self.temp_dir
        assert context.detected_languages == ["python", "javascript"]
        assert context.repository_url is None
        assert isinstance(context.repository_stats, dict)
        assert isinstance(context.language_statistics, dict)
    
    def test_create_context_from_modules_dict_results(self):
        """Test creating context from complex module results (dictionaries)"""
        git_result = {
            "path": self.temp_dir,
            "repository_url": "https://github.com/test/repo.git",
            "stats": {"size": 2048, "commits": 25}
        }
        
        lang_result = {
            "languages": ["python", "javascript", "java"],
            "statistics": {
                "python": {"lines": 1000, "files": 15},
                "javascript": {"lines": 500, "files": 8}
            }
        }
        
        context = self.module.create_context_from_modules(
            git_operations_result=git_result,
            language_identifier_result=lang_result
        )
        
        assert context.cloned_code_path == self.temp_dir
        assert context.repository_url == "https://github.com/test/repo.git"
        assert context.detected_languages == ["python", "javascript", "java"]
        assert context.repository_stats == git_result["stats"]
        assert context.language_statistics == lang_result["statistics"]
    
    def test_create_context_from_modules_alternative_keys(self):
        """Test creating context with alternative key names in results"""
        git_result = {
            "cloned_path": self.temp_dir,  # Alternative key name
            "stats": {"size": 1024}
        }
        
        lang_result = {
            "languages": ["python"],
            "statistics": {"python": {"lines": 100}}
        }
        
        context = self.module.create_context_from_modules(
            git_operations_result=git_result,
            language_identifier_result=lang_result
        )
        
        assert context.cloned_code_path == self.temp_dir
        assert context.detected_languages == ["python"]
    
    def test_create_context_from_modules_validation_errors(self):
        """Test validation errors in create_context_from_modules"""
        # Test invalid git result type
        with pytest.raises(ValueError, match="git_operations_result must be a string \\(path\\) or dict"):
            self.module.create_context_from_modules(
                git_operations_result=123,
                language_identifier_result=["python"]
            )
        
        # Test invalid language result type
        with pytest.raises(ValueError, match="language_identifier_result must be a list \\(languages\\) or dict"):
            self.module.create_context_from_modules(
                git_operations_result=self.temp_dir,
                language_identifier_result="python"
            )
        
        # Test missing path in git result dict
        with pytest.raises(ValueError, match="Cannot extract cloned_path from git_operations_result"):
            self.module.create_context_from_modules(
                git_operations_result={"stats": {}},  # No path key
                language_identifier_result=["python"]
            )
    
    def test_validate_context_valid(self):
        """Test context validation with valid context"""
        context = ProjectDataContext(
            cloned_code_path=self.temp_dir,
            detected_languages=["python", "javascript"]
        )
        
        assert self.module.validate_context(context) is True
    
    def test_validate_context_invalid_type(self):
        """Test context validation with invalid type"""
        fake_context = {"cloned_code_path": self.temp_dir}
        
        assert self.module.validate_context(fake_context) is False
    
    def test_validate_context_missing_path(self):
        """Test context validation with missing cloned_code_path"""
        # Create invalid context by mocking
        context = Mock(spec=ProjectDataContext)
        context.cloned_code_path = ""
        context.detected_languages = ["python"]
        
        assert self.module.validate_context(context) is False
    
    def test_validate_context_invalid_languages(self):
        """Test context validation with invalid languages"""
        # Create invalid context by mocking
        context = Mock(spec=ProjectDataContext)
        context.cloned_code_path = self.temp_dir
        context.detected_languages = "python"  # Should be list
        
        assert self.module.validate_context(context) is False
    
    def test_validate_context_exception_handling(self):
        """Test context validation with exception during validation"""
        # Create context that raises exception when accessed
        context = Mock(spec=ProjectDataContext)
        context.cloned_code_path = property(lambda self: 1/0)  # Raises ZeroDivisionError
        
        assert self.module.validate_context(context) is False
    
    def test_get_module_stats(self):
        """Test module statistics retrieval"""
        # Initial stats
        initial_stats = self.module.get_module_stats()
        assert initial_stats["contexts_created"] == 0
        assert initial_stats["total_preparation_time_ms"] == 0.0
        assert initial_stats["average_preparation_time_ms"] == 0.0
        assert "module_id" in initial_stats
        assert "uptime_seconds" in initial_stats
        
        # Create some contexts to modify stats
        self.module.create_project_context(
            cloned_code_path=self.temp_dir,
            detected_languages=["python"]
        )
        
        self.module.create_project_context(
            cloned_code_path=self.temp_dir,
            detected_languages=["javascript"]
        )
        
        # Check updated stats
        updated_stats = self.module.get_module_stats()
        assert updated_stats["contexts_created"] == 2
        assert updated_stats["total_preparation_time_ms"] > 0
        assert updated_stats["average_preparation_time_ms"] > 0
        assert updated_stats["average_preparation_time_ms"] == (
            updated_stats["total_preparation_time_ms"] / 2
        )
    
    def test_multiple_contexts_statistics(self):
        """Test statistics tracking across multiple context creations"""
        assert self.module.contexts_created == 0
        assert self.module.total_preparation_time == 0.0
        
        # Create multiple contexts
        for i in range(3):
            self.module.create_project_context(
                cloned_code_path=self.temp_dir,
                detected_languages=[f"lang{i}"]
            )
        
        assert self.module.contexts_created == 3
        assert self.module.total_preparation_time > 0
        
        stats = self.module.get_module_stats()
        assert stats["contexts_created"] == 3
        assert stats["average_preparation_time_ms"] > 0
    
    def test_edge_cases_empty_data(self):
        """Test edge cases with empty or minimal data"""
        # Empty languages list
        context = self.module.create_project_context(
            cloned_code_path=self.temp_dir,
            detected_languages=[]
        )
        
        assert context.detected_languages == []
        assert not context.has_languages
        
        # Empty optional dictionaries
        context2 = self.module.create_project_context(
            cloned_code_path=self.temp_dir,
            detected_languages=["python"],
            repository_stats={},
            language_statistics={}
        )
        
        assert context2.repository_stats == {}
        assert context2.language_statistics == {}
    
    def test_context_creation_timing(self):
        """Test that timing is properly recorded"""
        context = self.module.create_project_context(
            cloned_code_path=self.temp_dir,
            detected_languages=["python"]
        )
        
        # Should have recorded timing
        assert context.acquisition_duration_ms is not None
        assert context.acquisition_duration_ms > 0
        assert isinstance(context.acquisition_duration_ms, float)
        
        # Module should track total time
        assert self.module.total_preparation_time > 0
        assert self.module.total_preparation_time >= context.acquisition_duration_ms
    
    def test_timing_calculation(self):
        """Test timing calculation with real time"""
        # Simple test without mocking - just verify timing is recorded
        context = self.module.create_project_context(
            cloned_code_path=self.temp_dir,
            detected_languages=["python"]
        )
        
        # Should have recorded timing
        assert context.acquisition_duration_ms is not None
        assert context.acquisition_duration_ms > 0
        assert isinstance(context.acquisition_duration_ms, float)
    
    def test_logging_integration(self):
        """Test that logging is properly integrated"""
        # This test verifies that the module has a logger and uses it
        # We can't easily test actual log output without complex mocking
        
        assert hasattr(self.module, 'logger')
        assert self.module.logger is not None
        
        # Test that operations complete without logging errors
        context = self.module.create_project_context(
            cloned_code_path=self.temp_dir,
            detected_languages=["python"]
        )
        
        stats = self.module.get_module_stats()
        validation_result = self.module.validate_context(context)
        
        # If we get here without exceptions, logging is working
        assert context is not None
        assert stats is not None
        assert validation_result is True
    
    def test_module_id_uniqueness(self):
        """Test that module IDs are unique across instances"""
        # Create multiple modules rapidly
        modules = [DataPreparationModule() for _ in range(5)]
        module_ids = [m.module_id for m in modules]
        
        # All IDs should be unique
        assert len(set(module_ids)) == len(module_ids)
        assert all(mid.startswith('data_prep_') for mid in module_ids) 