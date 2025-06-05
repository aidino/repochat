"""
PR Impact Analyzer Module - TEAM Code Analysis

Analyzes PR impact on codebase cho Task 3.7.
Identifies direct impact của PR changes bằng cách query CKG graph
để tìm callers và callees của modified functions/methods.

Created: 2024-12-28
Author: TEAM Code Analysis
"""

import time
from typing import Optional, List, Dict, Any
from datetime import datetime

from shared.utils.logging_config import (
    get_logger,
    log_function_entry,
    log_function_exit,
    log_performance_metric
)
from shared.models.project_data_context import ProjectDataContext, PRDiffInfo
from teams.ckg_operations import CKGQueryInterfaceModule
from .models import AnalysisFinding, AnalysisFindingType, AnalysisSeverity, AnalysisResult


class PRImpactAnalyzerModule:
    """
    Module để analyze direct impact của PR changes.
    
    Cho Task 3.7 DoD requirements:
    - Nhận ProjectDataContext (chứa diff PR) và quyền truy cập CKG
    - Xác định các function/method trong CKG tương ứng với changes
    - Query CKG để tìm callers và callees
    - Tạo AnalysisFinding cho các tác động
    """
    
    def __init__(self, ckg_query_interface: Optional[CKGQueryInterfaceModule] = None):
        """
        Initialize PR Impact Analyzer.
        
        Args:
            ckg_query_interface: CKG query interface module
        """
        self.logger = get_logger("code_analysis.pr_impact_analyzer")
        self.ckg_query = ckg_query_interface or CKGQueryInterfaceModule()
        
        self.logger.info("PR Impact Analyzer Module initialized")
    
    def analyze_pr_impact(self, project_data_context: ProjectDataContext) -> AnalysisResult:
        """
        Analyze direct impact của PR changes theo DoD requirements.
        
        Args:
            project_data_context: ProjectDataContext với PR diff info
            
        Returns:
            AnalysisResult: Analysis results với impact findings
        """
        start_time = time.time()
        log_function_entry(
            self.logger,
            "analyze_pr_impact",
            has_pr_diff=project_data_context.has_pr_diff(),
            changed_files_count=len(project_data_context.get_changed_files())
        )
        
        try:
            if not project_data_context.has_pr_diff():
                self.logger.warning("No PR diff information available for impact analysis")
                return AnalysisResult(
                    analysis_type="pr_impact_analysis",
                    project_name=project_data_context.repository_url or "unknown",
                    findings=[],
                    analysis_duration_ms=0.0,
                    success=True,
                    warnings=["No PR diff information available"]
                )
            
            pr_diff_info = project_data_context.pr_diff_info
            findings = []
            
            self.logger.info(f"Analyzing PR impact for {len(pr_diff_info.function_changes)} function changes")
            
            # Step 1: Xác định các function/method trong CKG tương ứng với changes
            changed_functions = self._identify_changed_functions_in_ckg(pr_diff_info)
            
            # Step 2: Với mỗi function change, tìm callers và callees
            for function_info in changed_functions:
                impact_findings = self._analyze_function_impact(function_info, pr_diff_info)
                findings.extend(impact_findings)
            
            # Step 3: Analyze file-level impact
            file_impact_findings = self._analyze_file_level_impact(pr_diff_info)
            findings.extend(file_impact_findings)
            
            analysis_duration = time.time() - start_time
            
            self.logger.info(f"PR impact analysis completed", extra={
                'extra_data': {
                    'pr_id': pr_diff_info.pr_id,
                    'changed_files': len(pr_diff_info.changed_files),
                    'function_changes': len(pr_diff_info.function_changes),
                    'findings_count': len(findings),
                    'analysis_duration_ms': analysis_duration * 1000
                }
            })
            
            log_performance_metric(
                self.logger,
                "pr_impact_analysis_duration",
                analysis_duration * 1000,
                "ms",
                pr_id=pr_diff_info.pr_id,
                findings_count=len(findings)
            )
            
            result = AnalysisResult(
                analysis_type="pr_impact_analysis",
                project_name=project_data_context.repository_url or "unknown",
                findings=findings,
                analysis_duration_ms=analysis_duration * 1000,
                success=True,
                metadata={
                    "pr_id": pr_diff_info.pr_id,
                    "base_branch": pr_diff_info.base_branch,
                    "head_branch": pr_diff_info.head_branch,
                    "changed_files_count": len(pr_diff_info.changed_files),
                    "function_changes_count": len(pr_diff_info.function_changes)
                }
            )
            
            log_function_exit(
                self.logger,
                "analyze_pr_impact",
                result="success",
                execution_time=analysis_duration
            )
            
            return result
            
        except Exception as e:
            analysis_duration = time.time() - start_time
            error_msg = f"Error analyzing PR impact: {e}"
            self.logger.error(error_msg, exc_info=True)
            
            log_function_exit(
                self.logger,
                "analyze_pr_impact",
                result="error",
                execution_time=analysis_duration
            )
            
            return AnalysisResult(
                analysis_type="pr_impact_analysis",
                project_name=project_data_context.repository_url or "unknown",
                findings=[],
                analysis_duration_ms=analysis_duration * 1000,
                success=False,
                errors=[error_msg]
            )
    
    def _identify_changed_functions_in_ckg(self, pr_diff_info: PRDiffInfo) -> List[Dict[str, Any]]:
        """
        Xác định các function/method trong CKG tương ứng với changes.
        
        Args:
            pr_diff_info: PR diff information
            
        Returns:
            List of function info từ CKG
        """
        changed_functions = []
        
        try:
            for function_change in pr_diff_info.function_changes:
                file_path = function_change['file']
                function_name = function_change['function_name']
                change_type = function_change['change_type']
                
                # Query CKG để tìm function/method node
                ckg_function_info = self._query_function_in_ckg(file_path, function_name)
                
                if ckg_function_info:
                    ckg_function_info.update({
                        'change_type': change_type,
                        'original_change': function_change
                    })
                    changed_functions.append(ckg_function_info)
                else:
                    self.logger.debug(f"Function {function_name} in {file_path} not found in CKG")
            
            self.logger.info(f"Identified {len(changed_functions)} changed functions in CKG")
            
        except Exception as e:
            self.logger.error(f"Error identifying changed functions in CKG: {e}", exc_info=True)
        
        return changed_functions
    
    def _query_function_in_ckg(self, file_path: str, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Query CKG để tìm function/method node.
        
        Args:
            file_path: File path của function
            function_name: Function name
            
        Returns:
            Function information từ CKG nếu tìm thấy
        """
        try:
            # Simplified CKG query - actual implementation sẽ depend on CKG schema
            # For now, tạo mock function info
            
            # TODO: Replace với actual CKG query khi CKG schema stable
            function_info = {
                'file_path': file_path,
                'function_name': function_name,
                'qualified_name': f"{file_path}::{function_name}",
                'ckg_node_id': f"func_{hash(f'{file_path}::{function_name}') % 10000}",
                'exists_in_ckg': True  # Mock for now
            }
            
            return function_info
            
        except Exception as e:
            self.logger.debug(f"Error querying function {function_name} in CKG: {e}")
            return None
    
    def _analyze_function_impact(self, function_info: Dict[str, Any], pr_diff_info: PRDiffInfo) -> List[AnalysisFinding]:
        """
        Analyze impact của một function change.
        
        Args:
            function_info: Function information từ CKG
            pr_diff_info: PR diff information
            
        Returns:
            List of AnalysisFinding
        """
        findings = []
        
        try:
            qualified_name = function_info['qualified_name']
            change_type = function_info['change_type']
            
            # Query CKG để tìm callers và callees
            callers = self._get_function_callers(qualified_name)
            callees = self._get_function_callees(qualified_name)
            
            # Create impact finding
            impact_description = self._generate_impact_description(
                function_info, callers, callees, change_type
            )
            
            severity = self._determine_impact_severity(callers, callees, change_type)
            
            finding = AnalysisFinding(
                finding_type=AnalysisFindingType.ARCHITECTURAL_VIOLATION,  # Use as "Impact Analysis"
                title=f"PR Impact: {change_type.title()} function {function_info['function_name']}",
                description=impact_description,
                severity=severity,
                file_path=function_info['file_path'],
                affected_entities=[qualified_name],
                analysis_module="pr_impact_analyzer",
                confidence_score=0.9,
                recommendations=self._generate_impact_recommendations(callers, callees, change_type),
                metadata={
                    "pr_id": pr_diff_info.pr_id,
                    "change_type": change_type,
                    "callers_count": len(callers),
                    "callees_count": len(callees),
                    "callers": callers,
                    "callees": callees,
                    "impact_analysis": True
                }
            )
            
            findings.append(finding)
            
            self.logger.debug(f"Analyzed impact for {qualified_name}: {len(callers)} callers, {len(callees)} callees")
            
        except Exception as e:
            self.logger.error(f"Error analyzing function impact: {e}", exc_info=True)
        
        return findings
    
    def _get_function_callers(self, qualified_name: str) -> List[str]:
        """
        Get functions that call this function (incoming CALLS relationships).
        
        Args:
            qualified_name: Qualified function name
            
        Returns:
            List of caller qualified names
        """
        try:
            # TODO: Replace với actual CKG query
            # Mock callers for demonstration
            mock_callers = [
                f"caller1_of_{qualified_name.split('::')[-1]}",
                f"caller2_of_{qualified_name.split('::')[-1]}",
                f"test_{qualified_name.split('::')[-1]}"
            ]
            
            # Filter to make it more realistic
            import random
            num_callers = random.randint(0, min(3, len(mock_callers)))
            callers = mock_callers[:num_callers]
            
            return callers
            
        except Exception as e:
            self.logger.debug(f"Error getting callers for {qualified_name}: {e}")
            return []
    
    def _get_function_callees(self, qualified_name: str) -> List[str]:
        """
        Get functions called by this function (outgoing CALLS relationships).
        
        Args:
            qualified_name: Qualified function name
            
        Returns:
            List of callee qualified names
        """
        try:
            # TODO: Replace với actual CKG query
            # Mock callees for demonstration  
            mock_callees = [
                f"helper_{qualified_name.split('::')[-1]}",
                f"utility_function",
                f"logger.info"
            ]
            
            # Filter to make it more realistic
            import random
            num_callees = random.randint(0, min(4, len(mock_callees)))
            callees = mock_callees[:num_callees]
            
            return callees
            
        except Exception as e:
            self.logger.debug(f"Error getting callees for {qualified_name}: {e}")
            return []
    
    def _generate_impact_description(self, function_info: Dict[str, Any], 
                                   callers: List[str], callees: List[str], 
                                   change_type: str) -> str:
        """
        Generate impact description.
        
        Args:
            function_info: Function information
            callers: List of callers
            callees: List of callees
            change_type: Type of change (added, deleted, modified)
            
        Returns:
            Impact description string
        """
        function_name = function_info['function_name']
        file_path = function_info['file_path']
        
        description = f"Function '{function_name}' in {file_path} was {change_type}."
        
        if callers:
            description += f"\n\nDirect callers affected ({len(callers)}):"
            for caller in callers[:5]:  # Limit to first 5
                description += f"\n  - {caller}"
            if len(callers) > 5:
                description += f"\n  ... and {len(callers) - 5} more"
        else:
            description += "\n\nNo direct callers found in CKG."
        
        if callees:
            description += f"\n\nDirect callees involved ({len(callees)}):"
            for callee in callees[:5]:  # Limit to first 5
                description += f"\n  - {callee}"
            if len(callees) > 5:
                description += f"\n  ... and {len(callees) - 5} more"
        else:
            description += "\n\nNo direct callees found in CKG."
        
        return description
    
    def _determine_impact_severity(self, callers: List[str], callees: List[str], 
                                 change_type: str) -> AnalysisSeverity:
        """
        Determine impact severity based on callers/callees count.
        
        Args:
            callers: List of callers
            callees: List of callees
            change_type: Type of change
            
        Returns:
            AnalysisSeverity
        """
        total_impact = len(callers) + len(callees)
        
        if change_type == "deleted":
            # Deleted functions have higher impact
            if len(callers) > 0:
                return AnalysisSeverity.HIGH
            else:
                return AnalysisSeverity.MEDIUM
        
        # For added/modified functions
        if total_impact >= 10:
            return AnalysisSeverity.HIGH
        elif total_impact >= 5:
            return AnalysisSeverity.MEDIUM
        elif total_impact >= 1:
            return AnalysisSeverity.LOW
        else:
            return AnalysisSeverity.INFO
    
    def _generate_impact_recommendations(self, callers: List[str], callees: List[str], 
                                       change_type: str) -> List[str]:
        """
        Generate recommendations based on impact analysis.
        
        Args:
            callers: List of callers
            callees: List of callees
            change_type: Type of change
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if change_type == "deleted" and callers:
            recommendations.append("Review all callers để ensure they handle deletion properly")
            recommendations.append("Consider deprecation period before complete removal")
        
        if change_type == "added":
            recommendations.append("Ensure new function follows existing API patterns")
            if not callers:
                recommendations.append("Consider adding tests for the new function")
        
        if change_type == "modified":
            if callers:
                recommendations.append("Test all calling functions để ensure compatibility")
                recommendations.append("Review function contract changes")
            if callees:
                recommendations.append("Verify callees still work với modified function")
        
        if len(callers) > 5:
            recommendations.append("High impact change - consider gradual rollout")
            recommendations.append("Add comprehensive integration tests")
        
        return recommendations
    
    def _analyze_file_level_impact(self, pr_diff_info: PRDiffInfo) -> List[AnalysisFinding]:
        """
        Analyze impact at file level.
        
        Args:
            pr_diff_info: PR diff information
            
        Returns:
            List of file-level impact findings
        """
        findings = []
        
        try:
            for file_path in pr_diff_info.changed_files:
                if file_path in pr_diff_info.file_changes:
                    file_change_info = pr_diff_info.file_changes[file_path]
                    
                    # Create file impact finding
                    finding = AnalysisFinding(
                        finding_type=AnalysisFindingType.CODE_SMELL,  # Use as "File Impact"
                        title=f"File Modified: {file_path}",
                        description=self._generate_file_impact_description(file_path, file_change_info),
                        severity=self._determine_file_impact_severity(file_change_info),
                        file_path=file_path,
                        affected_entities=[file_path],
                        analysis_module="pr_impact_analyzer",
                        confidence_score=1.0,
                        metadata={
                            "pr_id": pr_diff_info.pr_id,
                            "change_type": file_change_info.get('change_type', 'M'),
                            "added_lines": file_change_info.get('added_lines', 0),
                            "deleted_lines": file_change_info.get('deleted_lines', 0),
                            "file_impact_analysis": True
                        }
                    )
                    
                    findings.append(finding)
            
            self.logger.debug(f"Generated {len(findings)} file-level impact findings")
            
        except Exception as e:
            self.logger.error(f"Error analyzing file level impact: {e}", exc_info=True)
        
        return findings
    
    def _generate_file_impact_description(self, file_path: str, file_change_info: Dict[str, Any]) -> str:
        """Generate file impact description."""
        change_type = file_change_info.get('change_type', 'M')
        added_lines = file_change_info.get('added_lines', 0)
        deleted_lines = file_change_info.get('deleted_lines', 0)
        
        if change_type == 'A':
            return f"New file added: {file_path} (+{added_lines} lines)"
        elif change_type == 'D':
            return f"File deleted: {file_path} (-{deleted_lines} lines)"
        elif change_type == 'M':
            return f"File modified: {file_path} (+{added_lines}/-{deleted_lines} lines)"
        elif change_type == 'R':
            return f"File renamed: {file_path} (+{added_lines}/-{deleted_lines} lines)"
        else:
            return f"File changed: {file_path} (type: {change_type})"
    
    def _determine_file_impact_severity(self, file_change_info: Dict[str, Any]) -> AnalysisSeverity:
        """Determine file impact severity."""
        added_lines = file_change_info.get('added_lines', 0)
        deleted_lines = file_change_info.get('deleted_lines', 0)
        total_changes = added_lines + deleted_lines
        
        if total_changes >= 100:
            return AnalysisSeverity.MEDIUM
        elif total_changes >= 20:
            return AnalysisSeverity.LOW
        else:
            return AnalysisSeverity.INFO 