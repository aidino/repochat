"""
Test Suite for Task 4.7: OutputFormatterModule và FinalReviewReport

This test suite verifies Task 4.7 DoD requirements:
- Pydantic model FinalReviewReport chứa trường report_content: str (và có thể là report_format: str = "text")
- Module có hàm nhận chuỗi báo cáo text từ ReportGeneratorModule
- Hàm tạo và trả về một instance của FinalReviewReport

Created: 2025-01-02
Author: RepoChat Development Team
"""

import unittest
import time
from datetime import datetime
from typing import Dict, Any

from teams.synthesis_reporting import (
    OutputFormatterModule,
    OutputFormatterConfig,
    FinalReviewReport
)


class TestTask47FinalReviewReport(unittest.TestCase):
    """
    Test FinalReviewReport Pydantic model.
    
    DoD Requirements:
    - ✅ Pydantic model FinalReviewReport chứa trường report_content: str  
    - ✅ Có thể có report_format: str = "text"
    """
    
    def test_final_review_report_basic_structure(self):
        """Test FinalReviewReport basic structure and required fields."""
        # Test với minimum required fields
        report = FinalReviewReport(
            report_content="Test report content"
        )
        
        # Required field
        self.assertEqual(report.report_content, "Test report content")
        
        # Default value
        self.assertEqual(report.report_format, "text")
        
        # Optional fields should be None by default
        self.assertIsNone(report.generated_at)
        self.assertIsNone(report.report_id) 
        self.assertEqual(report.language, "vietnamese")  # Has default
        self.assertIsNone(report.summary)
        self.assertIsNone(report.metadata)
        
        print("✓ FinalReviewReport basic structure validated")
    
    def test_final_review_report_all_fields(self):
        """Test FinalReviewReport với tất cả fields."""
        current_time = datetime.now()
        metadata = {"test": "metadata", "version": "1.0"}
        
        report = FinalReviewReport(
            report_content="Complete test report content",
            report_format="json",
            generated_at=current_time,
            report_id="test-report-123",
            language="english",
            summary="Test summary",
            metadata=metadata
        )
        
        # Validate all fields
        self.assertEqual(report.report_content, "Complete test report content")
        self.assertEqual(report.report_format, "json")
        self.assertEqual(report.generated_at, current_time)
        self.assertEqual(report.report_id, "test-report-123")
        self.assertEqual(report.language, "english")
        self.assertEqual(report.summary, "Test summary")
        self.assertEqual(report.metadata, metadata)
        
        print("✓ FinalReviewReport all fields working")
    
    def test_final_review_report_json_serialization(self):
        """Test FinalReviewReport JSON serialization."""
        current_time = datetime.now()
        
        report = FinalReviewReport(
            report_content="Serialization test",
            generated_at=current_time,
            metadata={"key": "value"}
        )
        
        # Test JSON serialization
        json_data = report.dict()
        
        self.assertIsInstance(json_data, dict)
        self.assertEqual(json_data["report_content"], "Serialization test")
        self.assertEqual(json_data["report_format"], "text")
        self.assertIsInstance(json_data["generated_at"], datetime)
        
        # Test JSON export
        json_str = report.json()
        self.assertIsInstance(json_str, str)
        self.assertIn("Serialization test", json_str)
        
        print("✓ FinalReviewReport JSON serialization working")
    
    def test_final_review_report_validation(self):
        """Test FinalReviewReport validation errors."""
        # Test empty report_content
        with self.assertRaises(Exception):  # Pydantic validation error
            FinalReviewReport(report_content="")
        
        # Test None report_content  
        with self.assertRaises(Exception):  # Pydantic validation error
            FinalReviewReport()
        
        print("✓ FinalReviewReport validation working")


