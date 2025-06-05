"""
TEAM Code Analysis - Code Quality & Architectural Analysis

Provides modules for analyzing code structure, detecting architectural issues,
and generating insights for code review and refactoring.

Modules:
- ArchitecturalAnalyzerModule: Detect circular dependencies, architectural violations
- models: Common data structures for analysis results

Key Features:
- Circular dependency detection
- Architectural pattern analysis
- Code quality insights
- Integration with Code Knowledge Graph (CKG)
"""

# Export main modules
from .architectural_analyzer_module import ArchitecturalAnalyzerModule
from .models import (
    AnalysisFinding,
    AnalysisFindingType,
    AnalysisSeverity,
    CircularDependency,
    AnalysisResult
)

__all__ = [
    'ArchitecturalAnalyzerModule',
    'AnalysisFinding',
    'AnalysisFindingType', 
    'AnalysisSeverity',
    'CircularDependency',
    'AnalysisResult'
]

__version__ = "1.0.0"
