"""
Comprehensive Unit Tests for Task 4.5: ReportGeneratorModule

Tests for TEAM Synthesis & Reporting ReportGeneratorModule
covering all DoD requirements and functionality.
"""

import pytest
import time
from datetime import datetime
from unittest.mock import Mock, patch
from typing import List

from teams.synthesis_reporting.report_generator_module import (
    ReportGeneratorModule,
    ReportGenerationConfig
)
from teams.code_analysis.models import (
    AnalysisFinding,
    AnalysisFindingType,
    AnalysisSeverity
)


class TestReportGeneratorModule:
    """Test class for ReportGeneratorModule Task 4.5 DoD requirements."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = ReportGenerationConfig(
            language="vietnamese",
            include_summary=True,
            include_recommendations=True,
            group_by_severity=True
        )
        self.module = ReportGeneratorModule(self.config)
        
        # Test data: sample findings
        self.sample_findings = [
            AnalysisFinding(
                finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
                title="Circular dependency between ClassA and ClassB",
                description="ClassA -> ClassB -> ClassA",
                severity=AnalysisSeverity.HIGH,
                file_path="src/main/java/ClassA.java",
                start_line=15,
                end_line=20,
                affected_entities=["ClassA", "ClassB"],
                analysis_module="architectural_analyzer",
                confidence_score=0.9,
                recommendations=["Tái cấu trúc để phá vỡ chu trình", "Sử dụng dependency injection"]
            ),
            AnalysisFinding(
                finding_type=AnalysisFindingType.UNUSED_PUBLIC_ELEMENT,
                title="Unused public method methodX",
                description="Method classC.methodX appears to be unused",
                severity=AnalysisSeverity.MEDIUM,
                file_path="src/main/java/ClassC.java",
                start_line=42,
                affected_entities=["classC.methodX"],
                analysis_module="architectural_analyzer",
                confidence_score=0.8,
                recommendations=["Xem xét loại bỏ method nếu không cần thiết"]
            ),
            AnalysisFinding(
                finding_type=AnalysisFindingType.CODE_SMELL,
                title="Large method detected",
                description="Method has too many lines",
                severity=AnalysisSeverity.LOW,
                file_path="src/main/java/LargeClass.java",
                start_line=100,
                end_line=200,
                analysis_module="code_analyzer",
                confidence_score=1.0,
                recommendations=["Chia nhỏ method thành các method con"]
            )
        ]
    
    def test_module_initialization(self):
        """Test ReportGeneratorModule initialization."""
        module = ReportGeneratorModule()
        assert module is not None
        assert module.config.language == "vietnamese"
        assert module.config.include_summary is True
        assert module._stats['total_reports_generated'] == 0
        
        # Test with custom config
        custom_config = ReportGenerationConfig(language="english", group_by_type=True)
        custom_module = ReportGeneratorModule(custom_config)
        assert custom_module.config.language == "english"
        assert custom_module.config.group_by_type is True
    
    # Task 4.5 DoD Requirement 1: Module có hàm nhận danh sách AnalysisFinding đã tổng hợp
    def test_generate_text_report_accepts_findings_list(self):
        """Test that module accepts list of AnalysisFinding objects."""
        # Test với empty list
        result = self.module.generate_text_report([])
        assert isinstance(result, str)
        assert "Không có vấn đề nào được phát hiện" in result
        
        # Test với non-empty list
        result = self.module.generate_text_report(self.sample_findings)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "BÁO CÁO PHÂN TÍCH CODE" in result
    
    # Task 4.5 DoD Requirement 2: Hàm tạo chuỗi string dạng text, liệt kê phát hiện rõ ràng
    def test_generate_text_report_clear_listing(self):
        """Test that report clearly lists findings."""
        result = self.module.generate_text_report(self.sample_findings)
        
        # Check for clear finding listings (DoD requirement examples)
        assert "Phụ thuộc vòng tròn: Circular dependency between ClassA and ClassB" in result
        assert "Phần tử công khai không sử dụng: Unused public method methodX" in result
        
        # Check for descriptions
        assert "ClassA -> ClassB -> ClassA" in result
        assert "Method classC.methodX appears to be unused" in result
        
        # Check for file paths
        assert "src/main/java/ClassA.java" in result
        assert "src/main/java/ClassC.java" in result
        
        # Check for line numbers
        assert "dòng 15" in result or "line 15" in result
        assert "dòng 42" in result or "line 42" in result
    
    # Task 4.5 DoD Requirement 3: Trả về chuỗi báo cáo text
    def test_generate_text_report_returns_string(self):
        """Test that function returns text string report."""
        result = self.module.generate_text_report(self.sample_findings)
        
        # Must return string
        assert isinstance(result, str)
        
        # Must be non-empty for valid findings
        assert len(result) > 0
        
        # Must contain structured report sections
        assert "═══════════════════════════════════════════════════════════════" in result
        assert "📋 BÁO CÁO PHÂN TÍCH CODE" in result
        assert "🔍 CHI TIẾT CÁC PHÁT HIỆN" in result
    
    def test_empty_findings_report(self):
        """Test report generation with empty findings list."""
        result = self.module.generate_text_report([])
        
        assert "🎉 Không có vấn đề nào được phát hiện!" in result
        assert "Dự án này có vẻ tuân thủ tốt" in result
        assert isinstance(result, str)
    
    def test_vietnamese_language_support(self):
        """Test Vietnamese language in report."""
        vietnamese_config = ReportGenerationConfig(language="vietnamese")
        module = ReportGeneratorModule(vietnamese_config)
        
        result = module.generate_text_report(self.sample_findings)
        
        assert "BÁO CÁO PHÂN TÍCH CODE" in result
        assert "TÓM TẮT PHÂN TÍCH" in result
        assert "CHI TIẾT CÁC PHÁT HIỆN" in result
        assert "KHUYẾN NGHỊ" in result
        assert "Phụ thuộc vòng tròn" in result
        assert "Phần tử công khai không sử dụng" in result
    
    def test_english_language_support(self):
        """Test English language in report."""
        english_config = ReportGenerationConfig(language="english")
        module = ReportGeneratorModule(english_config)
        
        result = module.generate_text_report(self.sample_findings)
        
        assert "CODE ANALYSIS REPORT" in result
        assert "ANALYSIS SUMMARY" in result
        assert "DETAILED FINDINGS" in result
        assert "RECOMMENDATIONS" in result
        assert "Circular Dependency" in result
        assert "Unused Public Element" in result
    
    def test_severity_grouping(self):
        """Test grouping findings by severity."""
        config = ReportGenerationConfig(group_by_severity=True, language="vietnamese")
        module = ReportGeneratorModule(config)
        
        result = module.generate_text_report(self.sample_findings)
        
        # Check severity sections appear in order
        assert "CAO" in result  # HIGH severity
        assert "TRUNG BÌNH" in result  # MEDIUM severity  
        assert "THẤP" in result  # LOW severity
        
        # HIGH severity should appear before MEDIUM
        high_pos = result.find("CAO")
        medium_pos = result.find("TRUNG BÌNH")
        assert high_pos < medium_pos
    
    def test_type_grouping(self):
        """Test grouping findings by type."""
        config = ReportGenerationConfig(group_by_type=True, group_by_severity=False)
        module = ReportGeneratorModule(config)
        
        result = module.generate_text_report(self.sample_findings)
        
        # Check finding type sections
        assert "PHỤ THUỘC VÒNG TRÒN" in result or "CIRCULAR_DEPENDENCY" in result
        assert "PHẦN TỬ CÔNG KHAI KHÔNG SỬ DỤNG" in result or "UNUSED_PUBLIC_ELEMENT" in result
    
    def test_summary_section(self):
        """Test summary statistics section."""
        config = ReportGenerationConfig(include_summary=True)
        module = ReportGeneratorModule(config)
        
        result = module.generate_text_report(self.sample_findings)
        
        assert "TÓM TẮT PHÂN TÍCH" in result
        assert "Phân bố theo mức độ nghiêm trọng" in result
        assert "Phân bố theo loại vấn đề" in result
        
        # Check severity counts
        assert "Cao: 1" in result
        assert "Trung bình: 1" in result
        assert "Thấp: 1" in result
        
        # Check type counts
        assert "Phụ thuộc vòng tròn: 1" in result
    
    def test_recommendations_section(self):
        """Test recommendations section."""
        config = ReportGenerationConfig(include_recommendations=True)
        module = ReportGeneratorModule(config)
        
        result = module.generate_text_report(self.sample_findings)
        
        assert "KHUYẾN NGHỊ" in result
        assert "Tái cấu trúc để phá vỡ chu trình" in result
        assert "Sử dụng dependency injection" in result
        assert "Xem xét loại bỏ method nếu không cần thiết" in result
    
    def test_metadata_section(self):
        """Test metadata section when enabled."""
        config = ReportGenerationConfig(include_metadata=True)
        module = ReportGeneratorModule(config)
        
        result = module.generate_text_report(self.sample_findings)
        
        assert "THÔNG TIN BỔ SUNG" in result
        assert "Modules phân tích" in result
        assert "architectural_analyzer" in result
        assert "code_analyzer" in result
    
    def test_finding_formatting_examples(self):
        """Test specific finding formatting examples from DoD."""
        # Create specific test cases matching DoD examples
        circular_dep = AnalysisFinding(
            finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
            title="fileA -> fileB -> fileA",
            description="Circular dependency detected",
            severity=AnalysisSeverity.HIGH
        )
        
        unused_method = AnalysisFinding(
            finding_type=AnalysisFindingType.UNUSED_PUBLIC_ELEMENT, 
            title="classC.methodX",
            description="Unused public method",
            severity=AnalysisSeverity.MEDIUM
        )
        
        result = self.module.generate_text_report([circular_dep, unused_method])
        
        # Check DoD example formats
        assert "Phụ thuộc vòng tròn: fileA -> fileB -> fileA" in result
        assert "Phần tử công khai không sử dụng: classC.methodX" in result
    
    def test_configuration_options(self):
        """Test various configuration options."""
        # Test minimal config
        minimal_config = ReportGenerationConfig(
            include_summary=False,
            include_recommendations=False,
            include_metadata=False
        )
        module = ReportGeneratorModule(minimal_config)
        result = module.generate_text_report(self.sample_findings)
        
        assert "TÓM TẮT PHÂN TÍCH" not in result
        assert "KHUYẾN NGHỊ" not in result
        assert "THÔNG TIN BỔ SUNG" not in result
        assert "CHI TIẾT CÁC PHÁT HIỆN" in result  # Core section always present
    
    def test_statistics_tracking(self):
        """Test module statistics tracking."""
        initial_stats = self.module.get_module_stats()
        assert initial_stats['total_reports_generated'] == 0
        assert initial_stats['total_findings_reported'] == 0
        
        # Generate reports
        self.module.generate_text_report(self.sample_findings)
        self.module.generate_text_report([self.sample_findings[0]])
        
        stats = self.module.get_module_stats()
        assert stats['total_reports_generated'] == 2
        assert stats['total_findings_reported'] == 4  # 3 + 1
        assert stats['average_generation_time_ms'] > 0
        
        # Test reset
        self.module.reset_stats()
        reset_stats = self.module.get_module_stats()
        assert reset_stats['total_reports_generated'] == 0
    
    def test_error_handling(self):
        """Test error handling during report generation."""
        # Test with None findings (should handle gracefully)
        try:
            result = self.module.generate_text_report(None)
            # Should return error report, not crash
            assert "ERROR" in result or "LỖI" in result
        except TypeError:
            # This is also acceptable - depends on implementation
            pass
    
    def test_performance_requirements(self):
        """Test performance requirements."""
        start_time = time.time()
        result = self.module.generate_text_report(self.sample_findings)
        end_time = time.time()
        
        # Should complete quickly for small finding sets
        processing_time = (end_time - start_time) * 1000  # ms
        assert processing_time < 1000  # Less than 1 second for 3 findings
        assert len(result) > 500  # Should generate substantial report
    
    def test_confidence_score_display(self):
        """Test confidence score display in reports."""
        low_confidence_finding = AnalysisFinding(
            finding_type=AnalysisFindingType.CODE_SMELL,
            title="Potential issue",
            description="Low confidence detection",
            severity=AnalysisSeverity.LOW,
            confidence_score=0.6  # 60% confidence
        )
        
        result = self.module.generate_text_report([low_confidence_finding])
        assert "60%" in result
        assert "Độ tin cậy" in result or "Confidence" in result
    
    def test_affected_entities_display(self):
        """Test affected entities display."""
        finding_with_entities = AnalysisFinding(
            finding_type=AnalysisFindingType.ARCHITECTURAL_VIOLATION,
            title="Architecture violation",
            description="Multiple entities affected",
            severity=AnalysisSeverity.HIGH,
            affected_entities=["ClassA", "ClassB", "InterfaceC"]
        )
        
        result = self.module.generate_text_report([finding_with_entities])
        assert "ClassA, ClassB, InterfaceC" in result
        assert "Ảnh hưởng" in result or "Affects" in result
    
    @patch('teams.synthesis_reporting.report_generator_module.get_logger')
    def test_logging_integration(self, mock_get_logger):
        """Test logging integration."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        module = ReportGeneratorModule()
        module.generate_text_report(self.sample_findings)
        
        # Verify logging calls
        assert mock_logger.info.called
        mock_get_logger.assert_called_with("synthesis_reporting.report_generator")


