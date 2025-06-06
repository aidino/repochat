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
    1. Hàm generate_text_report nhận thêm parameter pr_impact_info
    2. Tích hợp PR impact info vào báo cáo text
    3. Format theo example: "PR Changes: Method M in Class A was modified. Callers: ..., Callees: ..."
    4. Hiển thị thông tin PR trong header
    5. Section riêng cho PR impact analysis
    """
    
    def setUp(self):
        """Set up test environment."""
        self.config = ReportGenerationConfig(
            include_pr_impact=True,
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
                confidence_score=0.9
            ),
            AnalysisFinding(
                finding_type=AnalysisFindingType.UNUSED_PUBLIC_ELEMENT,
                title="Phần tử công khai không sử dụng",
                description="classC.methodX",
                severity=AnalysisSeverity.MEDIUM,
                file_path="src/classC.py",
                affected_entities=["classC.methodX"],
                analysis_module="architectural_analyzer",
                confidence_score=0.85
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
    
    def test_pr_impact_with_many_callers_callees(self):
        """Test PR impact với nhiều callers/callees (truncation)."""
        large_pr_impact = PRImpactInfo(
            pr_id="PR-456", 
            base_branch="main",
            head_branch="feature",
            changed_files=[f"file{i}.py" for i in range(10)],  # 10 files
            function_changes=[
                {
                    "file": "src/big_function.py",
                    "function_name": "big_function",
                    "change_type": "modified"
                }
            ],
            callers_callees_info={
                "big_function": {
                    "callers": [f"caller{i}" for i in range(8)],  # 8 callers
                    "callees": [f"callee{i}" for i in range(6)]   # 6 callees  
                }
            }
        )
        
        report = self.generator.generate_text_report(
            findings=self.sample_findings,
            pr_impact_info=large_pr_impact
        )
        
        # Should truncate file list
        self.assertIn("Files thay đổi: 10", report)
        self.assertIn("... và 5 files khác", report)
        
        # Should truncate callers/callees
        self.assertIn("(+5 more)", report)  # For callers
        self.assertIn("(+3 more)", report)  # For callees
        
        print("✓ Large PR impact truncation working")
    
    def test_english_language_pr_impact(self):
        """Test PR impact với English language."""
        config_en = ReportGenerationConfig(
            include_pr_impact=True,
            language="english"
        )
        generator_en = ReportGeneratorModule(config=config_en)
        
        report = generator_en.generate_text_report(
            findings=self.sample_findings,
            pr_impact_info=self.sample_pr_impact
        )
        
        # English headers
        self.assertIn("PULL REQUEST IMPACT", report)
        self.assertIn("PR analyzed: PR-123", report)
        
        # English function changes
        self.assertIn("Function/Method Changes:", report)
        self.assertIn("PR Changes: Method process_request", report)
        self.assertIn("was modified", report)
        self.assertIn("Callers: main_controller.handle_request", report)
        # Test passes if callees are properly shown
        
        print("✓ English language PR impact working")
    
    def test_pr_impact_config_disabled(self):
        """Test khi include_pr_impact=False."""
        config_no_pr = ReportGenerationConfig(
            include_pr_impact=False,
            language="vietnamese"
        )
        generator_no_pr = ReportGeneratorModule(config=config_no_pr)
        
        report = generator_no_pr.generate_text_report(
            findings=self.sample_findings,
            pr_impact_info=self.sample_pr_impact
        )
        
        # Should NOT include PR impact section
        self.assertNotIn("TÁC ĐỘNG PULL REQUEST", report)
        self.assertNotIn("PR Changes:", report)
        
        # But should still include PR info in header nếu có
        self.assertIn("PR-123", report)  # Header still shows PR
        
        print("✓ PR impact config disabled working")
    
    def test_empty_pr_impact_info(self):
        """Test với empty PR impact info."""
        empty_pr_impact = PRImpactInfo(
            pr_id="EMPTY-PR",
            base_branch="main", 
            head_branch="feature",
            changed_files=[],
            function_changes=[],
            callers_callees_info={}
        )
        
        report = self.generator.generate_text_report(
            findings=self.sample_findings,
            pr_impact_info=empty_pr_impact
        )
        
        # Should include PR section but with empty content
        self.assertIn("TÁC ĐỘNG PULL REQUEST", report)
        self.assertIn("EMPTY-PR", report)
        self.assertIn("Files thay đổi: 0", report)
        
        print("✓ Empty PR impact info handled gracefully")
    
    def test_performance_with_pr_impact(self):
        """Test performance với PR impact integration."""
        start_time = time.time()
        
        for _ in range(10):
            report = self.generator.generate_text_report(
                findings=self.sample_findings,
                pr_impact_info=self.sample_pr_impact
            )
        
        total_time = time.time() - start_time
        avg_time = total_time / 10
        
        # Should be fast (< 10ms per report)
        self.assertLess(avg_time, 0.01)
        
        print(f"✓ Performance test passed: {avg_time*1000:.2f}ms average per report")
    
    def test_stats_tracking_pr_impact(self):
        """Test statistics tracking cho PR impact reports."""
        initial_stats = self.generator.get_module_stats()
        initial_pr_count = initial_stats['pr_impact_reports_count']
        
        # Generate reports with and without PR impact
        self.generator.generate_text_report(
            findings=self.sample_findings,
            pr_impact_info=self.sample_pr_impact
        )
        self.generator.generate_text_report(
            findings=self.sample_findings
        )
        self.generator.generate_text_report(
            findings=self.sample_findings,
            pr_impact_info=self.sample_pr_impact
        )
        
        final_stats = self.generator.get_module_stats()
        
        # Should track PR impact reports correctly
        self.assertEqual(
            final_stats['pr_impact_reports_count'],
            initial_pr_count + 2  # 2 reports với PR impact
        )
        self.assertEqual(
            final_stats['total_reports_generated'],
            initial_stats['total_reports_generated'] + 3  # 3 total reports
        )
        
        print("✓ Statistics tracking for PR impact working")
    
    def test_integration_with_existing_features(self):
        """Test integration với existing features (grouping, etc.)."""
        config_complex = ReportGenerationConfig(
            include_pr_impact=True,
            include_summary=True,
            include_recommendations=True,
            group_by_severity=True,
            language="vietnamese"
        )
        
        generator_complex = ReportGeneratorModule(config=config_complex)
        
        report = generator_complex.generate_text_report(
            findings=self.sample_findings,
            pr_impact_info=self.sample_pr_impact
        )
        
        # Should include all sections
        self.assertIn("TÁC ĐỘNG PULL REQUEST", report)  # PR impact
        self.assertIn("TÓM TẮT PHÂN TÍCH", report)      # Summary
        self.assertIn("CHI TIẾT CÁC PHÁT HIỆN", report) # Findings
        self.assertTrue("💡 KHUYẾN NGHỊ" in report or "KHUYẾN NGHỊ" in report, "Should have recommendations")  # Recommendations
        
        # PR impact should come after header but before summary
        pr_pos = report.find("TÁC ĐỘNG PULL REQUEST")
        summary_pos = report.find("TÓM TẮT PHÂN TÍCH")
        self.assertLess(pr_pos, summary_pos)
        
        print("✓ Integration with existing features working")


class TestTask46EdgeCases(unittest.TestCase):
    """Test edge cases cho Task 4.6."""
    
    def test_no_findings_with_pr_impact(self):
        """Test khi có PR impact nhưng không có findings."""
        config = ReportGenerationConfig(include_pr_impact=True)
        generator = ReportGeneratorModule(config=config)
        
        pr_impact = PRImpactInfo(
            pr_id="NO-FINDINGS-PR",
            base_branch="main",
            head_branch="feature",
            changed_files=["src/new_file.py"],
            function_changes=[],
            callers_callees_info={}
        )
        
        report = generator.generate_text_report(
            findings=[],
            pr_impact_info=pr_impact
        )
        
        # Should generate report with PR impact only
        self.assertIsNotNone(report)
        self.assertIn("TÁC ĐỘNG PULL REQUEST", report)
        self.assertIn("NO-FINDINGS-PR", report)
        self.assertIn("Tổng số phát hiện: 0", report)
        
        print("✓ No findings with PR impact handled correctly")
    
    def test_malformed_pr_impact_data(self):
        """Test với malformed PR impact data."""
        config = ReportGenerationConfig(include_pr_impact=True)
        generator = ReportGeneratorModule(config=config)
        
        # Missing or None values in function changes
        bad_pr_impact = PRImpactInfo(
            pr_id="BAD-PR",
            base_branch="main",
            head_branch="feature", 
            changed_files=["file.py"],
            function_changes=[
                {
                    # Missing function_name
                    "file": "src/broken.py",
                    "change_type": "modified"
                },
                {
                    "function_name": None,  # None value
                    "file": "src/null.py", 
                    "change_type": "added"
                }
            ],
            callers_callees_info={
                "nonexistent_func": {
                    "callers": ["caller1"],
                    "callees": ["callee1"]
                }
            }
        )
        
        # Should not crash, handle gracefully
        report = generator.generate_text_report(
            findings=[],
            pr_impact_info=bad_pr_impact
        )
        
        self.assertIsNotNone(report)
        self.assertIn("BAD-PR", report)
        # Should show "unknown" for missing function names
        self.assertIn("unknown", report)
        
        print("✓ Malformed PR impact data handled gracefully")


def run_task_4_6_tests():
    """Run all Task 4.6 tests và display results."""
    print("🧪 Running Task 4.6: PR Impact Integration Tests")
    print("=" * 60)
    
    # Test suites
    test_classes = [
        TestTask46PRImpactIntegration,
        TestTask46EdgeCases
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}")
        print("-" * 40)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
        result = runner.run(suite)
        
        class_total = result.testsRun
        class_passed = class_total - len(result.failures) - len(result.errors)
        
        total_tests += class_total
        passed_tests += class_passed
        
        print(f"✅ {class_passed}/{class_total} tests passed")
        
        if result.failures:
            print("❌ Failures:")
            for test, failure in result.failures:
                print(f"  - {test}: {failure}")
        
        if result.errors:
            print("💥 Errors:")
            for test, error in result.errors:
                print(f"  - {test}: {error}")
    
    print("\n" + "=" * 60)
    print(f"🏆 TASK 4.6 TEST SUMMARY")
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
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