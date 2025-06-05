"""
Architectural Analyzer Module for TEAM Code Analysis

Implements Task 3.1 (F3.1): Phát hiện circular dependencies và các architectural violations khác.

Features:
- Detect circular dependencies between files, classes, packages
- Analyze architectural patterns and violations  
- Use CKG to perform dependency analysis
- Generate AnalysisFinding objects for detected issues

Enhanced for code review insights and architectural best practices.
"""

import time
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass

from ..ckg_operations.neo4j_connection_module import Neo4jConnectionModule
from ..ckg_operations.ast_to_ckg_builder_module import CKGQueryInterfaceModule
from .models import (
    AnalysisFinding, 
    AnalysisFindingType, 
    AnalysisSeverity,
    CircularDependency,
    AnalysisResult
)

# Mock imports for shared utilities (không có sẵn)
# from shared.utils.logging_config import get_logger, log_function_entry, log_function_exit

def get_logger(name, **kwargs):
    """Mock logger function."""
    return logging.getLogger(name)

def log_function_entry(logger, func_name, **kwargs):
    """Mock function entry logging."""
    logger.debug(f"Entering {func_name} with {kwargs}")

def log_function_exit(logger, func_name, **kwargs):
    """Mock function exit logging."""
    logger.debug(f"Exiting {func_name} with {kwargs}")


