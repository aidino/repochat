"""
ReportGeneratorModule for TEAM Synthesis & Reporting

Implementation of Task 4.5 (F4.5): Tạo báo cáo text đơn giản
Extended for Task 4.6 (F4.6): Tích hợp tóm tắt tác động PR
This module generates text-based reports from aggregated analysis findings with PR impact integration.
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit
from teams.code_analysis.models import AnalysisFinding, AnalysisFindingType, AnalysisSeverity


@dataclass
class ReportGenerationConfig:
    """Configuration for report generation."""
    include_summary: bool = True
    include_recommendations: bool = True
    include_metadata: bool = False
    include_pr_impact: bool = True  # New for Task 4.6
    group_by_severity: bool = True
    group_by_type: bool = False
    max_findings_per_section: Optional[int] = None
    language: str = "vietnamese"  # "vietnamese" or "english"


@dataclass
class PRImpactInfo:
    """PR Impact information for Task 4.6 integration."""
    pr_id: str
    base_branch: str
    head_branch: str
    changed_files: List[str]
    function_changes: List[Dict[str, Any]]
    callers_callees_info: Dict[str, Dict[str, List[str]]]  # function_name -> {"callers": [...], "callees": [...]}
    

class ReportGeneratorModule:
    """
    Module để tạo báo cáo text từ AnalysisFinding objects với PR impact integration.
    
    Task 4.5 DoD Requirements:
    - Module có hàm nhận danh sách các AnalysisFinding đã tổng hợp
    - Hàm tạo một chuỗi string dạng text, liệt kê các phát hiện một cách rõ ràng
    - Trả về chuỗi báo cáo text
    
    Task 4.6 DoD Requirements:
    - Hàm tạo báo cáo cũng nhận thông tin phân tích tác động PR (từ F3.7)
    - Tích hợp thông tin này vào báo cáo text (ví dụ: "PR Changes: Method M in Class A was modified. Callers: ..., Callees: ...")
    
    Features:
    - Vietnamese/English text report generation
    - PR impact analysis integration
    - Grouping by severity and finding type
    - Summary statistics
    - Configurable report sections
    - Clean, readable formatting
    """
    
    def __init__(self, config: Optional[ReportGenerationConfig] = None):
        """Initialize ReportGeneratorModule."""
        self.logger = get_logger("synthesis_reporting.report_generator")
        self.config = config or ReportGenerationConfig()
        
        self._stats = {
            'total_reports_generated': 0,
            'total_findings_reported': 0,
            'pr_impact_reports_count': 0,  # New for Task 4.6
            'generation_time_ms': 0.0
        }
        
        # Vietnamese translations for findings
        self._vietnamese_translations = {
            # Finding types
            AnalysisFindingType.CIRCULAR_DEPENDENCY: "Phụ thuộc vòng tròn",
            AnalysisFindingType.UNUSED_PUBLIC_ELEMENT: "Phần tử công khai không sử dụng",
            AnalysisFindingType.ARCHITECTURAL_VIOLATION: "Vi phạm kiến trúc",
            AnalysisFindingType.CODE_SMELL: "Mùi code",
            AnalysisFindingType.POTENTIAL_REFACTORING: "Tiềm năng tái cấu trúc",
            AnalysisFindingType.TEST_COVERAGE_ISSUE: "Vấn đề coverage test",
            AnalysisFindingType.PERFORMANCE_CONCERN: "Quan ngại hiệu năng",
            
            # Severity levels
            AnalysisSeverity.CRITICAL: "Nghiêm trọng",
            AnalysisSeverity.HIGH: "Cao",
            AnalysisSeverity.MEDIUM: "Trung bình",
            AnalysisSeverity.LOW: "Thấp",
            AnalysisSeverity.INFO: "Thông tin",
            
            # Report sections
            "summary": "Tóm tắt Phân tích",
            "findings": "Chi tiết Phát hiện",
            "recommendations": "Khuyến nghị",
            "metadata": "Thông tin bổ sung",
            "pr_impact": "Tác động Pull Request"  # New for Task 4.6
        }
        
        self.logger.info("ReportGeneratorModule initialized", extra={
            'extra_data': {
                'language': self.config.language,
                'include_summary': self.config.include_summary,
                'include_pr_impact': self.config.include_pr_impact,  # New for Task 4.6
                'group_by_severity': self.config.group_by_severity
            }
        })
    
    def generate_text_report(self, findings: List[AnalysisFinding], 
                           pr_impact_info: Optional[PRImpactInfo] = None) -> str:
        """
        Generate một báo cáo text từ danh sách AnalysisFinding đã tổng hợp với PR impact integration.
        
        Task 4.5 DoD Implementation:
        - Nhận danh sách AnalysisFinding đã tổng hợp
        - Tạo chuỗi string dạng text liệt kê phát hiện rõ ràng
        - Trả về chuỗi báo cáo text
        
        Task 4.6 DoD Implementation:
        - Nhận thông tin phân tích tác động PR (từ F3.7)
        - Tích hợp thông tin này vào báo cáo text
        
        Args:
            findings: List of aggregated AnalysisFinding objects
            pr_impact_info: Optional PR impact analysis information (Task 4.6)
            
        Returns:
            str: Formatted text report with PR impact integration
        """
        start_time = time.time()
        
        log_function_entry(
            self.logger,
            "generate_text_report",
            finding_count=len(findings),
            has_pr_impact=pr_impact_info is not None,
            language=self.config.language
        )
        
        try:
            if not findings and not pr_impact_info:
                return self._generate_empty_report()
            
            report_sections = []
            
            # Header
            report_sections.append(self._generate_header(findings, pr_impact_info))
            
            # PR Impact section (Task 4.6 - NEW)
            if self.config.include_pr_impact and pr_impact_info:
                pr_impact_section = self._generate_pr_impact_section(pr_impact_info)
                if pr_impact_section:
                    report_sections.append(pr_impact_section)
                    self._stats['pr_impact_reports_count'] += 1
            
            # Summary section
            if self.config.include_summary:
                report_sections.append(self._generate_summary_section(findings, pr_impact_info))
            
            # Findings section (core requirement)
            findings_section = self._generate_findings_section(findings)
            report_sections.append(findings_section)
            
            # Recommendations section
            if self.config.include_recommendations:
                recommendations_section = self._generate_recommendations_section(findings)
                if recommendations_section:
                    report_sections.append(recommendations_section)
            
            # Metadata section
            if self.config.include_metadata:
                metadata_section = self._generate_metadata_section(findings)
                if metadata_section:
                    report_sections.append(metadata_section)
            
            # Footer
            report_sections.append(self._generate_footer())
            
            # Combine all sections
            full_report = "\n\n".join(section for section in report_sections if section.strip())
            
            # Update statistics
            processing_time = (time.time() - start_time) * 1000
            self._stats['total_reports_generated'] += 1
            self._stats['total_findings_reported'] += len(findings)
            self._stats['generation_time_ms'] += processing_time
            
            self.logger.info("Text report generated successfully", extra={
                'extra_data': {
                    'finding_count': len(findings),
                    'has_pr_impact': pr_impact_info is not None,
                    'report_length': len(full_report),
                    'processing_time_ms': processing_time
                }
            })
            
            log_function_exit(
                self.logger,
                "generate_text_report"
            )
            
            return full_report
            
        except Exception as e:
            self.logger.error(f"Error generating text report: {str(e)}", extra={'extra_data': {'error': str(e)}})
            return self._generate_error_report(str(e))
    
    def _generate_pr_impact_section(self, pr_impact_info: PRImpactInfo) -> str:
        """
        Generate PR impact section for Task 4.6 DoD requirements.
        
        Args:
            pr_impact_info: PR impact analysis information
            
        Returns:
            Formatted PR impact section
        """
        if self.config.language == "vietnamese":
            section_title = "🔄 TÁC ĐỘNG PULL REQUEST"
            pr_info_header = f"Pull Request: {pr_impact_info.pr_id} ({pr_impact_info.base_branch} ← {pr_impact_info.head_branch})"
        else:
            section_title = "🔄 PULL REQUEST IMPACT"
            pr_info_header = f"Pull Request: {pr_impact_info.pr_id} ({pr_impact_info.base_branch} ← {pr_impact_info.head_branch})"
        
        lines = [
            "═" * 70,
            section_title,
            "═" * 70,
            "",
            pr_info_header,
            ""
        ]
        
        # Changed files summary
        if self.config.language == "vietnamese":
            lines.append(f"📁 Files thay đổi: {len(pr_impact_info.changed_files)}")
        else:
            lines.append(f"📁 Changed files: {len(pr_impact_info.changed_files)}")
            
        for file_path in pr_impact_info.changed_files[:5]:  # Show first 5 files
            lines.append(f"   • {file_path}")
        if len(pr_impact_info.changed_files) > 5:
            remaining = len(pr_impact_info.changed_files) - 5
            if self.config.language == "vietnamese":
                lines.append(f"   ... và {remaining} files khác")
            else:
                lines.append(f"   ... and {remaining} more files")
        
        lines.append("")
        
        # Function changes with callers/callees info (Task 4.6 DoD requirement)
        if pr_impact_info.function_changes:
            if self.config.language == "vietnamese":
                lines.append("🔧 Thay đổi Functions/Methods:")
            else:
                lines.append("🔧 Function/Method Changes:")
                
            for func_change in pr_impact_info.function_changes:
                func_name = func_change.get('function_name', 'unknown')
                change_type = func_change.get('change_type', 'modified')
                file_path = func_change.get('file', 'unknown')
                
                # Get callers/callees info
                caller_callee_info = pr_impact_info.callers_callees_info.get(func_name, {})
                callers = caller_callee_info.get('callers', [])
                callees = caller_callee_info.get('callees', [])
                
                # Format according to DoD example: "PR Changes: Method M in Class A was modified. Callers: ..., Callees: ..."
                if self.config.language == "vietnamese":
                    impact_line = f"   • Thay đổi PR: Method {func_name} trong {file_path} đã được {change_type}."
                else:
                    impact_line = f"   • PR Changes: Method {func_name} in {file_path} was {change_type}."
                
                if callers:
                    callers_str = ", ".join(callers[:3])  # Show first 3
                    if len(callers) > 3:
                        callers_str += f" (+{len(callers)-3} more)"
                    impact_line += f" Callers: {callers_str}."
                else:
                    if self.config.language == "vietnamese":
                        impact_line += " Callers: không có."
                    else:
                        impact_line += " Callers: none."
                
                if callees:
                    callees_str = ", ".join(callees[:3])  # Show first 3
                    if len(callees) > 3:
                        callees_str += f" (+{len(callees)-3} more)"
                    impact_line += f" Callees: {callees_str}."
                else:
                    if self.config.language == "vietnamese":
                        impact_line += " Callees: không có."
                    else:
                        impact_line += " Callees: none."
                
                lines.append(impact_line)
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_empty_report(self) -> str:
        """Generate report when no findings are provided."""
        if self.config.language == "vietnamese":
            return """
