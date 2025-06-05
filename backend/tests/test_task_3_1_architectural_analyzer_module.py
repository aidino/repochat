#!/usr/bin/env python3
"""
Unit Tests for Task 3.1 (F3.1): ArchitecturalAnalyzerModule

Tests the circular dependency detection functionality and architectural analysis features.

Test Coverage:
- Circular dependency detection (file level)
- Circular dependency detection (class level) 
- AnalysisFinding generation
- Error handling and edge cases
- Integration with CKG Query Interface

Author: RepoChat Development Team
Date: 2025-06-05
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to Python path for testing
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

from teams.code_analysis.architectural_analyzer_module import ArchitecturalAnalyzerModule
from teams.code_analysis.models import (
    AnalysisFinding, 
    AnalysisFindingType, 
    AnalysisSeverity,
    CircularDependency,
    AnalysisResult
)
from teams.ckg_operations.ast_to_ckg_builder_module import CKGQueryInterfaceModule


class TestArchitecturalAnalyzerModule(unittest.TestCase):
    """Test cases for ArchitecturalAnalyzerModule circular dependency detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock dependencies
        self.mock_neo4j_conn = Mock()
        self.mock_neo4j_conn.is_connected.return_value = True
        self.mock_neo4j_conn.connect.return_value = True
        
        self.mock_ckg_query = Mock(spec=CKGQueryInterfaceModule)
        self.mock_ckg_query.neo4j = self.mock_neo4j_conn
        
        # Create analyzer instance
        self.analyzer = ArchitecturalAnalyzerModule(ckg_query_interface=self.mock_ckg_query)
        
        # Test data
        self.test_project = "test-spring-petclinic"

    def test_init_analyzer_with_ckg_interface(self):
        """Test analyzer initialization with provided CKG interface."""
        analyzer = ArchitecturalAnalyzerModule(ckg_query_interface=self.mock_ckg_query)
        
        self.assertEqual(analyzer.ckg_query, self.mock_ckg_query)
        self.assertIsNotNone(analyzer.logger)
        self.assertEqual(analyzer._stats['analyses_performed'], 0)

    def test_init_analyzer_without_ckg_interface(self):
        """Test analyzer initialization without CKG interface (creates new one)."""
        with patch('teams.code_analysis.architectural_analyzer_module.CKGQueryInterfaceModule') as mock_ckg:
            analyzer = ArchitecturalAnalyzerModule()
            
            mock_ckg.assert_called_once()
            self.assertIsNotNone(analyzer.ckg_query)

    def test_detect_file_circular_dependencies_success(self):
        """Test successful detection of file circular dependencies."""
        # Mock Neo4j session and results
        mock_session = Mock()
        mock_result = Mock()
        
        # Sample circular dependency data
        mock_records = [
            {
                'cycle_path': ['FileA.java', 'FileB.java', 'FileC.java', 'FileA.java'],
                'cycle_length': 4
            },
            {
                'cycle_path': ['UtilX.java', 'UtilY.java', 'UtilX.java'],
                'cycle_length': 3
            }
        ]
        
        mock_result.__iter__ = Mock(return_value=iter(mock_records))
        mock_session.run.return_value = mock_result
        
        with patch.object(self.mock_neo4j_conn, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_get_session.return_value.__exit__ = Mock(return_value=None)
            
            cycles = self.analyzer._detect_file_circular_dependencies(self.test_project)
            
            # Verify results
            self.assertEqual(len(cycles), 2)
            
            # Check first cycle
            self.assertEqual(cycles[0].cycle_path, ['FileA.java', 'FileB.java', 'FileC.java'])
            self.assertEqual(cycles[0].cycle_type, 'file')
            self.assertIn(cycles[0].severity, [AnalysisSeverity.HIGH, AnalysisSeverity.MEDIUM])
            
            # Check second cycle  
            self.assertEqual(cycles[1].cycle_path, ['UtilX.java', 'UtilY.java'])
            self.assertEqual(cycles[1].cycle_type, 'file')

    def test_detect_class_circular_dependencies_inheritance(self):
        """Test detection of class inheritance circular dependencies."""
        mock_session = Mock()
        
        # Mock inheritance cycle results
        inheritance_records = [
            {
                'cycle_path': ['ClassA', 'ClassB', 'ClassA'],
                'cycle_length': 3,
                'relationship_types': ['EXTENDS', 'EXTENDS']
            }
        ]
        
        # Mock call cycle results (empty for this test)
        call_records = []
        
        # Set up multiple call results for different queries
        mock_session.run.side_effect = [
            iter(inheritance_records),  # First call for inheritance cycles
            iter(call_records)          # Second call for method call cycles
        ]
        
        with patch.object(self.mock_neo4j_conn, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_get_session.return_value.__exit__ = Mock(return_value=None)
            
            cycles = self.analyzer._detect_class_circular_dependencies(self.test_project)
            
            # Verify results
            self.assertEqual(len(cycles), 1)
            self.assertEqual(cycles[0].cycle_path, ['ClassA', 'ClassB'])
            self.assertEqual(cycles[0].cycle_type, 'class')
            self.assertEqual(cycles[0].confidence, 0.9)  # High confidence for inheritance
            self.assertIn(cycles[0].severity, [AnalysisSeverity.CRITICAL, AnalysisSeverity.HIGH])

    def test_detect_class_circular_dependencies_method_calls(self):
        """Test detection of class circular dependencies via method calls."""
        mock_session = Mock()
        
        # Mock method call cycle results
        inheritance_records = []  # No inheritance cycles
        call_records = [
            {
                'cycle_path': ['ClassX', 'methodA', 'ClassY', 'methodB', 'ClassX'],
                'cycle_length': 5
            }
        ]
        
        mock_session.run.side_effect = [
            iter(inheritance_records),
            iter(call_records)
        ]
        
        with patch.object(self.mock_neo4j_conn, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_get_session.return_value.__exit__ = Mock(return_value=None)
            
            cycles = self.analyzer._detect_class_circular_dependencies(self.test_project)
            
            # Verify results
            self.assertEqual(len(cycles), 1)
            self.assertEqual(cycles[0].cycle_path, ['ClassX', 'ClassY'])  # Extracted class names
            self.assertEqual(cycles[0].cycle_type, 'class')
            self.assertEqual(cycles[0].confidence, 0.6)  # Lower confidence for method calls
            self.assertEqual(cycles[0].severity, AnalysisSeverity.LOW)

    def test_determine_cycle_severity(self):
        """Test cycle severity determination logic."""
        # Test class cycle severity
        self.assertEqual(
            self.analyzer._determine_cycle_severity(2, "class"),
            AnalysisSeverity.CRITICAL
        )
        self.assertEqual(
            self.analyzer._determine_cycle_severity(3, "class"),
            AnalysisSeverity.HIGH
        )
        self.assertEqual(
            self.analyzer._determine_cycle_severity(6, "class"),
            AnalysisSeverity.MEDIUM
        )
        
        # Test file cycle severity
        self.assertEqual(
            self.analyzer._determine_cycle_severity(3, "file"),
            AnalysisSeverity.HIGH
        )
        self.assertEqual(
            self.analyzer._determine_cycle_severity(5, "file"),
            AnalysisSeverity.MEDIUM
        )
        self.assertEqual(
            self.analyzer._determine_cycle_severity(8, "file"),
            AnalysisSeverity.LOW
        )

    def test_convert_cycles_to_findings(self):
        """Test conversion of CircularDependency objects to AnalysisFinding objects."""
        # Create sample cycles
        cycles = [
            CircularDependency(
                cycle_path=['ClassA', 'ClassB', 'ClassC'],
                cycle_type='class',
                severity=AnalysisSeverity.HIGH,
                confidence=0.9
            ),
            CircularDependency(
                cycle_path=['FileX.java', 'FileY.java'],
                cycle_type='file',
                severity=AnalysisSeverity.MEDIUM,
                confidence=0.8
            )
        ]
        
        findings = self.analyzer._convert_cycles_to_findings(cycles, "class")
        
        # Verify findings
        self.assertEqual(len(findings), 2)
        
        # Check first finding
        finding1 = findings[0]
        self.assertEqual(finding1.finding_type, AnalysisFindingType.CIRCULAR_DEPENDENCY)
        self.assertEqual(finding1.severity, AnalysisSeverity.HIGH)
        self.assertEqual(finding1.confidence_score, 0.9)
        self.assertEqual(finding1.affected_entities, ['ClassA', 'ClassB', 'ClassC'])
        self.assertIn('dependency injection', finding1.recommendations[0])
        
        # Check metadata
        self.assertEqual(finding1.metadata['cycle_type'], 'class')
        self.assertEqual(finding1.metadata['cycle_length'], 3)

    def test_generate_cycle_recommendations(self):
        """Test recommendation generation for different cycle types."""
        # Test class cycle recommendations
        class_cycle = CircularDependency(
            cycle_path=['A', 'B'],
            cycle_type='class',
            severity=AnalysisSeverity.HIGH
        )
        
        recommendations = self.analyzer._generate_cycle_recommendations(class_cycle)
        
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any('dependency injection' in rec for rec in recommendations))
        self.assertTrue(any('interface' in rec for rec in recommendations))
        
        # Test file cycle recommendations
        file_cycle = CircularDependency(
            cycle_path=['X.java', 'Y.java'],
            cycle_type='file',
            severity=AnalysisSeverity.MEDIUM
        )
        
        recommendations = self.analyzer._generate_cycle_recommendations(file_cycle)
        
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any('utility module' in rec for rec in recommendations))
        self.assertTrue(any('dependency hierarchy' in rec for rec in recommendations))

    def test_detect_circular_dependencies_full_workflow(self):
        """Test the complete circular dependency detection workflow."""
        # Mock both file and class cycle detection methods
        mock_file_cycles = [
            CircularDependency(['File1.java', 'File2.java'], 'file', AnalysisSeverity.HIGH)
        ]
        mock_class_cycles = [
            CircularDependency(['ClassA', 'ClassB'], 'class', AnalysisSeverity.CRITICAL)
        ]
        
        with patch.object(self.analyzer, '_detect_file_circular_dependencies', return_value=mock_file_cycles), \
             patch.object(self.analyzer, '_detect_class_circular_dependencies', return_value=mock_class_cycles):
            
            result = self.analyzer.detect_circular_dependencies(self.test_project)
            
            # Verify overall result
            self.assertTrue(result.success)
            self.assertEqual(result.analysis_type, "circular_dependency_detection")
            self.assertEqual(result.project_name, self.test_project)
            
            # Verify findings
            self.assertEqual(len(result.findings), 2)  # 1 file + 1 class cycle
            self.assertGreater(result.analysis_duration_ms, 0)
            
            # Verify statistics updated
            self.assertEqual(self.analyzer._stats['analyses_performed'], 1)
            self.assertEqual(self.analyzer._stats['circular_dependencies_found'], 2)

    def test_neo4j_connection_failure(self):
        """Test handling of Neo4j connection failures."""
        # Mock connection failure
        self.mock_neo4j_conn.is_connected.return_value = False
        self.mock_neo4j_conn.connect.return_value = False
        
        cycles = self.analyzer._detect_file_circular_dependencies(self.test_project)
        
        # Should return empty list when connection fails
        self.assertEqual(len(cycles), 0)

    def test_cypher_query_exception(self):
        """Test handling of Cypher query exceptions."""
        mock_session = Mock()
        mock_session.run.side_effect = Exception("Cypher query failed")
        
        with patch.object(self.mock_neo4j_conn, 'get_session') as mock_get_session:
            mock_get_session.return_value.__enter__ = Mock(return_value=mock_session)
            mock_get_session.return_value.__exit__ = Mock(return_value=None)
            
            cycles = self.analyzer._detect_file_circular_dependencies(self.test_project)
            
            # Should handle exception gracefully
            self.assertEqual(len(cycles), 0)

    def test_analyze_project_architecture(self):
        """Test comprehensive architectural analysis."""
        # Mock the circular dependency detection
        mock_circular_result = AnalysisResult(
            analysis_type="circular_dependency_detection",
            project_name=self.test_project,
            findings=[
                AnalysisFinding(
                    finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
                    title="Test Cycle",
                    description="Test cycle description",
                    severity=AnalysisSeverity.HIGH,
                    analysis_module="ArchitecturalAnalyzerModule"
                )
            ],
            success=True
        )
        
        with patch.object(self.analyzer, 'detect_circular_dependencies', return_value=mock_circular_result):
            result = self.analyzer.analyze_project_architecture(self.test_project)
            
            # Verify comprehensive analysis
            self.assertTrue(result.success)
            self.assertEqual(result.analysis_type, "comprehensive_architectural_analysis")
            self.assertEqual(len(result.findings), 1)
            self.assertGreater(result.analysis_duration_ms, 0)

    def test_get_analysis_statistics(self):
        """Test analysis statistics retrieval."""
        # Perform some analyses to generate stats
        self.analyzer._stats['analyses_performed'] = 3
        self.analyzer._stats['circular_dependencies_found'] = 5
        self.analyzer._stats['total_analysis_time_ms'] = 1500.0
        
        stats = self.analyzer.get_analysis_statistics()
        
        self.assertEqual(stats['analyses_performed'], 3)
        self.assertEqual(stats['circular_dependencies_found'], 5)
        self.assertEqual(stats['total_analysis_time_ms'], 1500.0)
        self.assertEqual(stats['component'], 'ArchitecturalAnalyzerModule')


class TestAnalysisModels(unittest.TestCase):
    """Test cases for analysis data models."""
    
    def test_circular_dependency_cycle_description(self):
        """Test circular dependency description generation."""
        cycle = CircularDependency(
            cycle_path=['A', 'B', 'C'],
            cycle_type='class',
            severity=AnalysisSeverity.HIGH
        )
        
        description = cycle.get_cycle_description()
        
        self.assertIn('A → B → C → A', description)
        self.assertIn('Class circular dependency', description)

    def test_analysis_result_finding_filters(self):
        """Test AnalysisResult finding filter methods."""
        findings = [
            AnalysisFinding(
                finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
                title="Cycle 1",
                description="Test",
                severity=AnalysisSeverity.HIGH
            ),
            AnalysisFinding(
                finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
                title="Cycle 2",
                description="Test",
                severity=AnalysisSeverity.LOW
            ),
            AnalysisFinding(
                finding_type=AnalysisFindingType.CODE_SMELL,
                title="Smell 1",
                description="Test",
                severity=AnalysisSeverity.MEDIUM
            )
        ]
        
        result = AnalysisResult(
            analysis_type="test",
            project_name="test",
            findings=findings
        )
        
        # Test severity filtering
        high_findings = result.get_findings_by_severity(AnalysisSeverity.HIGH)
        self.assertEqual(len(high_findings), 1)
        self.assertEqual(high_findings[0].title, "Cycle 1")
        
        # Test type filtering
        cycle_findings = result.get_findings_by_type(AnalysisFindingType.CIRCULAR_DEPENDENCY)
        self.assertEqual(len(cycle_findings), 2)


if __name__ == '__main__':
    unittest.main() 