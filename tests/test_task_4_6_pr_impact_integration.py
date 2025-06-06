"""
Test Suite for Task 4.6: PR Impact Integration in ReportGeneratorModule

This test suite verifies Task 4.6 DoD requirements:
- Hàm tạo báo cáo cũng nhận thông tin phân tích tác động PR (từ F3.7)
- Tích hợp thông tin này vào báo cáo text (ví dụ: "PR Changes: Method M in Class A was modified. Callers: ..., Callees: ...")

Created: 2025-01-02
Author: RepoChat Development Team
"""

import unittest
import time
from typing import List, Dict, Any

from teams.synthesis_reporting import (
    ReportGeneratorModule, 
    ReportGenerationConfig, 
    PRImpactInfo
)
from teams.code_analysis.models import (
    AnalysisFinding, 
    AnalysisFindingType, 
    AnalysisSeverity
)


class TestTask46PRImpactIntegration(unittest.TestCase):
    """
    Test Task 4.6: PR Impact Integration trong ReportGeneratorModule.
    
    DoD Requirements:
    - ✅ Hàm tạo báo cáo cũng nhận thông tin phân tích tác động PR (từ F3.7)
    - ✅ Tích hợp thông tin này vào báo cáo text với format:
      "PR Changes: Method M in Class A was modified. Callers: ..., Callees: ..."
    """
    
    def setUp(self):
        """Setup test environment."""
        self.config = ReportGenerationConfig(
            include_pr_impact=True,
            include_summary=True,
            include_recommendations=True,
            language="vietnamese"
        )
        self.generator = ReportGeneratorModule(config=self.config)
        
        # Sample findings
        self.sample_findings = [
            AnalysisFinding(
                finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
                title="Phụ thuộc vòng tròn",
                description="fileA -> fileB -> fileA",
                severity=AnalysisSeverity.HIGH,
                file_path="src/fileA.py",
                affected_entities=["fileA", "fileB"],
                analysis_module="architectural_analyzer",
                confidence_score=0.9,
                recommendations=["Break circular dependency", "Refactor dependency structure"]
            ),
            AnalysisFinding(
                finding_type=AnalysisFindingType.UNUSED_PUBLIC_ELEMENT,
                title="Phần tử công khai không sử dụng",
                description="classC.methodX",
                severity=AnalysisSeverity.MEDIUM,
                file_path="src/classC.py",
                affected_entities=["classC.methodX"],
                analysis_module="architectural_analyzer",
                confidence_score=0.85,
                recommendations=["Remove unused method", "Mark as private if used internally"]
            )
        ]
        
        # Sample PR impact info
        self.sample_pr_impact = PRImpactInfo(
            pr_id="PR-123",
            base_branch="main",
            head_branch="feature/new-function",
            changed_files=["src/service.py", "src/utils.py", "test/test_service.py"],
            function_changes=[
                {
                    "file": "src/service.py",
                    "function_name": "process_request",
                    "change_type": "modified",
                    "line_number": 25
                },
                {
                    "file": "src/utils.py", 
                    "function_name": "helper_function",
                    "change_type": "added",
                    "line_number": 10
                }
            ],
            callers_callees_info={
                "process_request": {
                    "callers": ["main_controller.handle_request", "api_handler.process"],
                    "callees": ["database.save", "utils.validate", "logger.info"]
                },
                "helper_function": {
                    "callers": [],
                    "callees": ["json.loads", "string.strip"]
                }
            }
        )
    
    def test_pr_impact_info_dataclass(self):
        """Test PRImpactInfo dataclass structure."""
        pr_info = PRImpactInfo(
            pr_id="test-pr",
            base_branch="main",
            head_branch="feature",
            changed_files=["file1.py"],
            function_changes=[],
            callers_callees_info={}
        )
        
        self.assertEqual(pr_info.pr_id, "test-pr")
        self.assertEqual(pr_info.base_branch, "main")
        self.assertEqual(pr_info.head_branch, "feature")
        self.assertEqual(pr_info.changed_files, ["file1.py"])
        self.assertEqual(pr_info.function_changes, [])
        self.assertEqual(pr_info.callers_callees_info, {})
        
        print("✓ PRImpactInfo dataclass structure validated")
    
    def test_generate_text_report_with_pr_impact(self):
        """Test generate_text_report với PR impact info (main DoD requirement)."""
        report = self.generator.generate_text_report(
            findings=self.sample_findings,
            pr_impact_info=self.sample_pr_impact
        )
        
        # Basic structure checks
        self.assertIsNotNone(report)
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 0)
        
        # PR info in header 
        self.assertIn("PR-123", report)
        self.assertIn("main ← feature/new-function", report)
        
        # PR Impact section should exist
        self.assertIn("TÁC ĐỘNG PULL REQUEST", report)
        
        # DoD example format: "PR Changes: Method M in Class A was modified. Callers: ..., Callees: ..."
        self.assertIn("Thay đổi PR: Method process_request", report)
        self.assertIn("đã được modified", report)
        self.assertIn("Callers:", report)
        self.assertIn("Callees:", report)
        
        # Function changes should be listed
        self.assertIn("process_request", report)
        self.assertIn("helper_function", report)
        
        # Caller/callee info should be shown
        self.assertIn("main_controller.handle_request", report)
        self.assertIn("database.save", report)
        
        print("✓ Report generation with PR impact working")
        print(f"  - Report length: {len(report)} characters")
    
    def test_generate_text_report_without_pr_impact(self):
        """Test generate_text_report không có PR impact (backward compatibility)."""
        report = self.generator.generate_text_report(
            findings=self.sample_findings
        )
        
        # Should work normally without PR impact
        self.assertIsNotNone(report)
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 0)
        
        # Should NOT contain PR impact section
        self.assertNotIn("TÁC ĐỘNG PULL REQUEST", report)
        self.assertNotIn("PR Changes:", report)
        
        # Should still contain findings
        self.assertIn("Phụ thuộc vòng tròn", report)
        self.assertIn("fileA -> fileB -> fileA", report)
        
        print("✓ Backward compatibility without PR impact working")
    
    def test_pr_impact_section_generation(self):
        """Test _generate_pr_impact_section method chi tiết."""
        pr_impact_section = self.generator._generate_pr_impact_section(self.sample_pr_impact)
        
        self.assertIsNotNone(pr_impact_section)
        self.assertIsInstance(pr_impact_section, str)
        
        # Section title
        self.assertIn("TÁC ĐỘNG PULL REQUEST", pr_impact_section)
        
        # PR information
        self.assertIn("PR-123", pr_impact_section)
        self.assertIn("main ← feature/new-function", pr_impact_section)
        
        # Files changed
        self.assertIn("Files thay đổi: 3", pr_impact_section)
        self.assertIn("src/service.py", pr_impact_section)
        self.assertIn("src/utils.py", pr_impact_section)
        
        # Function changes với DoD format
        self.assertIn("Thay đổi Functions/Methods:", pr_impact_section)
        
        # DoD requirement: "PR Changes: Method M in Class A was modified. Callers: ..., Callees: ..."
        self.assertIn("Thay đổi PR: Method process_request", pr_impact_section)
        self.assertIn("đã được modified", pr_impact_section)
        self.assertIn("Callers: main_controller.handle_request, api_handler.process", pr_impact_section)
        self.assertIn("Callees: database.save, utils.validate, logger.info", pr_impact_section)
        
        # Added function
        self.assertIn("Thay đổi PR: Method helper_function", pr_impact_section)
        self.assertIn("đã được added", pr_impact_section)
        self.assertIn("Callers: không có", pr_impact_section)
        self.assertIn("Callees: json.loads, string.strip", pr_impact_section)
        
        print("✓ PR impact section generation working correctly")
    
    def test_empty_pr_impact_info(self):
        """Test với empty/None PR impact info."""
        # Test với None
        report1 = self.generator.generate_text_report(
            findings=self.sample_findings,
            pr_impact_info=None
        )
        
        self.assertIsNotNone(report1)
        self.assertNotIn("TÁC ĐỘNG PULL REQUEST", report1)
        
        # Test với empty PRImpactInfo
        empty_pr_impact = PRImpactInfo(
            pr_id="",
            base_branch="",
            head_branch="",
            changed_files=[],
            function_changes=[],
            callers_callees_info={}
        )
        
        report2 = self.generator.generate_text_report(
            findings=self.sample_findings,
            pr_impact_info=empty_pr_impact
        )
        
        self.assertIsNotNone(report2)
        # Should handle empty gracefully
        
        print("✓ Empty PR impact info handled gracefully")


def run_task_4_6_tests():
    """Run all Task 4.6 tests và display results."""
    print("🧪 Running Task 4.6: PR Impact Integration Tests")
    print("=" * 60)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask46PRImpactIntegration)
    runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
    result = runner.run(suite)
    
    total_tests = result.testsRun
    passed_tests = total_tests - len(result.failures) - len(result.errors)
    
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if result.failures:
        print("❌ Failures:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")
    
    if result.errors:
        print("💥 Errors:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    if passed_tests == total_tests:
        print("🎉 ALL TASK 4.6 TESTS PASSED!")
        print("✅ PR Impact Integration: VERIFIED")
        print("✅ DoD Requirements: SATISFIED")
        return True
    else:
        print("❌ Some tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = run_task_4_6_tests()
    exit(0 if success else 1) 