# Additional test for integration scenarios
class TestReportGeneratorIntegration:
    """Integration tests for ReportGeneratorModule."""
    
    def test_integration_with_finding_aggregator(self):
        """Test integration with FindingAggregatorModule output."""
        from teams.synthesis_reporting.finding_aggregator_module import (
            FindingAggregatorModule, AggregationConfig
        )
        
        # Create sample findings
        findings = [
            AnalysisFinding(
                finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
                title="Test circular dependency",
                description="Test description",
                severity=AnalysisSeverity.HIGH
            ),
            AnalysisFinding(
                finding_type=AnalysisFindingType.UNUSED_PUBLIC_ELEMENT,
                title="Test unused element",
                description="Test description",
                severity=AnalysisSeverity.MEDIUM
            )
        ]
        
        # Process through FindingAggregatorModule
        aggregator = FindingAggregatorModule()
        aggregation_result = aggregator.aggregate_findings(findings)
        
        # Generate report from aggregated findings
        report_generator = ReportGeneratorModule()
        report = report_generator.generate_text_report(aggregation_result.aggregated_findings)
        
        # Verify integration works
        assert isinstance(report, str)
        assert len(report) > 0
        assert "BÁO CÁO PHÂN TÍCH CODE" in report
        assert "Test circular dependency" in report
        assert "Test unused element" in report
    
    def test_large_findings_set_performance(self):
        """Test performance with larger set of findings."""
        # Generate larger test set
        large_findings = []
        for i in range(50):
            finding = AnalysisFinding(
                finding_type=AnalysisFindingType.CODE_SMELL,
                title=f"Code smell {i}",
                description=f"Description for issue {i}",
                severity=AnalysisSeverity.LOW,
                file_path=f"src/test/TestClass{i}.java"
            )
            large_findings.append(finding)
        
        start_time = time.time()
        report_generator = ReportGeneratorModule()
        report = report_generator.generate_text_report(large_findings)
        end_time = time.time()
        
        # Performance check
        processing_time = (end_time - start_time) * 1000
        assert processing_time < 5000  # Less than 5 seconds for 50 findings
        assert len(report) > 2000  # Should generate substantial content
        assert "50" in report or "Tổng số phát hiện: 50" in report 