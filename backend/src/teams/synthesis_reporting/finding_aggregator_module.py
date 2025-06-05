"""
FindingAggregatorModule for TEAM Synthesis & Reporting

Implementation of Task 4.4 (F4.4): Thu thập AnalysisFinding
This module aggregates, processes, and organizes analysis findings from TEAM Code Analysis.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit, log_performance_metric
from teams.code_analysis.models import AnalysisFinding, AnalysisFindingType, AnalysisSeverity


class AggregationStrategy(Enum):
    """Strategies for aggregating findings."""
    PRESERVE_ALL = "preserve_all"
    DEDUPLICATE = "deduplicate"
    MERGE_SIMILAR = "merge_similar"
    SEVERITY_FILTER = "severity_filter"


@dataclass
class AggregationConfig:
    """Configuration for finding aggregation."""
    strategy: AggregationStrategy = AggregationStrategy.PRESERVE_ALL
    min_severity: Optional[AnalysisSeverity] = None
    max_findings: Optional[int] = None
    dedupe_threshold: float = 0.8  # Similarity threshold for deduplication
    group_by_type: bool = True
    sort_by_severity: bool = True
    sort_by_confidence: bool = False


@dataclass  
class AggregationResult:
    """Result of finding aggregation process."""
    aggregated_findings: List[AnalysisFinding]
    original_count: int
    final_count: int
    duplicates_removed: int = 0
    filtered_count: int = 0
    processing_time_ms: float = 0.0
    summary: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.summary is None:
            self.summary = {}


class FindingAggregatorModule:
    """
    Module để thu thập và tổng hợp AnalysisFinding objects.
    
    Task 4.4 DoD Requirements:
    - Module có hàm nhận một danh sách các AnalysisFinding (từ TEAM Code Analysis thông qua Orchestrator)
    - Hàm có thể thực hiện xử lý cơ bản như loại bỏ trùng lặp (nếu có) hoặc sắp xếp
    - Trả về danh sách các phát hiện đã được tổng hợp/xử lý
    
    Features:
    - Basic finding aggregation and deduplication
    - Sorting by severity, confidence, finding type
    - Filtering by severity levels
    - Statistical analysis of findings
    - Configurable aggregation strategies
    """
    
    def __init__(self):
        """Initialize FindingAggregatorModule."""
        self.logger = get_logger("synthesis_reporting.finding_aggregator")
        self._stats = {
            'total_aggregations': 0,
            'total_findings_processed': 0,
            'total_duplicates_removed': 0,
            'aggregation_time_ms': 0.0
        }
        
        self.logger.info("FindingAggregatorModule initialized")
    
    def aggregate_findings(
        self, 
        findings: List[AnalysisFinding], 
        config: Optional[AggregationConfig] = None
    ) -> AggregationResult:
        """
        Aggregate và process a list of AnalysisFinding objects.
        
        Task 4.4 DoD Implementation:
        - Nhận danh sách AnalysisFinding từ TEAM Code Analysis (thông qua Orchestrator)
        - Thực hiện xử lý cơ bản: deduplication, sorting, filtering
        - Trả về danh sách findings đã được tổng hợp/xử lý
        
        Args:
            findings: List of AnalysisFinding objects to aggregate
            config: Optional aggregation configuration
            
        Returns:
            AggregationResult: Result containing processed findings and metadata
        """
        start_time = time.time()
        
        log_function_entry(
            self.logger,
            "aggregate_findings",
            finding_count=len(findings),
            config_strategy=config.strategy.value if config else "default"
        )
        
        if config is None:
            config = AggregationConfig()
        
        original_count = len(findings)
        
        try:
            # Step 1: Input validation
            if not findings:
                self.logger.info("No findings provided for aggregation")
                return AggregationResult(
                    aggregated_findings=[],
                    original_count=0,
                    final_count=0,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            
            self.logger.info(f"Starting aggregation of {original_count} findings", extra={
                'extra_data': {
                    'strategy': config.strategy.value,
                    'min_severity': config.min_severity.value if config.min_severity else None,
                    'max_findings': config.max_findings
                }
            })
            
            # Step 2: Apply filtering by severity if configured
            processed_findings = findings.copy()
            filtered_count = 0
            
            if config.min_severity:
                processed_findings = self._filter_by_severity(processed_findings, config.min_severity)
                filtered_count = original_count - len(processed_findings)
                self.logger.debug(f"Filtered {filtered_count} findings below {config.min_severity.value} severity")
            
            # Step 3: Apply deduplication based on strategy
            duplicates_removed = 0
            if config.strategy in [AggregationStrategy.DEDUPLICATE, AggregationStrategy.MERGE_SIMILAR]:
                deduplicated_findings, duplicates_removed = self._deduplicate_findings(
                    processed_findings, 
                    config.dedupe_threshold
                )
                processed_findings = deduplicated_findings
                self.logger.debug(f"Removed {duplicates_removed} duplicate findings")
            
            # Step 4: Apply sorting
            if config.sort_by_severity or config.sort_by_confidence:
                processed_findings = self._sort_findings(processed_findings, config)
                self.logger.debug("Applied sorting to findings")
            
            # Step 5: Group by type if requested
            if config.group_by_type:
                processed_findings = self._group_by_type(processed_findings)
                self.logger.debug("Grouped findings by type")
            
            # Step 6: Apply max findings limit
            if config.max_findings and len(processed_findings) > config.max_findings:
                processed_findings = processed_findings[:config.max_findings]
                self.logger.debug(f"Limited results to {config.max_findings} findings")
            
            # Step 7: Generate summary statistics
            summary = self._generate_summary(processed_findings, original_count)
            
            processing_time = (time.time() - start_time) * 1000
            final_count = len(processed_findings)
            
            # Update module statistics
            self._stats['total_aggregations'] += 1
            self._stats['total_findings_processed'] += original_count
            self._stats['total_duplicates_removed'] += duplicates_removed
            self._stats['aggregation_time_ms'] += processing_time
            
            result = AggregationResult(
                aggregated_findings=processed_findings,
                original_count=original_count,
                final_count=final_count,
                duplicates_removed=duplicates_removed,
                filtered_count=filtered_count,
                processing_time_ms=processing_time,
                summary=summary
            )
            
            self.logger.info("Finding aggregation completed successfully", extra={
                'extra_data': {
                    'original_count': original_count,
                    'final_count': final_count,
                    'duplicates_removed': duplicates_removed,
                    'filtered_count': filtered_count,
                    'processing_time_ms': processing_time,
                    'summary': summary
                }
            })
            
            log_performance_metric(
                self.logger,
                "finding_aggregation_duration",
                processing_time,
                "ms",
                finding_count=original_count,
                strategy=config.strategy.value
            )
            
            log_function_exit(self.logger, "aggregate_findings", result="success")
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"Error during finding aggregation: {e}"
            self.logger.error(error_msg, exc_info=True, extra={
                'extra_data': {
                    'original_count': original_count,
                    'processing_time_ms': processing_time,
                    'strategy': config.strategy.value if config else 'unknown'
                }
            })
            
            log_function_exit(self.logger, "aggregate_findings", result="error")
            raise
    
    def _filter_by_severity(
        self, 
        findings: List[AnalysisFinding], 
        min_severity: AnalysisSeverity
    ) -> List[AnalysisFinding]:
        """Filter findings by minimum severity level."""
        severity_order = {
            AnalysisSeverity.CRITICAL: 5,
            AnalysisSeverity.HIGH: 4,
            AnalysisSeverity.MEDIUM: 3,
            AnalysisSeverity.LOW: 2,
            AnalysisSeverity.INFO: 1
        }
        
        min_level = severity_order[min_severity]
        return [f for f in findings if severity_order.get(f.severity, 0) >= min_level]
    
    def _deduplicate_findings(
        self, 
        findings: List[AnalysisFinding], 
        threshold: float
    ) -> Tuple[List[AnalysisFinding], int]:
        """Remove duplicate findings based on similarity threshold."""
        if not findings:
            return findings, 0
        
        unique_findings = []
        duplicates_count = 0
        
        for finding in findings:
            is_duplicate = False
            
            for unique_finding in unique_findings:
                if self._calculate_similarity(finding, unique_finding) >= threshold:
                    is_duplicate = True
                    duplicates_count += 1
                    break
            
            if not is_duplicate:
                unique_findings.append(finding)
        
        return unique_findings, duplicates_count
    
    def _calculate_similarity(self, finding1: AnalysisFinding, finding2: AnalysisFinding) -> float:
        """Calculate similarity score between two findings."""
        if finding1.finding_type != finding2.finding_type:
            return 0.0
        
        similarity_score = 0.0
        
        # Same file and similar location
        if finding1.file_path == finding2.file_path:
            similarity_score += 0.3
            
            if (finding1.start_line and finding2.start_line and 
                abs(finding1.start_line - finding2.start_line) <= 5):
                similarity_score += 0.3
        
        # Similar title/description
        if finding1.title == finding2.title:
            similarity_score += 0.2
        
        if finding1.description == finding2.description:
            similarity_score += 0.2
        
        return min(similarity_score, 1.0)
    
    def _sort_findings(
        self, 
        findings: List[AnalysisFinding], 
        config: AggregationConfig
    ) -> List[AnalysisFinding]:
        """Sort findings based on configuration."""
        def sort_key(finding):
            severity_order = {
                AnalysisSeverity.CRITICAL: 5,
                AnalysisSeverity.HIGH: 4,
                AnalysisSeverity.MEDIUM: 3,
                AnalysisSeverity.LOW: 2,
                AnalysisSeverity.INFO: 1
            }
            
            primary = severity_order.get(finding.severity, 0) if config.sort_by_severity else 0
            secondary = finding.confidence_score if config.sort_by_confidence else 0
            
            return (-primary, -secondary)  # Negative for descending order
        
        return sorted(findings, key=sort_key)
    
    def _group_by_type(self, findings: List[AnalysisFinding]) -> List[AnalysisFinding]:
        """Group findings by finding type."""
        type_groups = {}
        
        for finding in findings:
            finding_type = finding.finding_type
            if finding_type not in type_groups:
                type_groups[finding_type] = []
            type_groups[finding_type].append(finding)
        
        # Maintain order: critical types first
        ordered_types = [
            AnalysisFindingType.CIRCULAR_DEPENDENCY,
            AnalysisFindingType.ARCHITECTURAL_VIOLATION,
            AnalysisFindingType.UNUSED_PUBLIC_ELEMENT,
            AnalysisFindingType.CODE_SMELL,
            AnalysisFindingType.POTENTIAL_REFACTORING,
            AnalysisFindingType.TEST_COVERAGE_ISSUE,
            AnalysisFindingType.PERFORMANCE_CONCERN
        ]
        
        grouped_findings = []
        for finding_type in ordered_types:
            if finding_type in type_groups:
                grouped_findings.extend(type_groups[finding_type])
        
        # Add any remaining types not in ordered list
        for finding_type, findings_list in type_groups.items():
            if finding_type not in ordered_types:
                grouped_findings.extend(findings_list)
        
        return grouped_findings
    
    def _generate_summary(self, findings: List[AnalysisFinding], original_count: int) -> Dict[str, Any]:
        """Generate summary statistics for aggregated findings."""
        if not findings:
            return {
                'total_findings': 0,
                'by_severity': {},
                'by_type': {},
                'average_confidence': 0.0
            }
        
        # Count by severity
        severity_counts = {}
        for severity in AnalysisSeverity:
            severity_counts[severity.value] = sum(1 for f in findings if f.severity == severity)
        
        # Count by type
        type_counts = {}
        for finding_type in AnalysisFindingType:
            type_counts[finding_type.value] = sum(1 for f in findings if f.finding_type == finding_type)
        
        # Calculate average confidence
        total_confidence = sum(f.confidence_score for f in findings)
        avg_confidence = total_confidence / len(findings) if findings else 0.0
        
        # Find most common file
        file_counts = {}
        for finding in findings:
            if finding.file_path:
                file_counts[finding.file_path] = file_counts.get(finding.file_path, 0) + 1
        
        most_common_file = max(file_counts.items(), key=lambda x: x[1]) if file_counts else None
        
        return {
            'total_findings': len(findings),
            'original_count': original_count,
            'reduction_percentage': ((original_count - len(findings)) / original_count * 100) if original_count > 0 else 0.0,
            'by_severity': severity_counts,
            'by_type': type_counts,
            'average_confidence': round(avg_confidence, 3),
            'most_common_file': most_common_file[0] if most_common_file else None,
            'most_common_file_count': most_common_file[1] if most_common_file else 0
        }
    
    def get_module_stats(self) -> Dict[str, Any]:
        """Get module statistics."""
        return {
            'module': 'FindingAggregatorModule',
            'stats': self._stats.copy(),
            'average_processing_time': (
                self._stats['aggregation_time_ms'] / self._stats['total_aggregations']
                if self._stats['total_aggregations'] > 0 else 0.0
            )
        }
    
    def reset_stats(self) -> None:
        """Reset module statistics."""
        self._stats = {
            'total_aggregations': 0,
            'total_findings_processed': 0,
            'total_duplicates_removed': 0,
            'aggregation_time_ms': 0.0
        }
        self.logger.info("Module statistics reset") 