📋 BÁO CÁO PHÂN TÍCH CODE

🎉 Không có vấn đề nào được phát hiện!

Dự án này có vẻ tuân thủ tốt các best practices đã được kiểm tra.
Tiếp tục duy trì chất lượng code này!

═══════════════════════════════════════════════════════════════
""".strip()
        else:
            return """
📋 CODE ANALYSIS REPORT

🎉 No issues found!

This project appears to follow the checked best practices well.
Keep maintaining this code quality!

═══════════════════════════════════════════════════════════════
""".strip()
    
    def _generate_header(self, findings: List[AnalysisFinding], 
                        pr_impact_info: Optional[PRImpactInfo]) -> str:
        """Generate report header."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if self.config.language == "vietnamese":
            header = f"""
═══════════════════════════════════════════════════════════════
📋 BÁO CÁO PHÂN TÍCH CODE
═══════════════════════════════════════════════════════════════
🕒 Thời gian tạo: {timestamp}
🔍 Tổng số phát hiện: {len(findings)}"""
            
            if pr_impact_info:
                header += f"""
🔄 PR phân tích: {pr_impact_info.pr_id} ({pr_impact_info.base_branch} ← {pr_impact_info.head_branch})"""
                
            return header + "\n"
        else:
            header = f"""
═══════════════════════════════════════════════════════════════
📋 CODE ANALYSIS REPORT
═══════════════════════════════════════════════════════════════
🕒 Generated: {timestamp}
🔍 Total findings: {len(findings)}"""
            
            if pr_impact_info:
                header += f"""
🔄 PR analyzed: {pr_impact_info.pr_id} ({pr_impact_info.base_branch} ← {pr_impact_info.head_branch})"""
                
            return header + "\n"
    
    def _generate_summary_section(self, findings: List[AnalysisFinding], 
                                 pr_impact_info: Optional[PRImpactInfo]) -> str:
        """Generate summary statistics section."""
        severity_counts = {}
        type_counts = {}
        
        for finding in findings:
            # Count by severity
            if finding.severity not in severity_counts:
                severity_counts[finding.severity] = 0
            severity_counts[finding.severity] += 1
            
            # Count by type
            if finding.finding_type not in type_counts:
                type_counts[finding.finding_type] = 0
            type_counts[finding.finding_type] += 1
        
        if self.config.language == "vietnamese":
            section = "\n📊 TÓM TẮT PHÂN TÍCH\n" + "─" * 50 + "\n"
            
            # Severity breakdown
            section += "🚨 Phân bố theo mức độ nghiêm trọng:\n"
            for severity in [AnalysisSeverity.CRITICAL, AnalysisSeverity.HIGH, 
                           AnalysisSeverity.MEDIUM, AnalysisSeverity.LOW, AnalysisSeverity.INFO]:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    severity_name = self._vietnamese_translations[severity]
                    section += f"  • {severity_name}: {count}\n"
            
            # Type breakdown
            section += "\n🔍 Phân bố theo loại vấn đề:\n"
            for finding_type, count in type_counts.items():
                type_name = self._vietnamese_translations[finding_type]
                section += f"  • {type_name}: {count}\n"
                
        else:
            section = "\n📊 ANALYSIS SUMMARY\n" + "─" * 50 + "\n"
            
            # Severity breakdown
            section += "🚨 By severity level:\n"
            for severity in [AnalysisSeverity.CRITICAL, AnalysisSeverity.HIGH, 
                           AnalysisSeverity.MEDIUM, AnalysisSeverity.LOW, AnalysisSeverity.INFO]:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    section += f"  • {severity.value.title()}: {count}\n"
            
            # Type breakdown
            section += "\n🔍 By issue type:\n"
            for finding_type, count in type_counts.items():
                section += f"  • {finding_type.value.replace('_', ' ').title()}: {count}\n"
        
        return section
    
    def _generate_findings_section(self, findings: List[AnalysisFinding]) -> str:
        """
        Generate main findings section (core DoD requirement).
        
        This implements the core requirement:
        "Hàm tạo một chuỗi string dạng text, liệt kê các phát hiện một cách rõ ràng"
        """
        if self.config.language == "vietnamese":
            section = "\n🔍 CHI TIẾT CÁC PHÁT HIỆN\n" + "─" * 50 + "\n"
        else:
            section = "\n🔍 DETAILED FINDINGS\n" + "─" * 50 + "\n"
        
        if self.config.group_by_severity:
            # Group by severity level
            severity_order = [AnalysisSeverity.CRITICAL, AnalysisSeverity.HIGH, 
                            AnalysisSeverity.MEDIUM, AnalysisSeverity.LOW, AnalysisSeverity.INFO]
            
            for severity in severity_order:
                severity_findings = [f for f in findings if f.severity == severity]
                if not severity_findings:
                    continue
                
                if self.config.language == "vietnamese":
                    severity_name = self._vietnamese_translations[severity]
                    section += f"\n🚨 {severity_name.upper()} ({len(severity_findings)} vấn đề)\n"
                else:
                    section += f"\n🚨 {severity.value.upper()} ({len(severity_findings)} issues)\n"
                
                section += "─" * 30 + "\n"
                
                for i, finding in enumerate(severity_findings, 1):
                    section += self._format_finding(finding, i)
                    
        elif self.config.group_by_type:
            # Group by finding type
            type_groups = {}
            for finding in findings:
                if finding.finding_type not in type_groups:
                    type_groups[finding.finding_type] = []
                type_groups[finding.finding_type].append(finding)
            
            for finding_type, type_findings in type_groups.items():
                if self.config.language == "vietnamese":
                    type_name = self._vietnamese_translations[finding_type]
                    section += f"\n📋 {type_name.upper()} ({len(type_findings)} vấn đề)\n"
                else:
                    section += f"\n📋 {finding_type.value.upper()} ({len(type_findings)} issues)\n"
                
                section += "─" * 30 + "\n"
                
                for i, finding in enumerate(type_findings, 1):
                    section += self._format_finding(finding, i)
        else:
            # Simple linear listing
            for i, finding in enumerate(findings, 1):
                section += self._format_finding(finding, i)
        
        return section
    
    def _format_finding(self, finding: AnalysisFinding, index: int) -> str:
        """
        Format một AnalysisFinding thành text rõ ràng (core DoD requirement).
        
        Examples:
        - "Circular Dependency: fileA -> fileB -> fileA"
        - "Unused Public Method: classC.methodX"
        """
        if self.config.language == "vietnamese":
            # Vietnamese formatting
            result = f"\n{index}. "
            
            # Finding type and title
            type_name = self._vietnamese_translations.get(finding.finding_type, finding.finding_type.value)
            result += f"🔸 {type_name}: {finding.title}\n"
            
            # Description
            if finding.description:
                result += f"   📝 Mô tả: {finding.description}\n"
            
            # Location info
            if finding.file_path:
                location = f"📁 File: {finding.file_path}"
                if finding.start_line:
                    location += f" (dòng {finding.start_line}"
                    if finding.end_line and finding.end_line != finding.start_line:
                        location += f"-{finding.end_line}"
                    location += ")"
                result += f"   {location}\n"
            
            # Affected entities
            if finding.affected_entities:
                entities_str = ", ".join(finding.affected_entities)
                result += f"   🎯 Ảnh hưởng: {entities_str}\n"
            
            # Confidence score
            if finding.confidence_score < 1.0:
                confidence_percent = int(finding.confidence_score * 100)
                result += f"   📊 Độ tin cậy: {confidence_percent}%\n"
                
        else:
            # English formatting
            result = f"\n{index}. "
            
            # Finding type and title
            type_name = finding.finding_type.value.replace('_', ' ').title()
            result += f"🔸 {type_name}: {finding.title}\n"
            
            # Description
            if finding.description:
                result += f"   📝 Description: {finding.description}\n"
            
            # Location info
            if finding.file_path:
                location = f"📁 File: {finding.file_path}"
                if finding.start_line:
                    location += f" (line {finding.start_line}"
                    if finding.end_line and finding.end_line != finding.start_line:
                        location += f"-{finding.end_line}"
                    location += ")"
                result += f"   {location}\n"
            
            # Affected entities
            if finding.affected_entities:
                entities_str = ", ".join(finding.affected_entities)
                result += f"   🎯 Affects: {entities_str}\n"
            
            # Confidence score
            if finding.confidence_score < 1.0:
                confidence_percent = int(finding.confidence_score * 100)
                result += f"   📊 Confidence: {confidence_percent}%\n"
        
        return result
    
    def _generate_recommendations_section(self, findings: List[AnalysisFinding]) -> str:
        """Generate recommendations section."""
        all_recommendations = []
        
        for finding in findings:
            if finding.recommendations:
                all_recommendations.extend(finding.recommendations)
        
        if not all_recommendations:
            return ""
        
        # Remove duplicates while preserving order
        unique_recommendations = []
        seen = set()
        for rec in all_recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        if self.config.language == "vietnamese":
            section = "\n💡 KHUYẾN NGHỊ\n" + "─" * 50 + "\n"
            for i, rec in enumerate(unique_recommendations, 1):
                section += f"{i}. {rec}\n"
        else:
            section = "\n💡 RECOMMENDATIONS\n" + "─" * 50 + "\n"
            for i, rec in enumerate(unique_recommendations, 1):
                section += f"{i}. {rec}\n"
        
        return section
    
    def _generate_metadata_section(self, findings: List[AnalysisFinding]) -> str:
        """Generate metadata section."""
        analysis_modules = set()
        discovery_times = []
        
        for finding in findings:
            analysis_modules.add(finding.analysis_module)
            discovery_times.append(finding.discovered_at)
        
        if self.config.language == "vietnamese":
            section = "\n📋 THÔNG TIN BỔ SUNG\n" + "─" * 50 + "\n"
            section += f"🔧 Modules phân tích: {', '.join(analysis_modules)}\n"
            if discovery_times:
                earliest = min(discovery_times).strftime("%Y-%m-%d %H:%M:%S")
                latest = max(discovery_times).strftime("%Y-%m-%d %H:%M:%S")
                section += f"⏰ Thời gian phát hiện: {earliest} - {latest}\n"
        else:
            section = "\n📋 METADATA\n" + "─" * 50 + "\n"
            section += f"🔧 Analysis modules: {', '.join(analysis_modules)}\n"
            if discovery_times:
                earliest = min(discovery_times).strftime("%Y-%m-%d %H:%M:%S")
                latest = max(discovery_times).strftime("%Y-%m-%d %H:%M:%S")
                section += f"⏰ Discovery time: {earliest} - {latest}\n"
        
        return section
    
    def _generate_footer(self) -> str:
        """Generate report footer."""
        if self.config.language == "vietnamese":
            return """
═══════════════════════════════════════════════════════════════
🤖 Báo cáo được tạo bởi RepoChat v1.0
💡 Gợi ý: Xem xét ưu tiên các vấn đề có mức độ nghiêm trọng cao trước
═══════════════════════════════════════════════════════════════
"""
        else:
            return """
═══════════════════════════════════════════════════════════════
🤖 Report generated by RepoChat v1.0
💡 Tip: Consider prioritizing high-severity issues first
═══════════════════════════════════════════════════════════════
"""
    
    def _generate_error_report(self, error_message: str) -> str:
        """Generate error report when generation fails."""
        if self.config.language == "vietnamese":
            return f"""
📋 BÁO CÁO PHÂN TÍCH CODE

❌ LỖI: Không thể tạo báo cáo
Chi tiết lỗi: {error_message}

Vui lòng kiểm tra logs để biết thêm thông tin chi tiết.
"""
        else:
            return f"""
📋 CODE ANALYSIS REPORT

❌ ERROR: Failed to generate report
Error details: {error_message}

Please check logs for more details.
"""
    
    def get_module_stats(self) -> Dict[str, Any]:
        """Get module statistics."""
        return {
            'total_reports_generated': self._stats['total_reports_generated'],
            'total_findings_reported': self._stats['total_findings_reported'],
            'pr_impact_reports_count': self._stats['pr_impact_reports_count'],
            'average_generation_time_ms': (
                self._stats['generation_time_ms'] / max(1, self._stats['total_reports_generated'])
            ),
            'total_generation_time_ms': self._stats['generation_time_ms']
        }
    
    def reset_stats(self) -> None:
        """Reset module statistics."""
        self._stats = {
            'total_reports_generated': 0,
            'total_findings_reported': 0,
            'pr_impact_reports_count': 0,
            'generation_time_ms': 0.0
        }
        self.logger.info("Module statistics reset") 