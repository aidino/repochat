"""
Data Models for TEAM Code Analysis

Contains common data structures used across code analysis modules.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AnalysisFindingType(Enum):
    """Types of analysis findings."""
    CIRCULAR_DEPENDENCY = "circular_dependency"
    UNUSED_PUBLIC_ELEMENT = "unused_public_element" 
    ARCHITECTURAL_VIOLATION = "architectural_violation"
    CODE_SMELL = "code_smell"
    POTENTIAL_REFACTORING = "potential_refactoring"
    TEST_COVERAGE_ISSUE = "test_coverage_issue"
    PERFORMANCE_CONCERN = "performance_concern"


class AnalysisSeverity(Enum):
    """Severity levels for analysis findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class AnalysisFinding:
    """
    Represents a single finding from code analysis.
    
    This is the standardized format for all analysis results
    across different analysis modules.
    """
    
    # Core identification
    finding_type: AnalysisFindingType
    title: str
    description: str
    severity: AnalysisSeverity
    
    # Location information
    file_path: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    affected_entities: Optional[List[str]] = None  # qualified names of classes/methods
    
    # Analysis details
    analysis_module: str = "unknown"
    confidence_score: float = 1.0  # 0.0 to 1.0
    
    # Additional context
    recommendations: Optional[List[str]] = None
    related_findings: Optional[List[str]] = None  # IDs of related findings
    metadata: Optional[Dict[str, Any]] = None
    
    # Timestamps
    discovered_at: datetime = None
    
    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.now()
        if self.recommendations is None:
            self.recommendations = []
        if self.related_findings is None:
            self.related_findings = []
        if self.metadata is None:
            self.metadata = {}
        if self.affected_entities is None:
            self.affected_entities = []


@dataclass
class CircularDependency:
    """
    Represents a circular dependency detected in the codebase.
    """
    cycle_path: List[str]  # List of entities forming the cycle
    cycle_type: str  # "file", "class", "package"
    severity: AnalysisSeverity
    confidence: float = 1.0
    
    def get_cycle_description(self) -> str:
        """Get human-readable description of the cycle."""
        if len(self.cycle_path) <= 1:
            return "Invalid cycle"
        
        cycle_str = " → ".join(self.cycle_path)
        cycle_str += f" → {self.cycle_path[0]}"  # Complete the circle
        return f"{self.cycle_type.title()} circular dependency: {cycle_str}"


@dataclass
class AnalysisResult:
    """
    Container for analysis results from a single analysis run.
    """
    analysis_type: str
    project_name: str
    findings: List[AnalysisFinding]
    analysis_duration_ms: float = 0.0
    success: bool = True
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}
    
    def get_findings_by_severity(self, severity: AnalysisSeverity) -> List[AnalysisFinding]:
        """Get findings filtered by severity level."""
        return [f for f in self.findings if f.severity == severity]
    
    def get_findings_by_type(self, finding_type: AnalysisFindingType) -> List[AnalysisFinding]:
        """Get findings filtered by finding type."""
        return [f for f in self.findings if f.finding_type == finding_type] 