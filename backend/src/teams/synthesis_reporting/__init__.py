"""
TEAM Synthesis & Reporting

Responsible for aggregating analysis findings and generating reports.
Contains modules for Task 4.4-4.8 implementation.
"""

from teams.synthesis_reporting.finding_aggregator_module import (
    FindingAggregatorModule,
    AggregationStrategy,
    AggregationConfig,
    AggregationResult
)

# Task 4.5 & 4.6: ReportGeneratorModule with PR Impact Integration
from teams.synthesis_reporting.report_generator_module import (
    ReportGeneratorModule,
    ReportGenerationConfig,
    PRImpactInfo
)

# Task 4.7: OutputFormatterModule and FinalReviewReport
from teams.synthesis_reporting.output_formatter_module import (
    OutputFormatterModule,
    OutputFormatterConfig,
    FinalReviewReport
)

__all__ = [
    'FindingAggregatorModule',
    'AggregationStrategy', 
    'AggregationConfig',
    'AggregationResult',
    'ReportGeneratorModule',
    'ReportGenerationConfig',
    'PRImpactInfo',  # New for Task 4.6
    'OutputFormatterModule',  # New for Task 4.7
    'OutputFormatterConfig',  # New for Task 4.7
    'FinalReviewReport'  # New for Task 4.7
]