class ArchitecturalAnalyzerModule:
    """
    Architectural Analyzer Module for detecting code structure issues.
    
    Focuses on detecting circular dependencies, architectural violations,
    and other structural code quality issues using the Code Knowledge Graph.
    """
    
    def __init__(self, ckg_query_interface: Optional[CKGQueryInterfaceModule] = None,
                 neo4j_connection: Optional[Neo4jConnectionModule] = None):
        """
        Initialize Architectural Analyzer.
        
        Args:
            ckg_query_interface: Optional CKG query interface. If None, creates new one.
            neo4j_connection: Optional Neo4j connection. If None, creates new one.
        """
        self.logger = get_logger(
            "code_analysis.architectural_analyzer",
            extra_context={'component': 'ArchitecturalAnalyzerModule'}
        )
        
        # CKG access setup
        if ckg_query_interface:
            self.ckg_query = ckg_query_interface
        else:
            self.ckg_query = CKGQueryInterfaceModule(neo4j_connection=neo4j_connection)
        
        # Analysis statistics  
        self._stats = {
            'analyses_performed': 0,
            'circular_dependencies_found': 0,
            'total_analysis_time_ms': 0.0
        }
        
        self.logger.info("Architectural Analyzer Module initialized")

    def detect_circular_dependencies(self, project_name: str) -> AnalysisResult:
        """
        Detect circular dependencies in the project.
        
        Args:
            project_name: Name of the project to analyze
            
        Returns:
            AnalysisResult containing detected circular dependencies
        """
        start_time = time.time()
        log_function_entry(self.logger, "detect_circular_dependencies", project_name=project_name)
        
        result = AnalysisResult(
            analysis_type="circular_dependency_detection",
            project_name=project_name,
            findings=[]
        )
        
        try:
            self.logger.info(f"Starting circular dependency analysis for project: {project_name}")
            
            # Detect different types of circular dependencies
            findings = []
            
            # 1. File-level circular dependencies (based on imports/contains relationships)
            file_cycles = self._detect_file_circular_dependencies(project_name)
            findings.extend(self._convert_cycles_to_findings(file_cycles, "file"))
            
            # 2. Class-level circular dependencies (based on extends/implements)
            class_cycles = self._detect_class_circular_dependencies(project_name)
            findings.extend(self._convert_cycles_to_findings(class_cycles, "class"))
            
            # 3. Package-level circular dependencies (if we had package structure)
            # package_cycles = self._detect_package_circular_dependencies(project_name)
            # findings.extend(self._convert_cycles_to_findings(package_cycles, "package"))
            
            result.findings = findings
            result.success = True
            
            self.logger.info(f"Circular dependency analysis completed. Found {len(findings)} issues.")
            
            # Update statistics
            self._stats['analyses_performed'] += 1
            self._stats['circular_dependencies_found'] += len(findings)
            
        except Exception as e:
            error_msg = f"Failed to detect circular dependencies: {str(e)}"
            result.errors.append(error_msg)
            result.success = False
            self.logger.error(error_msg, exc_info=True)
        
        # Record timing
        result.analysis_duration_ms = (time.time() - start_time) * 1000
        self._stats['total_analysis_time_ms'] += result.analysis_duration_ms
        
        log_function_exit(self.logger, "detect_circular_dependencies", 
                         findings_count=len(result.findings), success=result.success)
        return result

    def _detect_file_circular_dependencies(self, project_name: str) -> List[CircularDependency]:
        """
        Detect circular dependencies between files using CONTAINS relationships.
        
        Args:
            project_name: Project to analyze
            
        Returns:
            List of detected circular dependencies
        """
        self.logger.debug("Detecting file-level circular dependencies")
        
        if not self.ckg_query.neo4j.is_connected():
            if not self.ckg_query.neo4j.connect():
                self.logger.error("Cannot connect to Neo4j for circular dependency detection")
                return []
        
        # Query to find cycles in file dependencies
        # We'll look for cycles in CONTAINS relationships (simplified approach)
        cycle_query = """
        MATCH path = (f1:File {project_name: $project_name})-[:CONTAINS*2..10]->(f1)
        WHERE length(path) >= 3
        RETURN [node in nodes(path) | node.name] as cycle_path,
               length(path) as cycle_length
        ORDER BY cycle_length
        LIMIT 20
        """
        
        cycles = []
        
        try:
            with self.ckg_query.neo4j.get_session() as session:
                result = session.run(cycle_query, project_name=project_name)
                
                for record in result:
                    cycle_path = record['cycle_path']
                    cycle_length = record['cycle_length']
                    
                    if len(cycle_path) >= 2:
                        # Remove duplicate at the end (since it's a cycle)
                        if cycle_path[0] == cycle_path[-1]:
                            cycle_path = cycle_path[:-1]
                        
                        severity = self._determine_cycle_severity(cycle_length, "file")
                        
                        cycle = CircularDependency(
                            cycle_path=cycle_path,
                            cycle_type="file",
                            severity=severity,
                            confidence=0.8  # Medium confidence for file cycles
                        )
                        cycles.append(cycle)
                        
                        self.logger.debug(f"Found file cycle: {cycle.get_cycle_description()}")
        
        except Exception as e:
            self.logger.error(f"Error detecting file circular dependencies: {e}")
            
        return cycles

    def _detect_class_circular_dependencies(self, project_name: str) -> List[CircularDependency]:
        """
        Detect circular dependencies between classes using inheritance/implementation.
        
        Args:
            project_name: Project to analyze
            
        Returns:
            List of detected circular dependencies
        """
        self.logger.debug("Detecting class-level circular dependencies")
        
        if not self.ckg_query.neo4j.is_connected():
            if not self.ckg_query.neo4j.connect():
                self.logger.error("Cannot connect to Neo4j for class circular dependency detection")
                return []
        
        # Query to find inheritance cycles
        inheritance_cycle_query = """
        MATCH path = (c1:Class {project_name: $project_name})-[:EXTENDS|IMPLEMENTS*1..10]->(c1)
        WHERE length(path) >= 2
        RETURN [node in nodes(path) | node.name] as cycle_path,
               length(path) as cycle_length,
               [rel in relationships(path) | type(rel)] as relationship_types
        ORDER BY cycle_length
        LIMIT 15
        """
        
        # Query to find method call cycles (more complex dependencies)
        call_cycle_query = """
        MATCH path = (c1:Class {project_name: $project_name})<-[:CONTAINS]-(m1:Method)-[:CALLS*2..8]->
                     (m2:Method)-[:CONTAINS]->(c1)
        WHERE length(path) >= 4
        RETURN [node in nodes(path) | 
               CASE WHEN 'Class' IN labels(node) THEN node.name 
                    WHEN 'Method' IN labels(node) THEN node.name 
                    ELSE node.name END] as cycle_path,
               length(path) as cycle_length
        ORDER BY cycle_length
        LIMIT 10
        """
        
        cycles = []
        
        try:
            with self.ckg_query.neo4j.get_session() as session:
                # Check inheritance cycles
                result = session.run(inheritance_cycle_query, project_name=project_name)
                
                for record in result:
                    cycle_path = record['cycle_path']
                    cycle_length = record['cycle_length']
                    
                    if len(cycle_path) >= 2:
                        # Remove duplicate at the end
                        if cycle_path[0] == cycle_path[-1]:
                            cycle_path = cycle_path[:-1]
                        
                        severity = self._determine_cycle_severity(cycle_length, "class")
                        
                        cycle = CircularDependency(
                            cycle_path=cycle_path,
                            cycle_type="class",
                            severity=severity,
                            confidence=0.9  # High confidence for inheritance cycles
                        )
                        cycles.append(cycle)
                        
                        self.logger.debug(f"Found class inheritance cycle: {cycle.get_cycle_description()}")
                        
                # Check method call cycles (looser coupling)
                result = session.run(call_cycle_query, project_name=project_name)
                
                for record in result:
                    cycle_path = record['cycle_path']
                    cycle_length = record['cycle_length']
                    
                    if len(cycle_path) >= 3:
                        # Extract just class names for method call cycles
                        class_cycle = []
                        for i, entity in enumerate(cycle_path):
                            if i % 2 == 0:  # Classes are at even indices
                                class_cycle.append(entity)
                        
                        if len(class_cycle) >= 2 and len(set(class_cycle)) >= 2:
                            # Remove duplicate at the end if exists (complete cycle)
                            if len(class_cycle) > 1 and class_cycle[0] == class_cycle[-1]:
                                class_cycle = class_cycle[:-1]
                            
                            severity = AnalysisSeverity.LOW  # Method call cycles are less severe
                            
                            cycle = CircularDependency(
                                cycle_path=class_cycle,
                                cycle_type="class",
                                severity=severity,
                                confidence=0.6  # Lower confidence for method call cycles
                            )
                            cycles.append(cycle)
                            
                            self.logger.debug(f"Found class method call cycle: {cycle.get_cycle_description()}")
        
        except Exception as e:
            self.logger.error(f"Error detecting class circular dependencies: {e}")
            
        return cycles

    def _determine_cycle_severity(self, cycle_length: int, cycle_type: str) -> AnalysisSeverity:
        """
        Determine severity based on cycle characteristics.
        
        Args:
            cycle_length: Length of the cycle
            cycle_type: Type of cycle (file, class, package)
            
        Returns:
            Appropriate severity level
        """
        if cycle_type == "class":
            # Class inheritance cycles are more serious
            if cycle_length <= 2:
                return AnalysisSeverity.CRITICAL
            elif cycle_length <= 4:
                return AnalysisSeverity.HIGH
            else:
                return AnalysisSeverity.MEDIUM
        elif cycle_type == "file":
            # File cycles are moderately serious
            if cycle_length <= 3:
                return AnalysisSeverity.HIGH
            elif cycle_length <= 6:
                return AnalysisSeverity.MEDIUM
            else:
                return AnalysisSeverity.LOW
        else:
            # Default severity
            return AnalysisSeverity.MEDIUM

    def _convert_cycles_to_findings(self, cycles: List[CircularDependency], 
                                  cycle_type: str) -> List[AnalysisFinding]:
        """
        Convert CircularDependency objects to AnalysisFinding objects.
        
        Args:
            cycles: List of detected cycles
            cycle_type: Type of cycles
            
        Returns:
            List of AnalysisFinding objects
        """
        findings = []
        
        for cycle in cycles:
            # Generate recommendations based on cycle type
            recommendations = self._generate_cycle_recommendations(cycle)
            
            finding = AnalysisFinding(
                finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
                title=f"{cycle_type.title()} Circular Dependency Detected",
                description=cycle.get_cycle_description(),
                severity=cycle.severity,
                affected_entities=cycle.cycle_path,
                analysis_module="ArchitecturalAnalyzerModule",
                confidence_score=cycle.confidence,
                recommendations=recommendations,
                metadata={
                    'cycle_type': cycle.cycle_type,
                    'cycle_length': len(cycle.cycle_path),
                    'cycle_path': cycle.cycle_path
                }
            )
            
            findings.append(finding)
            
        return findings

    def _generate_cycle_recommendations(self, cycle: CircularDependency) -> List[str]:
        """
        Generate recommendations for resolving circular dependency.
        
        Args:
            cycle: The circular dependency to analyze
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if cycle.cycle_type == "class":
            recommendations.extend([
                "Consider using dependency injection to break the circular dependency",
                "Extract common functionality into a separate base class or interface",
                "Use the Observer pattern or events to decouple the classes",
                "Review the responsibilities of each class and consider refactoring"
            ])
        elif cycle.cycle_type == "file":
            recommendations.extend([
                "Move shared functionality to a common utility module",
                "Reorganize code to create a clear dependency hierarchy",
                "Consider splitting large files into smaller, focused modules",
                "Use dependency inversion to reduce coupling between files"
            ])
        else:
            recommendations.append("Review the architectural design to eliminate circular dependencies")
            
        return recommendations

    def get_analysis_statistics(self) -> Dict[str, Any]:
        """
        Get analysis statistics.
        
        Returns:
            Dictionary containing analysis statistics
        """
        return {
            **self._stats,
            'component': 'ArchitecturalAnalyzerModule'
        }

    def detect_unused_public_elements(self, project_name: str) -> AnalysisResult:
        """
        Detect public methods and classes that are potentially unused within the analyzed codebase.
        
        Note: This analysis has limitations as it only considers static usage within the analyzed
        codebase and cannot detect usage through reflection, dependency injection, or external APIs.
        
        Args:
            project_name: Name of the project to analyze
            
        Returns:
            AnalysisResult containing potentially unused public elements
        """
        start_time = time.time()
        log_function_entry(self.logger, "detect_unused_public_elements", project_name=project_name)
        
        result = AnalysisResult(
            analysis_type="unused_public_elements_detection",
            project_name=project_name,
            findings=[]
        )
        
        try:
            self.logger.info(f"Starting unused public elements analysis for project: {project_name}")
            
            if not self.ckg_query.neo4j.is_connected():
                if not self.ckg_query.neo4j.connect():
                    raise Exception("Cannot connect to Neo4j for unused elements detection")
            
            # Detect unused public methods
            unused_methods = self._detect_unused_public_methods(project_name)
            
            # Detect unused public classes  
            unused_classes = self._detect_unused_public_classes(project_name)
            
            # Convert to findings
            method_findings = self._convert_unused_elements_to_findings(
                unused_methods, "method", project_name
            )
            class_findings = self._convert_unused_elements_to_findings(
                unused_classes, "class", project_name
            )
            
            result.findings.extend(method_findings)
            result.findings.extend(class_findings)
            result.success = True
            
            # Add analysis limitations warning
            if result.findings:
                result.warnings.append(
                    "Static analysis limitations: Cannot detect usage through reflection, "
                    "dependency injection, external APIs, or runtime dynamic calls"
                )
            
            self.logger.info(f"Unused public elements analysis completed. "
                           f"Found {len(method_findings)} unused methods, "
                           f"{len(class_findings)} unused classes.")
            
            # Update statistics
            self._stats['analyses_performed'] += 1
            if 'unused_elements_found' not in self._stats:
                self._stats['unused_elements_found'] = 0
            self._stats['unused_elements_found'] += len(result.findings)
            
        except Exception as e:
            error_msg = f"Failed to detect unused public elements: {str(e)}"
            result.errors.append(error_msg)
            result.success = False
            self.logger.error(error_msg, exc_info=True)
        
        # Record timing
        result.analysis_duration_ms = (time.time() - start_time) * 1000
        self._stats['total_analysis_time_ms'] += result.analysis_duration_ms
        
        log_function_exit(self.logger, "detect_unused_public_elements", 
                         findings_count=len(result.findings), success=result.success)
        return result

    def _detect_unused_public_methods(self, project_name: str) -> List[Dict[str, Any]]:
        """
        Detect public methods that are not called anywhere in the codebase.
        
        Args:
            project_name: Project to analyze
            
        Returns:
            List of unused method information
        """
        self.logger.debug("Detecting unused public methods")
        
        # Query to find public methods that have no incoming CALLS relationships
        unused_methods_query = """
        MATCH (m:Method {project_name: $project_name})
        WHERE m.visibility = 'public' OR m.visibility = 'protected'
        AND NOT exists((m)<-[:CALLS]-())
        AND NOT m.name IN ['main', 'toString', 'equals', 'hashCode', 'clone', 'finalize']
        AND NOT m.name STARTS WITH 'get'
        AND NOT m.name STARTS WITH 'set' 
        AND NOT m.name STARTS WITH 'is'
        OPTIONAL MATCH (m)-[:CONTAINS]->(f:File)
        OPTIONAL MATCH (m)-[:CONTAINS]->(c:Class)
        RETURN 
            m.name as method_name,
            m.qualified_name as qualified_name,
            m.visibility as visibility,
            f.name as file_name,
            f.path as file_path,
            c.name as class_name,
            m.line_number as line_number
        ORDER BY c.name, m.name
        """
        
        unused_methods = []
        
        try:
            with self.ckg_query.neo4j.get_session() as session:
                result = session.run(unused_methods_query, project_name=project_name)
                
                for record in result:
                    method_info = {
                        'name': record['method_name'],
                        'qualified_name': record['qualified_name'],
                        'visibility': record['visibility'],
                        'file_name': record['file_name'],
                        'file_path': record['file_path'],
                        'class_name': record['class_name'],
                        'line_number': record['line_number'],
                        'element_type': 'method'
                    }
                    unused_methods.append(method_info)
                    
                    self.logger.debug(f"Found potentially unused method: {method_info['qualified_name']}")
        
        except Exception as e:
            self.logger.error(f"Error detecting unused public methods: {e}")
            
        return unused_methods

    def _detect_unused_public_classes(self, project_name: str) -> List[Dict[str, Any]]:
        """
        Detect public classes that are not referenced anywhere in the codebase.
        
        Args:
            project_name: Project to analyze
            
        Returns:
            List of unused class information
        """
        self.logger.debug("Detecting unused public classes")
        
        # Query to find public classes that are not extended, implemented, or instantiated
        unused_classes_query = """
        MATCH (c:Class {project_name: $project_name})
        WHERE c.visibility = 'public' OR c.visibility = 'protected'
        AND NOT exists((c)<-[:EXTENDS]-())
        AND NOT exists((c)<-[:IMPLEMENTS]-())
        AND NOT exists((c)<-[:INSTANTIATES]-())
        AND NOT exists((:Method)-[:CALLS]->(:Method)-[:CONTAINS]->(c))
        AND NOT c.name IN ['Main', 'Application', 'App']
        AND NOT c.name ENDS WITH 'Test'
        AND NOT c.name ENDS WITH 'Tests'
        OPTIONAL MATCH (c)-[:CONTAINS]->(f:File)
        RETURN 
            c.name as class_name,
            c.qualified_name as qualified_name,
            c.visibility as visibility,
            f.name as file_name,
            f.path as file_path,
            c.line_number as line_number
        ORDER BY c.name
        """
        
        unused_classes = []
        
        try:
            with self.ckg_query.neo4j.get_session() as session:
                result = session.run(unused_classes_query, project_name=project_name)
                
                for record in result:
                    class_info = {
                        'name': record['class_name'],
                        'qualified_name': record['qualified_name'],
                        'visibility': record['visibility'],
                        'file_name': record['file_name'],
                        'file_path': record['file_path'],
                        'line_number': record['line_number'],
                        'element_type': 'class'
                    }
                    unused_classes.append(class_info)
                    
                    self.logger.debug(f"Found potentially unused class: {class_info['qualified_name']}")
        
        except Exception as e:
            self.logger.error(f"Error detecting unused public classes: {e}")
            
        return unused_classes

    def _convert_unused_elements_to_findings(self, unused_elements: List[Dict[str, Any]], 
                                           element_type: str, project_name: str) -> List[AnalysisFinding]:
        """
        Convert unused element information to AnalysisFinding objects.
        
        Args:
            unused_elements: List of unused element information
            element_type: Type of elements ('method' or 'class')
            project_name: Project name for context
            
        Returns:
            List of AnalysisFinding objects
        """
        findings = []
        
        for element in unused_elements:
            # Determine severity based on visibility and element type
            if element['visibility'] == 'public':
                severity = AnalysisSeverity.MEDIUM if element_type == 'class' else AnalysisSeverity.LOW
            else:  # protected
                severity = AnalysisSeverity.LOW
            
            # Generate description
            description = (f"Public {element_type} '{element['name']}' appears to be unused "
                         f"within the analyzed codebase.")
            if element.get('class_name') and element_type == 'method':
                description += f" (in class '{element['class_name']}')"
            
            # Generate recommendations
            recommendations = self._generate_unused_element_recommendations(element, element_type)
            
            finding = AnalysisFinding(
                finding_type=AnalysisFindingType.UNUSED_PUBLIC_ELEMENT,
                title=f"Potentially Unused Public {element_type.title()}",
                description=description,
                severity=severity,
                file_path=element['file_path'],
                start_line=element['line_number'],
                affected_entities=[element['qualified_name']] if element['qualified_name'] else [element['name']],
                analysis_module="ArchitecturalAnalyzerModule",
                confidence_score=0.7,  # Medium confidence due to static analysis limitations
                recommendations=recommendations,
                metadata={
                    'element_type': element_type,
                    'visibility': element['visibility'],
                    'class_name': element.get('class_name'),
                    'project_name': project_name,
                    'analysis_limitations': [
                        'Cannot detect reflection usage',
                        'Cannot detect dependency injection usage',
                        'Cannot detect external API usage',
                        'Cannot detect runtime dynamic calls'
                    ]
                }
            )
            
            findings.append(finding)
            
        return findings

    def _generate_unused_element_recommendations(self, element: Dict[str, Any], 
                                               element_type: str) -> List[str]:
        """
        Generate recommendations for potentially unused elements.
        
        Args:
            element: Element information
            element_type: Type of element ('method' or 'class')
            
        Returns:
            List of recommendations
        """
        recommendations = [
            f"Verify that this {element_type} is not used through reflection or dependency injection",
            f"Check if this {element_type} is part of a public API or framework interface"
        ]
        
        if element_type == 'method':
            recommendations.extend([
                "Consider if this method is required by an interface or abstract class",
                "Check if this method is called through inheritance or polymorphism",
                "If truly unused, consider making it private or removing it"
            ])
        elif element_type == 'class':
            recommendations.extend([
                "Verify if this class is instantiated through configuration or annotations",
                "Check if this class is used as a type parameter or generic constraint",
                "If truly unused, consider removing it to reduce codebase complexity"
            ])
        
        recommendations.append("Review code coverage reports to confirm usage patterns")
        
        return recommendations

    def detect_unused_elements(self, project_name: str) -> AnalysisResult:
        """
        Alias for detect_unused_public_elements for backward compatibility.
        
        Args:
            project_name: Name of the project to analyze
            
        Returns:
            AnalysisResult containing unused element findings
        """
        return self.detect_unused_public_elements(project_name)

    def analyze_project_architecture(self, project_name: str) -> AnalysisResult:
        """
        Perform comprehensive architectural analysis of a project.
        
        Args:
            project_name: Name of the project to analyze
            
        Returns:
            AnalysisResult containing all architectural findings
        """
        start_time = time.time()
        log_function_entry(self.logger, "analyze_project_architecture", project_name=project_name)
        
        result = AnalysisResult(
            analysis_type="comprehensive_architectural_analysis",
            project_name=project_name,
            findings=[]
        )
        
        try:
            # Run circular dependency detection
            circular_deps_result = self.detect_circular_dependencies(project_name)
            
            if circular_deps_result.success:
                result.findings.extend(circular_deps_result.findings)
                result.warnings.extend(circular_deps_result.warnings)
            else:
                result.errors.extend(circular_deps_result.errors)
            
            # Run unused public elements detection (Task 3.2 - F3.2)
            unused_elements_result = self.detect_unused_public_elements(project_name)
            
            if unused_elements_result.success:
                result.findings.extend(unused_elements_result.findings)
                result.warnings.extend(unused_elements_result.warnings)
            else:
                result.errors.extend(unused_elements_result.errors)
            
            # Future: Add other architectural analyses here
            # - Dependency inversion violations
            # - God class detection  
            # - Dead code analysis
            
            result.success = len(result.errors) == 0
            
        except Exception as e:
            error_msg = f"Comprehensive architectural analysis failed: {str(e)}"
            result.errors.append(error_msg)
            result.success = False
            self.logger.error(error_msg, exc_info=True)
        
        result.analysis_duration_ms = (time.time() - start_time) * 1000
        
        log_function_exit(self.logger, "analyze_project_architecture",
                         findings_count=len(result.findings), success=result.success)
        return result 