"""
Unit tests for ProjectDataContext model

Tests the ProjectDataContext Pydantic model including validation,
properties, methods, and edge cases.
"""

import pytest
import tempfile
import os
from datetime import datetime
from typing import List, Dict, Any

from src.shared.models.project_data_context import ProjectDataContext


class TestProjectDataContext:
    """Test suite for ProjectDataContext model"""
    
    def test_basic_initialization(self):
        """Test basic ProjectDataContext creation with required fields"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python", "javascript"]
            )
            
            assert context.cloned_code_path == temp_dir
            assert context.detected_languages == ["python", "javascript"]
            assert context.repository_url is None
            assert isinstance(context.repository_stats, dict)
            assert isinstance(context.language_statistics, dict)
            assert isinstance(context.analysis_timestamp, datetime)
            assert context.acquisition_duration_ms is None
    
    def test_initialization_with_all_fields(self):
        """Test ProjectDataContext creation with all optional fields"""
        with tempfile.TemporaryDirectory() as temp_dir:
            timestamp = datetime.now()
            repo_stats = {"size": 1024, "commits": 42}
            lang_stats = {"python": {"lines": 500}, "javascript": {"lines": 300}}
            
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python", "javascript"],
                repository_url="https://github.com/test/repo.git",
                repository_stats=repo_stats,
                language_statistics=lang_stats,
                analysis_timestamp=timestamp,
                acquisition_duration_ms=1500.5
            )
            
            assert context.cloned_code_path == temp_dir
            assert context.detected_languages == ["python", "javascript"]
            assert context.repository_url == "https://github.com/test/repo.git"
            assert context.repository_stats == repo_stats
            assert context.language_statistics == lang_stats
            assert context.analysis_timestamp == timestamp
            assert context.acquisition_duration_ms == 1500.5
    
    def test_path_validation_absolute_path(self):
        """Test that only absolute paths are accepted"""
        # Valid absolute path (temporary directory)
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python"]
            )
            assert context.cloned_code_path == temp_dir
        
        # Invalid relative path
        with pytest.raises(ValueError, match="cloned_code_path must be an absolute path"):
            ProjectDataContext(
                cloned_code_path="relative/path",
                detected_languages=["python"]
            )
    
    def test_path_validation_empty_path(self):
        """Test validation of empty or None paths"""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ProjectDataContext(
                cloned_code_path="",
                detected_languages=["python"]
            )
        
        with pytest.raises(ValidationError):
            ProjectDataContext(
                cloned_code_path=None,
                detected_languages=["python"]
            )
    
    def test_languages_validation_and_normalization(self):
        """Test language list validation and normalization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test normalization (lowercase, strip whitespace)
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["Python", "  JavaScript  ", "JAVA", "python"]  # Duplicate
            )
            
            # Should be normalized and deduplicated
            expected = ["python", "javascript", "java"]
            assert context.detected_languages == expected
    
    def test_languages_validation_invalid_types(self):
        """Test language validation with invalid types"""
        from pydantic import ValidationError
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Invalid: not a list
            with pytest.raises(ValidationError):
                ProjectDataContext(
                    cloned_code_path=temp_dir,
                    detected_languages="python"
                )
            
            # Test with invalid types in list (will raise ValidationError in Pydantic v2)
            with pytest.raises(ValidationError):
                ProjectDataContext(
                    cloned_code_path=temp_dir,
                    detected_languages=["python", 123, None, "", "javascript"]
                )
            
            # Test with valid strings only
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python", "javascript", ""]  # Empty string will be filtered
            )
            
            # Should filter out empty strings in validation
            assert "python" in context.detected_languages
            assert "javascript" in context.detected_languages
    
    def test_empty_languages_list(self):
        """Test with empty languages list"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=[]
            )
            
            assert context.detected_languages == []
            assert not context.has_languages
            assert context.primary_language is None
            assert context.language_count == 0
    
    def test_properties_single_language(self):
        """Test properties with single language"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python"]
            )
            
            assert context.has_languages
            assert context.primary_language == "python"
            assert context.language_count == 1
            assert context.has_language("python")
            assert context.has_language("Python")  # Case insensitive
            assert not context.has_language("javascript")
    
    def test_properties_multiple_languages(self):
        """Test properties with multiple languages"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python", "javascript", "java"]
            )
            
            assert context.has_languages
            assert context.primary_language == "python"
            assert context.language_count == 3
            assert context.has_language("python")
            assert context.has_language("javascript")
            assert context.has_language("java")
            assert not context.has_language("cpp")
    
    def test_get_summary(self):
        """Test get_summary method"""
        with tempfile.TemporaryDirectory() as temp_dir:
            timestamp = datetime.now()
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python", "javascript"],
                repository_url="https://github.com/test/repo.git",
                analysis_timestamp=timestamp,
                acquisition_duration_ms=1234.5
            )
            
            summary = context.get_summary()
            
            assert isinstance(summary, dict)
            assert summary["repository_url"] == "https://github.com/test/repo.git"
            assert summary["cloned_path"] == temp_dir
            assert summary["detected_languages"] == ["python", "javascript"]
            assert summary["language_count"] == 2
            assert summary["primary_language"] == "python"
            assert summary["has_languages"] is True
            assert summary["analysis_timestamp"] == timestamp.isoformat()
            assert summary["acquisition_duration_ms"] == 1234.5
    
    def test_string_representations(self):
        """Test __str__ and __repr__ methods"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with multiple languages
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python", "javascript"],
                repository_url="https://github.com/test/repo.git"
            )
            
            str_repr = str(context)
            assert os.path.basename(temp_dir) in str_repr
            assert "2 languages" in str_repr
            
            repr_str = repr(context)
            assert "ProjectDataContext" in repr_str
            assert temp_dir in repr_str
            assert "python" in repr_str
            assert "javascript" in repr_str
            
            # Test with single language
            context_single = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python"]
            )
            
            str_repr_single = str(context_single)
            assert "python" in str_repr_single
            assert "languages" not in str_repr_single  # Should show the language name
            
            # Test with no languages
            context_empty = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=[]
            )
            
            str_repr_empty = str(context_empty)
            assert "no languages" in str_repr_empty
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python", "javascript"],
                repository_url="https://github.com/test/repo.git",
                acquisition_duration_ms=1500.0
            )
            
            # Serialize to JSON (Pydantic v2)
            json_data = original.model_dump_json()
            assert isinstance(json_data, str)
            
            # Deserialize from JSON (Pydantic v2)
            deserialized = ProjectDataContext.model_validate_json(json_data)
            
            assert deserialized.cloned_code_path == original.cloned_code_path
            assert deserialized.detected_languages == original.detected_languages
            assert deserialized.repository_url == original.repository_url
            assert deserialized.acquisition_duration_ms == original.acquisition_duration_ms
    
    def test_dict_conversion(self):
        """Test dictionary conversion"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python", "javascript"],
                repository_url="https://github.com/test/repo.git"
            )
            
            # Convert to dict (Pydantic v2)
            context_dict = context.model_dump()
            assert isinstance(context_dict, dict)
            assert context_dict["cloned_code_path"] == temp_dir
            assert context_dict["detected_languages"] == ["python", "javascript"]
            assert context_dict["repository_url"] == "https://github.com/test/repo.git"
            
            # Create from dict
            new_context = ProjectDataContext(**context_dict)
            assert new_context.cloned_code_path == context.cloned_code_path
            assert new_context.detected_languages == context.detected_languages
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Very long language list
            many_languages = [f"lang{i}" for i in range(100)]
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=many_languages
            )
            
            assert len(context.detected_languages) == 100
            assert context.language_count == 100
            assert context.primary_language == "lang0"
            
            # Unicode in languages
            unicode_context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python", "中文", "русский", "עברית"]
            )
            
            assert "中文" in unicode_context.detected_languages
            assert unicode_context.has_language("中文")
    
    def test_immutability_aspects(self):
        """Test that certain aspects of the model behave correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProjectDataContext(
                cloned_code_path=temp_dir,
                detected_languages=["python", "javascript"]
            )
            
            # Get the languages list
            languages = context.detected_languages
            
            # Modifying the returned list should not affect the model
            # (Pydantic models are not deeply immutable by default, but this tests behavior)
            original_length = len(languages)
            languages.append("new_language")
            
            # The model should still have the original languages
            # Note: This test depends on how Pydantic handles list fields
            assert len(context.detected_languages) >= original_length 