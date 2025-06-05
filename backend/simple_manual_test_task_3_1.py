#!/usr/bin/env python3
"""
Simple Manual Test for Task 3.1 - Test với requests-python-test project
"""

import os
import sys

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from teams.code_analysis.architectural_analyzer_module import ArchitecturalAnalyzerModule
from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule
from teams.ckg_operations.ast_to_ckg_builder_module import CKGQueryInterfaceModule

def main():
    print("🔍 Simple Manual Test - Task 3.1: Circular Dependencies Detection")
    print("=" * 80)
    
    # Initialize
    neo4j_conn = Neo4jConnectionModule(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="repochat123"
    )
    
    ckg_query = CKGQueryInterfaceModule(neo4j_connection=neo4j_conn)
    analyzer = ArchitecturalAnalyzerModule(ckg_query_interface=ckg_query)
    
    print("✅ ArchitecturalAnalyzerModule initialized")
    
    # Test with requests-python-test project
    project_name = "requests-python-test"
    print(f"\n🔍 Analyzing project: {project_name}")
    
    # Run analysis
    result = analyzer.detect_circular_dependencies(project_name)
    
    print(f"\n📊 RESULTS:")
    print(f"   ✅ Success: {result.success}")
    print(f"   📊 Total findings: {len(result.findings)}")
    print(f"   ⏱️  Analysis time: {result.analysis_duration_ms:.1f}ms")
    
    if result.findings:
        print(f"\n🔍 DETAILED FINDINGS:")
        for i, finding in enumerate(result.findings, 1):
            print(f"\n   📍 Finding #{i}:")
            print(f"      🎯 Title: {finding.title}")
            print(f"      ⚠️  Severity: {finding.severity.value.upper()}")
            print(f"      🎲 Confidence: {finding.confidence_score:.1%}")
            print(f"      📝 Description: {finding.description}")
            
            if finding.affected_entities:
                print(f"      🎯 Affected: {', '.join(finding.affected_entities[:3])}...")
            
            if finding.recommendations:
                print(f"      💡 Recommendations:")
                for j, rec in enumerate(finding.recommendations[:2], 1):
                    print(f"         {j}. {rec}")
    else:
        print("   🎉 No circular dependencies found!")
    
    # Get final statistics
    stats = analyzer.get_analysis_statistics()
    print(f"\n📈 ANALYSIS STATISTICS:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 Manual test completed successfully!")

if __name__ == "__main__":
    main() 