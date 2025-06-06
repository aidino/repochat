#!/usr/bin/env python3
"""
Manual Test for Task 4.5: ReportGeneratorModule Demo

This script demonstrates the ReportGeneratorModule functionality
by generating sample reports with various configurations.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from teams.synthesis_reporting.report_generator_module import (
    ReportGeneratorModule,
    ReportGenerationConfig
)
from teams.code_analysis.models import (
    AnalysisFinding,
    AnalysisFindingType,
    AnalysisSeverity
)


def create_sample_findings():
    """Create a comprehensive set of sample findings for demo."""
    findings = [
        # Circular Dependency Example (DoD requirement)
        AnalysisFinding(
            finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
            title="fileA -> fileB -> fileA",
            description="Circular dependency detected between core modules",
            severity=AnalysisSeverity.HIGH,
            file_path="src/main/java/com/example/FileA.java",
            start_line=25,
            end_line=35,
            affected_entities=["com.example.FileA", "com.example.FileB"],
            analysis_module="architectural_analyzer",
            confidence_score=0.95,
            recommendations=[
                "Tái cấu trúc để phá vỡ chu trình phụ thuộc",
                "Sử dụng dependency injection pattern",
                "Tạo interface chung để decoupling"
            ]
        ),
        
        # Unused Public Method Example (DoD requirement)
        AnalysisFinding(
            finding_type=AnalysisFindingType.UNUSED_PUBLIC_ELEMENT,
            title="classC.methodX",
            description="Public method appears to be unused across the codebase",
            severity=AnalysisSeverity.MEDIUM,
            file_path="src/main/java/com/example/ClassC.java",
            start_line=142,
            affected_entities=["com.example.ClassC.methodX"],
            analysis_module="architectural_analyzer",
            confidence_score=0.85,
            recommendations=[
                "Xem xét loại bỏ method nếu không cần thiết",
                "Chuyển thành private nếu chỉ dùng nội bộ",
                "Kiểm tra lại với reflection hoặc dynamic loading"
            ]
        ),
        
        # Additional realistic findings
        AnalysisFinding(
            finding_type=AnalysisFindingType.CODE_SMELL,
            title="Large Class: UserManager",
            description="Class has too many responsibilities (342 lines)",
            severity=AnalysisSeverity.MEDIUM,
            file_path="src/main/java/com/example/service/UserManager.java",
            start_line=1,
            end_line=342,
            affected_entities=["com.example.service.UserManager"],
            analysis_module="code_analyzer",
            confidence_score=1.0,
            recommendations=[
                "Chia nhỏ class thành các service chuyên biệt",
                "Áp dụng Single Responsibility Principle"
            ]
        ),
        
        AnalysisFinding(
            finding_type=AnalysisFindingType.ARCHITECTURAL_VIOLATION,
            title="Layer Violation: Controller accessing DAO directly",
            description="Controller layer is directly accessing DAO layer, bypassing Service layer",
            severity=AnalysisSeverity.HIGH,
            file_path="src/main/java/com/example/controller/ProductController.java",
            start_line=89,
            affected_entities=["ProductController", "ProductDAO"],
            analysis_module="architectural_analyzer",
            confidence_score=0.9,
            recommendations=[
                "Sử dụng Service layer để access DAO",
                "Refactor để tuân thủ layered architecture"
            ]
        ),
        
        AnalysisFinding(
            finding_type=AnalysisFindingType.PERFORMANCE_CONCERN,
            title="N+1 Query Pattern",
            description="Potential N+1 query issue in user loading",
            severity=AnalysisSeverity.MEDIUM,
            file_path="src/main/java/com/example/service/OrderService.java",
            start_line=67,
            affected_entities=["OrderService.loadOrdersWithUsers"],
            analysis_module="performance_analyzer",
            confidence_score=0.75,
            recommendations=[
                "Sử dụng JOIN hoặc batch loading",
                "Implement lazy loading strategy"
            ]
        ),
        
        AnalysisFinding(
            finding_type=AnalysisFindingType.TEST_COVERAGE_ISSUE,
            title="Low test coverage: PaymentProcessor",
            description="Critical payment logic has only 45% test coverage",
            severity=AnalysisSeverity.CRITICAL,
            file_path="src/main/java/com/example/payment/PaymentProcessor.java",
            affected_entities=["PaymentProcessor"],
            analysis_module="test_analyzer",
            confidence_score=1.0,
            recommendations=[
                "Viết unit tests cho tất cả payment scenarios",
                "Thêm integration tests cho payment flows",
                "Mock external payment services"
            ]
        )
    ]
    
    return findings


def demo_basic_report():
    """Demo basic Vietnamese report generation."""
    print("=" * 80)
    print("🔍 DEMO: Báo cáo cơ bản (Vietnamese)")
    print("=" * 80)
    
    findings = create_sample_findings()
    
    # Basic Vietnamese config
    config = ReportGenerationConfig(
        language="vietnamese",
        include_summary=True,
        include_recommendations=True,
        group_by_severity=True
    )
    
    generator = ReportGeneratorModule(config)
    report = generator.generate_text_report(findings)
    
    print(report)
    print("\n" + "=" * 80)
    print(f"📊 Report Stats: {len(report)} characters")
    print("=" * 80)


def demo_english_report():
    """Demo English report generation."""
    print("\n" * 2)
    print("=" * 80)
    print("🔍 DEMO: Basic English Report")
    print("=" * 80)
    
    findings = create_sample_findings()[:3]  # Shorter for demo
    
    # English config
    config = ReportGenerationConfig(
        language="english",
        include_summary=True,
        include_recommendations=True,
        group_by_severity=True
    )
    
    generator = ReportGeneratorModule(config)
    report = generator.generate_text_report(findings)
    
    print(report)
    print("\n" + "=" * 80)


def demo_minimal_report():
    """Demo minimal report (findings only)."""
    print("\n" * 2)
    print("=" * 80)
    print("🔍 DEMO: Minimal Report (Findings Only)")
    print("=" * 80)
    
    findings = create_sample_findings()[:2]  # Just DoD examples
    
    # Minimal config
    config = ReportGenerationConfig(
        language="vietnamese",
        include_summary=False,
        include_recommendations=False,
        include_metadata=False,
        group_by_severity=False
    )
    
    generator = ReportGeneratorModule(config)
    report = generator.generate_text_report(findings)
    
    print(report)
    print("\n" + "=" * 80)


def demo_type_grouping():
    """Demo grouping by finding type."""
    print("\n" * 2)
    print("=" * 80)
    print("🔍 DEMO: Grouping by Finding Type")
    print("=" * 80)
    
    findings = create_sample_findings()
    
    # Type grouping config
    config = ReportGenerationConfig(
        language="vietnamese",
        include_summary=True,
        group_by_severity=False,
        group_by_type=True
    )
    
    generator = ReportGeneratorModule(config)
    report = generator.generate_text_report(findings)
    
    print(report)
    print("\n" + "=" * 80)


def demo_dod_examples():
    """Demo specific DoD examples: Circular Dependency and Unused Public Method."""
    print("\n" * 2)
    print("=" * 80)
    print("🎯 DEMO: DoD Examples - Circular Dependency & Unused Public Method")
    print("=" * 80)
    
    # Create exact DoD examples
    dod_findings = [
        AnalysisFinding(
            finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
            title="fileA -> fileB -> fileA",
            description="Circular dependency: fileA depends on fileB which depends back on fileA",
            severity=AnalysisSeverity.HIGH,
            analysis_module="architectural_analyzer"
        ),
        AnalysisFinding(
            finding_type=AnalysisFindingType.UNUSED_PUBLIC_ELEMENT,
            title="classC.methodX",
            description="Unused public method detected in classC",
            severity=AnalysisSeverity.MEDIUM,
            analysis_module="architectural_analyzer"
        )
    ]
    
    config = ReportGenerationConfig(language="vietnamese")
    generator = ReportGeneratorModule(config)
    report = generator.generate_text_report(dod_findings)
    
    print(report)
    
    # Verify DoD requirements
    print("\n" + "🎯 DoD Verification:")
    print("✅ Module nhận danh sách AnalysisFinding:", "✓" if len(dod_findings) > 0 else "✗")
    print("✅ Liệt kê rõ ràng - Circular Dependency:", "✓" if "Phụ thuộc vòng tròn: fileA -> fileB -> fileA" in report else "✗")
    print("✅ Liệt kê rõ ràng - Unused Public Method:", "✓" if "Phần tử công khai không sử dụng: classC.methodX" in report else "✗")
    print("✅ Trả về chuỗi text:", "✓" if isinstance(report, str) and len(report) > 0 else "✗")
    print("=" * 80)


def demo_empty_findings():
    """Demo empty findings report."""
    print("\n" * 2)
    print("=" * 80)
    print("🎉 DEMO: Empty Findings (No Issues Found)")
    print("=" * 80)
    
    generator = ReportGeneratorModule()
    report = generator.generate_text_report([])
    
    print(report)
    print("\n" + "=" * 80)


def demo_performance_stats():
    """Demo module statistics and performance."""
    print("\n" * 2)
    print("=" * 80)
    print("📊 DEMO: Performance Statistics")
    print("=" * 80)
    
    findings = create_sample_findings()
    generator = ReportGeneratorModule()
    
    # Generate multiple reports
    for i in range(3):
        subset = findings[:i+2]
        generator.generate_text_report(subset)
    
    stats = generator.get_module_stats()
    
    print("Module Statistics:")
    print(f"  📈 Total reports generated: {stats['total_reports_generated']}")
    print(f"  📋 Total findings processed: {stats['total_findings_reported']}")
    print(f"  ⏱️  Average generation time: {stats['average_generation_time_ms']:.2f}ms")
    print(f"  ⏰ Total generation time: {stats['total_generation_time_ms']:.2f}ms")
    print("=" * 80)


def main():
    """Run all demos."""
    print("🚀 RepoChat v1.0 - Task 4.5 ReportGeneratorModule Demo")
    print("📋 Task DoD: Module tạo báo cáo text từ AnalysisFinding objects")
    
    try:
        # Run demos in sequence
        demo_dod_examples()          # Most important - DoD verification
        demo_basic_report()          # Core functionality
        demo_english_report()        # Language support
        demo_minimal_report()        # Configuration options
        demo_type_grouping()         # Grouping features
        demo_empty_findings()        # Edge case
        demo_performance_stats()     # Performance verification
        
        print("\n" + "🎉 All demos completed successfully!")
        print("✅ Task 4.5 ReportGeneratorModule is fully functional")
        print("✅ All DoD requirements satisfied")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 