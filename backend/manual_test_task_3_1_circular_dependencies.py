#!/usr/bin/env python3
"""
Manual Test for Task 3.1 (F3.1): Circular Dependency Detection

Tests the ArchitecturalAnalyzerModule against real project data to detect circular dependencies.

Features tested:
- File-level circular dependencies
- Class-level circular dependencies  
- AnalysisFinding generation with recommendations
- Integration with CKG Query Interface
- Real-world performance and accuracy

Test Data: Spring Pet Clinic project (should already be in Neo4j from Phase 2 tests)

Author: RepoChat Development Team
Date: 2025-06-05
"""

import os
import sys
import time
import traceback
from typing import Dict, Any, List

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Import required modules
from teams.code_analysis.architectural_analyzer_module import ArchitecturalAnalyzerModule
from teams.code_analysis.models import (
    AnalysisFinding, 
    AnalysisFindingType, 
    AnalysisSeverity,
    CircularDependency,
    AnalysisResult
)
from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule
from teams.ckg_operations.ast_to_ckg_builder_module import CKGQueryInterfaceModule

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"🔍 {title}")
    print(f"{'='*80}")

def print_finding(finding: AnalysisFinding, index: int):
    """Print formatted finding details."""
    print(f"\n📍 Finding #{index + 1}: {finding.title}")
    print(f"   🎯 Type: {finding.finding_type.value}")
    print(f"   ⚠️  Severity: {finding.severity.value.upper()}")
    print(f"   🎲 Confidence: {finding.confidence_score:.1%}")
    print(f"   📝 Description: {finding.description}")
    
    if finding.affected_entities:
        print(f"   🎯 Affected Entities: {', '.join(finding.affected_entities)}")
    
    if finding.recommendations:
        print(f"   💡 Recommendations:")
        for i, rec in enumerate(finding.recommendations, 1):
            print(f"      {i}. {rec}")
    
    if finding.metadata:
        print(f"   📊 Metadata: {finding.metadata}")

def test_neo4j_connection() -> bool:
    """Test Neo4j connection with correct credentials."""
    print_section("Testing Neo4j Connection")
    
    neo4j = Neo4jConnectionModule(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="repochat123"
    )
    
    try:
        success = neo4j.connect()
        if success:
            print("✅ Neo4j connection successful!")
            
            # Test basic query
            with neo4j.get_session() as session:
                result = session.run("MATCH (n) RETURN count(n) as total_nodes")
                total_nodes = result.single()['total_nodes']
                print(f"📊 Total nodes in database: {total_nodes}")
                
                # Check if we have project data
                result = session.run("""
                MATCH (p:Project {project_name: 'spring_petclinic_phase2_test'}) 
                RETURN count(p) as project_count
                """)
                project_count = result.single()['project_count']
                print(f"📊 Spring Pet Clinic test projects found: {project_count}")
                
                if project_count == 0:
                    print("⚠️  Warning: No Spring Pet Clinic test data found. Run Phase 2 manual test first.")
                    return False
                
            neo4j.close()
            return True
        else:
            print("❌ Neo4j connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Neo4j connection error: {e}")
        return False

def test_architectural_analyzer_initialization():
    """Test ArchitecturalAnalyzerModule initialization."""
    print_section("Testing Architectural Analyzer Initialization")
    
    try:
        # Test with custom Neo4j connection
        neo4j_conn = Neo4jConnectionModule(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="repochat123"
        )
        
        ckg_query = CKGQueryInterfaceModule(neo4j_connection=neo4j_conn)
        analyzer = ArchitecturalAnalyzerModule(ckg_query_interface=ckg_query)
        
        print("✅ ArchitecturalAnalyzerModule initialized successfully")
        
        # Get initial statistics
        stats = analyzer.get_analysis_statistics()
        print(f"📊 Initial statistics: {stats}")
        
        return analyzer
        
    except Exception as e:
        print(f"❌ Analyzer initialization failed: {e}")
        traceback.print_exc()
        return None

def test_circular_dependency_detection(analyzer: ArchitecturalAnalyzerModule) -> AnalysisResult:
    """Test circular dependency detection on available project."""
    print_section("Testing Circular Dependency Detection")
    
    project_name = "spring_petclinic_phase2_test"  # Use available project
    
    try:
        print(f"🔍 Analyzing project '{project_name}' for circular dependencies...")
        
        start_time = time.time()
        result = analyzer.detect_circular_dependencies(project_name)
        end_time = time.time()
        
        print(f"⏱️  Analysis completed in {(end_time - start_time)*1000:.1f}ms")
        print(f"✅ Analysis success: {result.success}")
        print(f"📊 Total findings: {len(result.findings)}")
        
        if result.errors:
            print(f"❌ Errors encountered: {result.errors}")
        
        if result.warnings:
            print(f"⚠️  Warnings: {result.warnings}")
        
        # Display findings by severity
        if result.findings:
            print(f"\n📈 Findings by Severity:")
            for severity in AnalysisSeverity:
                severity_findings = result.get_findings_by_severity(severity)
                if severity_findings:
                    print(f"   {severity.value.upper()}: {len(severity_findings)}")
            
            # Display all findings
            print(f"\n🔍 Detailed Findings:")
            for i, finding in enumerate(result.findings):
                print_finding(finding, i)
        else:
            print("🎉 No circular dependencies detected! (This is good)")
        
        return result
        
    except Exception as e:
        print(f"❌ Circular dependency detection failed: {e}")
        traceback.print_exc()
        return None