class TestTask47OutputFormatterModule(unittest.TestCase):
    """
    Test OutputFormatterModule.
    
    DoD Requirements:
    - ✅ Module có hàm nhận chuỗi báo cáo text từ ReportGeneratorModule
    - ✅ Hàm tạo và trả về một instance của FinalReviewReport
    """
    
    def setUp(self):
        """Setup test environment."""
        self.config = OutputFormatterConfig(
            include_metadata=True,
            include_summary=True,
            include_timestamp=True,
            language="vietnamese"
        )
        self.formatter = OutputFormatterModule(config=self.config)
        
        # Sample report text (simulating ReportGeneratorModule output)
        self.sample_report_text = """
═══════════════════════════════════════════════════════════════
📋 BÁO CÁO PHÂN TÍCH CODE
═══════════════════════════════════════════════════════════════
🕒 Thời gian tạo: 2025-01-02 14:30:15
🔍 Tổng số phát hiện: 2

📊 TÓM TẮT PHÂN TÍCH
────────────────────────────────────────────────────────────────
• Nghiêm trọng cao: 1 phát hiện
• Nghiêm trọng trung bình: 1 phát hiện

🔍 CHI TIẾT CÁC PHÁT HIỆN
────────────────────────────────────────────────────────────────

🔴 NGHIÊM TRỌNG CAO
┌─────────────────────────────────────────────────────────────┐
│ Phụ thuộc vòng tròn                                         │
│ 📁 File: src/fileA.py                                       │
│ 📄 Mô tả: fileA -> fileB -> fileA                           │
│ 🎯 Độ tin cậy: 90%                                          │
│ 🔧 Module: architectural_analyzer                           │
└─────────────────────────────────────────────────────────────┘

🟡 NGHIÊM TRỌNG TRUNG BÌNH  
┌─────────────────────────────────────────────────────────────┐
│ Phần tử công khai không sử dụng                             │
│ 📁 File: src/classC.py                                      │
│ 📄 Mô tả: classC.methodX                                    │
│ 🎯 Độ tin cậy: 85%                                          │
│ 🔧 Module: architectural_analyzer                           │
└─────────────────────────────────────────────────────────────┘

💡 KHUYẾN NGHỊ
────────────────────────────────────────────────────────────────
• Break circular dependency
• Refactor dependency structure  
• Remove unused method
• Mark as private if used internally

📈 THỐNG KÊ
────────────────────────────────────────────────────────────────
• Tổng phát hiện: 2
• Files affected: 2
• Trung bình độ tin cậy: 87.5%
"""
    
    def test_format_text_report_basic(self):
        """Test format_text_report basic functionality (main DoD requirement)."""
        # DoD: Module có hàm nhận chuỗi báo cáo text từ ReportGeneratorModule
        result = self.formatter.format_text_report(self.sample_report_text)
        
        # DoD: Hàm tạo và trả về một instance của FinalReviewReport
        self.assertIsInstance(result, FinalReviewReport)
        
        # Verify content
        self.assertEqual(result.report_content, self.sample_report_text)
        self.assertEqual(result.report_format, "text")
        self.assertEqual(result.language, "vietnamese")
        
        # Should have timestamp
        self.assertIsNotNone(result.generated_at)
        self.assertIsInstance(result.generated_at, datetime)
        
        # Should have report_id
        self.assertIsNotNone(result.report_id)
        self.assertIsInstance(result.report_id, str)
        
        # Should have summary
        self.assertIsNotNone(result.summary)
        self.assertIn("BÁO CÁO PHÂN TÍCH CODE", result.summary)
        
        # Should have metadata
        self.assertIsNotNone(result.metadata)
        self.assertIn("original_length", result.metadata)
        self.assertIn("lines_count", result.metadata)
        
        print("✓ format_text_report basic functionality working")
        print(f"  - Report ID: {result.report_id}")
        print(f"  - Content length: {len(result.report_content)}")
        print(f"  - Summary: {result.summary[:50]}...")
    
    def test_format_text_report_with_custom_params(self):
        """Test format_text_report với custom parameters."""
        custom_metadata = {"source": "test", "version": "1.0"}
        custom_id = "custom-test-report-123"
        
        result = self.formatter.format_text_report(
            report_text=self.sample_report_text,
            report_id=custom_id,
            metadata=custom_metadata
        )
        
        # Verify custom parameters
        self.assertEqual(result.report_id, custom_id)
        self.assertIn("source", result.metadata)
        self.assertEqual(result.metadata["source"], "test")
        self.assertEqual(result.metadata["version"], "1.0")
        
        # Should still have formatter metadata
        self.assertIn("original_length", result.metadata)
        self.assertIn("processing_time", result.metadata)
        
        print("✓ format_text_report with custom parameters working")
    
    def test_format_text_report_empty_input(self):
        """Test format_text_report với empty/invalid input."""
        # Test empty string
        with self.assertRaises(ValueError):
            self.formatter.format_text_report("")
        
        # Test None input
        with self.assertRaises(ValueError):
            self.formatter.format_text_report(None)
        
        # Test non-string input
        with self.assertRaises(ValueError):
            self.formatter.format_text_report(123)
        
        print("✓ format_text_report input validation working")
    
    def test_output_formatter_config_variations(self):
        """Test OutputFormatterModule với different configurations."""
        # Config without metadata
        config_minimal = OutputFormatterConfig(
            include_metadata=False,
            include_summary=False,
            include_timestamp=False,
            language="english"
        )
        
        formatter_minimal = OutputFormatterModule(config=config_minimal)
        result = formatter_minimal.format_text_report("Simple test report")
        
        # Should not have metadata/summary/timestamp
        self.assertIsNone(result.metadata)
        self.assertIsNone(result.summary) 
        self.assertIsNone(result.generated_at)
        self.assertEqual(result.language, "english")
        
        print("✓ OutputFormatterConfig variations working")
    
    def test_default_config(self):
        """Test OutputFormatterModule với default config."""
        formatter_default = OutputFormatterModule()
        result = formatter_default.format_text_report("Default config test")
        
        # Should use defaults
        self.assertEqual(result.report_format, "text")
        self.assertEqual(result.language, "vietnamese") 
        self.assertIsNotNone(result.generated_at)  # include_timestamp=True default
        
        print("✓ Default configuration working")
    
    def test_module_statistics(self):
        """Test module statistics tracking."""
        initial_stats = self.formatter.get_module_stats()
        self.assertEqual(initial_stats["reports_formatted"], 0)
        
        # Format some reports
        self.formatter.format_text_report("Report 1")
        self.formatter.format_text_report("Report 2")
        self.formatter.format_text_report("Report 3")
        
        final_stats = self.formatter.get_module_stats()
        
        # Check statistics
        self.assertEqual(final_stats["reports_formatted"], 3)
        self.assertGreater(final_stats["total_processing_time"], 0)
        self.assertIsNotNone(final_stats["last_format_time"])
        self.assertGreater(final_stats["average_processing_time"], 0)
        
        print("✓ Module statistics tracking working")
    
    def test_report_id_generation(self):
        """Test automatic report ID generation."""
        result1 = self.formatter.format_text_report("Report 1")
        result2 = self.formatter.format_text_report("Report 2")
        
        # IDs should be different
        self.assertNotEqual(result1.report_id, result2.report_id)
        
        # Should contain timestamp and sequence
        self.assertIn("report_", result1.report_id)
        self.assertIn("report_", result2.report_id)
        
        print("✓ Report ID generation working")
    
    def test_summary_extraction(self):
        """Test summary extraction logic."""
        result = self.formatter.format_text_report(self.sample_report_text)
        
        # Should extract meaningful summary
        self.assertIsNotNone(result.summary)
        self.assertIn("BÁO CÁO", result.summary)
        
        # Test with simple text
        simple_result = self.formatter.format_text_report("Simple report\nNo special headers")
        self.assertEqual(simple_result.summary, "Simple report")
        
        print("✓ Summary extraction working")
    
    def test_integration_with_report_generator_output(self):
        """Test integration với realistic ReportGeneratorModule output."""
        # This simulates actual output from Task 4.5 ReportGeneratorModule
        realistic_report = """
═══════════════════════════════════════════════════════════════
📋 BÁO CÁO PHÂN TÍCH CODE
═══════════════════════════════════════════════════════════════
🕒 Thời gian tạo: 2025-01-02 15:30:45
🔍 Tổng số phát hiện: 1

📊 TÓM TẮT PHÂN TÍCH
────────────────────────────────────────────────────────────────
• Nghiêm trọng cao: 1 phát hiện

🔍 CHI TIẾT CÁC PHÁT HIỆN
────────────────────────────────────────────────────────────────

🔴 NGHIÊM TRỌNG CAO
┌─────────────────────────────────────────────────────────────┐
│ Phụ thuộc vòng tròn                                         │
│ 📁 File: fileA.py                                           │
│ 📄 Mô tả: fileA -> fileB -> fileA                           │
└─────────────────────────────────────────────────────────────┘
"""
        
        result = self.formatter.format_text_report(realistic_report)
        
        # Should handle realistic input correctly
        self.assertIsInstance(result, FinalReviewReport)
        self.assertEqual(result.report_content, realistic_report)
        self.assertIn("fileA -> fileB -> fileA", result.report_content)
        
        # Metadata should include realistic stats
        self.assertGreater(result.metadata["original_length"], 500)
        self.assertGreater(result.metadata["lines_count"], 10)
        
        print("✓ Integration with ReportGeneratorModule output working")
    
    def test_performance(self):
        """Test performance of OutputFormatterModule."""
        start_time = time.time()
        
        # Format multiple reports
        for i in range(10):
            self.formatter.format_text_report(f"Performance test report {i}")
        
        total_time = time.time() - start_time
        average_time = total_time / 10
        
        # Should be fast (< 1ms per report)
        self.assertLess(average_time, 0.001)
        
        stats = self.formatter.get_module_stats()
        self.assertEqual(stats["reports_formatted"], 10)
        
        print(f"✓ Performance test passed: {average_time*1000:.2f}ms average per report")


def run_task_4_7_tests():
    """Run all Task 4.7 tests và display results."""
    print("🧪 Running Task 4.7: OutputFormatterModule và FinalReviewReport Tests")
    print("=" * 70)
    
    # Test suites
    test_classes = [
        TestTask47FinalReviewReport,
        TestTask47OutputFormatterModule
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}")
        print("-" * 50)
        
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
                print(f"  - {test}: {failure.split('AssertionError:')[-1] if 'AssertionError:' in failure else failure}")
        
        if result.errors:
            print("💥 Errors:")
            for test, error in result.errors:
                print(f"  - {test}: {error.split('Exception:')[-1] if 'Exception:' in error else error}")
    
    print("\n" + "=" * 70)
    print(f"🏆 TASK 4.7 TEST SUMMARY")
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 ALL TASK 4.7 TESTS PASSED!")
        print("✅ FinalReviewReport Pydantic Model: VERIFIED")
        print("✅ OutputFormatterModule: VERIFIED") 
        print("✅ DoD Requirements: SATISFIED")
        return True
    else:
        print("❌ Some tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = run_task_4_7_tests()
    exit(0 if success else 1) 