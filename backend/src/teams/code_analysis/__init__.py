"""
TEAM Code Analysis - Code Quality & Architectural Analysis

Provides modules for analyzing code structure, detecting architectural issues,
and generating insights for code review and refactoring.

Modules:
- ArchitecturalAnalyzerModule: Detect circular dependencies, architectural violations
- LLMAnalysisSupportModule: Bridge to LLM Services for code analysis tasks
- models: Common data structures for analysis results

Key Features:
- Circular dependency detection
- Architectural pattern analysis  
- LLM-powered code analysis
- Code quality insights
- Integration with Code Knowledge Graph (CKG)
"""

# Export main modules
from .architectural_analyzer_module import ArchitecturalAnalyzerModule
from .llm_analysis_support_module import (
    LLMAnalysisSupportModule, 
    CodeAnalysisContext,
    create_llm_analysis_support,
    create_explain_code_request
)
from .pr_impact_analyzer_module import PRImpactAnalyzerModule  # Task 3.7
from .static_analysis_integrator_module import StaticAnalysisIntegratorModule  # Task 3.8
from .models import (
    AnalysisFinding,
    AnalysisFindingType,
    AnalysisSeverity,
    CircularDependency,
    AnalysisResult
)

__all__ = [
    'ArchitecturalAnalyzerModule',
    'LLMAnalysisSupportModule',
    'PRImpactAnalyzerModule',  # Task 3.7
    'StaticAnalysisIntegratorModule',  # Task 3.8
    'CodeAnalysisContext', 
    'create_llm_analysis_support',
    'create_explain_code_request',
    'AnalysisFinding',
    'AnalysisFindingType', 
    'AnalysisSeverity',
    'CircularDependency',
    'AnalysisResult'
]

__version__ = "1.0.0"