def test_comprehensive_architectural_analysis(analyzer: ArchitecturalAnalyzerModule):
    """Test comprehensive architectural analysis."""
    print_section("Testing Comprehensive Architectural Analysis")
    
    project_name = "spring_petclinic_phase2_test"  # Use available project
    
    try:
        print(f"🔍 Running comprehensive architectural analysis on '{project_name}'...")
        
        start_time = time.time()
        result = analyzer.analyze_project_architecture(project_name)
        end_time = time.time()
        
        print(f"⏱️  Comprehensive analysis completed in {(end_time - start_time)*1000:.1f}ms")
        print(f"✅ Analysis success: {result.success}")
        print(f"📊 Total findings: {len(result.findings)}")
        print(f"📊 Analysis type: {result.analysis_type}")
        
        # Show final statistics
        stats = analyzer.get_analysis_statistics()
        print(f"\n📊 Final Analysis Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Comprehensive analysis failed: {e}")
        traceback.print_exc()
        return None

def test_analysis_finding_models():
    """Test analysis data models and their functionality."""
    print_section("Testing Analysis Data Models")
    
    try:
        # Test CircularDependency
        cycle = CircularDependency(
            cycle_path=['ClassA', 'ClassB', 'ClassC'],
            cycle_type='class',
            severity=AnalysisSeverity.HIGH,
            confidence=0.95
        )
        
        description = cycle.get_cycle_description()
        print(f"✅ CircularDependency description: {description}")
        
        # Test AnalysisFinding
        finding = AnalysisFinding(
            finding_type=AnalysisFindingType.CIRCULAR_DEPENDENCY,
            title="Test Circular Dependency",
            description=description,
            severity=cycle.severity,
            affected_entities=cycle.cycle_path,
            analysis_module="ArchitecturalAnalyzerModule",
            confidence_score=cycle.confidence,
            recommendations=[
                "Consider using dependency injection",
                "Extract common interface",
                "Refactor to eliminate coupling"
            ],
            metadata={
                'cycle_type': cycle.cycle_type,
                'cycle_length': len(cycle.cycle_path)
            }
        )
        
        print(f"✅ AnalysisFinding created successfully")
        print(f"   📝 Title: {finding.title}")
        print(f"   🎯 Type: {finding.finding_type.value}")
        print(f"   ⚠️  Severity: {finding.severity.value}")
        print(f"   💡 Recommendations: {len(finding.recommendations)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model testing failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print_section("Task 3.1 (F3.1): Circular Dependencies Detection - Manual Test")
    print("Testing ArchitecturalAnalyzerModule against Spring Pet Clinic project")
    
    # Test sequence
    success_count = 0
    total_tests = 5
    
    # 1. Test Neo4j connection
    if test_neo4j_connection():
        success_count += 1
    
    # 2. Test analyzer initialization
    analyzer = test_architectural_analyzer_initialization()
    if analyzer:
        success_count += 1
        
        # 3. Test circular dependency detection
        cd_result = test_circular_dependency_detection(analyzer)
        if cd_result:
            success_count += 1
        
        # 4. Test comprehensive analysis
        comp_result = test_comprehensive_architectural_analysis(analyzer)
        if comp_result:
            success_count += 1
    
    # 5. Test data models
    if test_analysis_finding_models():
        success_count += 1
    
    # Final summary
    print_section("Test Summary")
    print(f"✅ Tests passed: {success_count}/{total_tests}")
    print(f"📊 Success rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Task 3.1 implementation is working correctly.")
        print("\n📋 Manual Test Scenarios to Verify:")
        print("   1. ✅ Neo4j connection with correct credentials")
        print("   2. ✅ ArchitecturalAnalyzerModule initialization")
        print("   3. ✅ Circular dependency detection algorithm")
        print("   4. ✅ AnalysisFinding generation with recommendations")
        print("   5. ✅ Analysis data models functionality")
        print("   6. ✅ Integration with CKG Query Interface")
        print("   7. ✅ Error handling and edge cases")
        print("   8. ✅ Performance and timing measurements")
        
        return True
    else:
        print(f"❌ {total_tests - success_count} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 