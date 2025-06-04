"""
Unit Tests for TaskDefinition Model

Tests for the TaskDefinition Pydantic model, including:
- Expected use case
- Edge case 
- Failure case
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from shared.models.task_definition import TaskDefinition


class TestTaskDefinition:
    """Test suite for TaskDefinition model."""
    
    def test_task_definition_creation_expected_use(self):
        """Test normal TaskDefinition creation with valid repository URL."""
        # Arrange
        repo_url = "https://github.com/example/test-repo.git"
        
        # Act
        task_def = TaskDefinition(repository_url=repo_url)
        
        # Assert
        assert task_def.repository_url == repo_url
        assert task_def.task_id is None
        assert task_def.created_at is None
        assert str(task_def) == f"TaskDefinition(repo={repo_url}, id=None)"
    
    def test_task_definition_with_all_fields(self):
        """Test TaskDefinition creation with all fields populated."""
        # Arrange
        repo_url = "https://github.com/example/test-repo.git"
        task_id = "test-task-123"
        created_at = datetime.now()
        
        # Act
        task_def = TaskDefinition(
            repository_url=repo_url,
            task_id=task_id,
            created_at=created_at
        )
        
        # Assert
        assert task_def.repository_url == repo_url
        assert task_def.task_id == task_id
        assert task_def.created_at == created_at
        assert str(task_def) == f"TaskDefinition(repo={repo_url}, id={task_id})"
    
    def test_task_definition_edge_case_empty_url(self):
        """Test TaskDefinition with empty URL - edge case."""
        # Arrange
        repo_url = ""
        
        # Act
        task_def = TaskDefinition(repository_url=repo_url)
        
        # Assert
        assert task_def.repository_url == ""
        assert task_def.task_id is None
        assert task_def.created_at is None
    
    def test_task_definition_failure_case_missing_required_field(self):
        """Test TaskDefinition creation failure when required field is missing."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            TaskDefinition()  # Missing required repository_url
        
        # Verify the error is about the missing field
        error = exc_info.value
        assert "repository_url" in str(error)
        assert "field required" in str(error).lower()
    
    def test_task_definition_json_serialization(self):
        """Test JSON serialization of TaskDefinition."""
        # Arrange
        repo_url = "https://github.com/example/test-repo.git"
        task_id = "test-task-123"
        created_at = datetime(2025, 6, 4, 12, 0, 0)
        
        task_def = TaskDefinition(
            repository_url=repo_url,
            task_id=task_id,
            created_at=created_at
        )
        
        # Act
        json_data = task_def.model_dump()
        
        # Assert
        assert json_data["repository_url"] == repo_url
        assert json_data["task_id"] == task_id
        assert json_data["created_at"] == created_at
    
    def test_task_definition_from_dict(self):
        """Test creating TaskDefinition from dictionary."""
        # Arrange
        data = {
            "repository_url": "https://github.com/example/test-repo.git",
            "task_id": "test-task-123"
        }
        
        # Act
        task_def = TaskDefinition(**data)
        
        # Assert
        assert task_def.repository_url == data["repository_url"]
        assert task_def.task_id == data["task_id"]
        assert task_def.created_at is None 