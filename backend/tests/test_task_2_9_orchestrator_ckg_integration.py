"""
Unit Tests for Task 2.9: Orchestrator CKG Integration

Tests the integration between Orchestrator Agent and TEAM CKG Operations,
verifying the complete workflow from data acquisition to CKG building.
"""

import unittest
import tempfile
import shutil
import os
from unittest.mock import Mock, patch

from shared.models.task_definition import TaskDefinition
from shared.models.project_data_context import ProjectDataContext
from teams.ckg_operations.team_ckg_operations_facade import TeamCKGOperationsFacade, CKGOperationResult
from orchestrator.orchestrator_agent import OrchestratorAgent


class TestOrchestratorCKGIntegration(unittest.TestCase):
    """Test OrchestratorAgent integration with TEAM CKG Operations."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_task_definition = TaskDefinition(
            repository_url="https://github.com/test/repo.git"
        )
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('orchestrator.orchestrator_agent.TeamCKGOperationsFacade')
    def test_orchestrator_initialization_with_ckg(self, mock_facade_class):
        """Test that OrchestratorAgent initializes with CKG Operations."""
        mock_facade = Mock()
        mock_facade.is_ready.return_value = True
        mock_facade_class.return_value = mock_facade
        
        orchestrator = OrchestratorAgent()
        
        # Verify CKG operations are initialized
        self.assertIsNotNone(orchestrator.ckg_operations)
        mock_facade_class.assert_called_once()
        
        orchestrator.shutdown()
    
    @patch('orchestrator.orchestrator_agent.TeamCKGOperationsFacade')
    def test_handle_scan_project_with_ckg_task_success(self, mock_facade_class):
        """Test successful scan project with CKG workflow."""
        # Setup CKG facade mock
        mock_facade = Mock()
        mock_facade.is_ready.return_value = True
        
        mock_ckg_result = CKGOperationResult(
            success=True,
            project_name="test_repo",
            files_parsed=5,
            entities_found=25,
            relationships_found=15,
            nodes_created=30,
            relationships_created=15,
            files_processed=5
        )
        mock_facade.process_project_data_context.return_value = mock_ckg_result
        mock_facade_class.return_value = mock_facade
        
        # Mock data acquisition workflow
        with patch.object(OrchestratorAgent, 'handle_scan_project_task') as mock_scan:
            mock_project_context = ProjectDataContext(
                cloned_code_path=self.temp_dir,
                detected_languages=["java"],
                repository_url="https://github.com/test/repo.git"
            )
            mock_scan.return_value = mock_project_context
            
            orchestrator = OrchestratorAgent()
            
            # Execute full workflow
            project_context, ckg_result = orchestrator.handle_scan_project_with_ckg_task(
                self.test_task_definition
            )
            
            # Verify data acquisition was called
            mock_scan.assert_called_once_with(self.test_task_definition)
            
            # Verify CKG operations was called  
            mock_facade.process_project_data_context.assert_called_once()
            
            # Verify results
            self.assertEqual(project_context, mock_project_context)
            self.assertEqual(ckg_result, mock_ckg_result)
            self.assertTrue(ckg_result.success)
            self.assertEqual(ckg_result.nodes_created, 30)
            
            orchestrator.shutdown()


class TestCKGOperationResult(unittest.TestCase):
    """Test CKGOperationResult data class."""
    
    def test_ckg_operation_result_initialization(self):
        """Test CKGOperationResult initialization and defaults."""
        result = CKGOperationResult(success=True, project_name="test")
        
        self.assertTrue(result.success)
        self.assertEqual(result.project_name, "test")
        self.assertEqual(result.operation_duration_ms, 0.0)
        self.assertEqual(result.files_parsed, 0)
        self.assertEqual(result.entities_found, 0)
        self.assertEqual(result.relationships_found, 0)
        self.assertEqual(result.nodes_created, 0)
        self.assertEqual(result.relationships_created, 0)
        self.assertEqual(result.files_processed, 0)
        self.assertEqual(result.ckg_build_duration_ms, 0.0)
        self.assertEqual(result.languages_processed, [])
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])


if __name__ == '__main__':
    unittest.main() 