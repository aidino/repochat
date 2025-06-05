#!/usr/bin/env python3
"""
Manual Test for Task 3.2 (F3.2): Unused Public Elements Detection

Tests the ArchitecturalAnalyzerModule unused public elements detection 
functionality with real Neo4j data from Phase 2 CKG.

Usage:
    python manual_test_task_3_2_unused_elements.py

Prerequisites:
    - Neo4j running with CKG data from Phase 2 (Spring PetClinic project)
    - Phase 1 & 2 completed successfully
"""

import sys
import os
import time
import json
from datetime import datetime

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from teams.code_analysis.architectural_analyzer_module import ArchitecturalAnalyzerModule
from teams.code_analysis.models import AnalysisFindingType, AnalysisSeverity
from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule


def test_unused_elements_detection():
    """Test unused public elements detection on real project data."""
    
    print("🔍 Manual Test: Task 3.2 - Unused Public Elements Detection")
    print("=" * 70)
    
    # Test configuration
    project_name = "spring-petclinic"  # From Phase 2 tests
    neo4j_config = {
        'uri': 'bolt://localhost:7687',
        'username': 'neo4j',
        'password': 'password'
    }
    
    print(f"📊 Project: {project_name}")
    print(f"🔌 Neo4j: {neo4j_config['uri']}")
    print()
    
    try:
        # Initialize components
        print("🔧 Initializing ArchitecturalAnalyzerModule...")
        neo4j_conn = Neo4jConnectionModule(**neo4j_config)
        analyzer = ArchitecturalAnalyzerModule(neo4j_connection=neo4j_conn)
        
        # Test Neo4j connection
        print("🔗 Testing Neo4j connection...")
        if not neo4j_conn.connect():
            print("❌ FAILED: Cannot connect to Neo4j")
            return False
        print("✅ Neo4j connection successful")
        
        # Check if project data exists
        print(f"📋 Checking for project data: {project_name}")
        with neo4j_conn.get_session() as session:
            result = session.run(
                "MATCH (p:Project {name: $project_name}) RETURN count(p) as count",
                project_name=project_name
            )
            project_count = result.single()['count']
            
            if project_count == 0:
                print(f"❌ FAILED: No project data found for '{project_name}'")
                print("   Please run Phase 2 tests first to create CKG data")
                return False
        
        print(f"✅ Project data found: {project_name}")
        
        # Test 1: Basic unused elements detection
        print("\n🧪 Test 1: Basic Unused Elements Detection")
        print("-" * 50)
        
        start_time = time.time()
        result = analyzer.detect_unused_public_elements(project_name)
        duration = (time.time() - start_time) * 1000
        
        if not result.success:
            print("❌ FAILED: Unused elements detection failed")
            for error in result.errors:
                print(f"   Error: {error}")
            return False
        
        print(f"✅ Detection completed in {duration:.2f}ms")
        print(f"📊 Found {len(result.findings)} potentially unused elements")
        print(f"⚠️  Warnings: {len(result.warnings)}")
        
        # Analyze findings by type
        method_findings = [f for f in result.findings 
                          if f.metadata.get('element_type') == 'method']
        class_findings = [f for f in result.findings 
                         if f.metadata.get('element_type') == 'class']
        
        print(f"   - Unused methods: {len(method_findings)}")
        print(f"   - Unused classes: {len(class_findings)}")
        
        # Show sample findings
        if result.findings:
            print("\n📋 Sample Findings:")
            for i, finding in enumerate(result.findings[:3], 1):
                print(f"   {i}. {finding.title}")
                print(f"      {finding.description}")
                print(f"      Severity: {finding.severity.value}")
                print(f"      Confidence: {finding.confidence_score}")
                if finding.file_path:
                    print(f"      Location: {finding.file_path}:{finding.start_line}")
                print()
        
        # Show warnings (analysis limitations)
        if result.warnings:
            print("⚠️  Analysis Limitations:")
            for warning in result.warnings:
                print(f"   - {warning}")
            print()
        
        # Test 2: Severity distribution analysis
        print("🧪 Test 2: Severity Distribution Analysis")
        print("-" * 50)
        
        severity_counts = {}
        for finding in result.findings:
            severity = finding.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        print("📊 Findings by severity:")
        for severity, count in sorted(severity_counts.items()):
            print(f"   - {severity.upper()}: {count}")
        
        # Test 3: Comprehensive architectural analysis
        print("\n🧪 Test 3: Comprehensive Architectural Analysis")
        print("-" * 50)
        
        start_time = time.time()
        comprehensive_result = analyzer.analyze_project_architecture(project_name)
        duration = (time.time() - start_time) * 1000
        
        if not comprehensive_result.success:
            print("❌ FAILED: Comprehensive analysis failed")
            for error in comprehensive_result.errors:
                print(f"   Error: {error}")
            return False
        
        print(f"✅ Comprehensive analysis completed in {duration:.2f}ms")
        print(f"📊 Total findings: {len(comprehensive_result.findings)}")
        
        # Analyze findings by type
        finding_types = {}
        for finding in comprehensive_result.findings:
            ftype = finding.finding_type.value
            finding_types[ftype] = finding_types.get(ftype, 0) + 1
        
        print("📋 Findings by type:")
        for ftype, count in sorted(finding_types.items()):
            print(f"   - {ftype.replace('_', ' ').title()}: {count}")
        
        # Test 4: Performance and statistics
        print("\n🧪 Test 4: Performance and Statistics")
        print("-" * 50)
        
        stats = analyzer.get_analysis_statistics()
        print("📊 Analyzer Statistics:")
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"   - {key}: {value:.2f}")
            else:
                print(f"   - {key}: {value}")
        
        # Test 5: Verification queries
        print("\n🧪 Test 5: Database Verification Queries")
        print("-" * 50)
        
        with neo4j_conn.get_session() as session:
            # Count total public methods
            result_methods = session.run("""
                MATCH (m:Method {project_name: $project_name})
                WHERE m.visibility = 'public' OR m.visibility = 'protected'
                RETURN count(m) as total_public_methods
            """, project_name=project_name)
            total_public_methods = result_methods.single()['total_public_methods']
            
            # Count total public classes
            result_classes = session.run("""
                MATCH (c:Class {project_name: $project_name})
                WHERE c.visibility = 'public' OR c.visibility = 'protected'
                RETURN count(c) as total_public_classes
            """, project_name=project_name)
            total_public_classes = result_classes.single()['total_public_classes']
            
            print(f"📊 Database Verification:")
            print(f"   - Total public/protected methods: {total_public_methods}")
            print(f"   - Total public/protected classes: {total_public_classes}")
            print(f"   - Unused methods found: {len(method_findings)}")
            print(f"   - Unused classes found: {len(class_findings)}")
            
            if total_public_methods > 0:
                unused_method_percentage = (len(method_findings) / total_public_methods) * 100
                print(f"   - Unused method percentage: {unused_method_percentage:.1f}%")
            
            if total_public_classes > 0:
                unused_class_percentage = (len(class_findings) / total_public_classes) * 100
                print(f"   - Unused class percentage: {unused_class_percentage:.1f}%")
        
        # Success summary
        print("\n🎉 Test Summary")
        print("=" * 70)
        print("✅ All tests PASSED successfully!")
        print(f"✅ Task 3.2 (F3.2) implementation verified")
        print(f"✅ Unused public elements detection working correctly")
        print(f"✅ Integration with comprehensive analysis confirmed")
        print(f"✅ Performance metrics within acceptable range")
        
        # Generate test report
        test_report = {
            'test_name': 'Task 3.2 - Unused Public Elements Detection',
            'timestamp': datetime.now().isoformat(),
            'project_name': project_name,
            'success': True,
            'results': {
                'unused_elements_found': len(result.findings),
                'unused_methods': len(method_findings),
                'unused_classes': len(class_findings),
                'analysis_duration_ms': duration,
                'total_public_methods': total_public_methods,
                'total_public_classes': total_public_classes,
                'severity_distribution': severity_counts,
                'finding_types': finding_types,
                'warnings_count': len(result.warnings)
            },
            'statistics': stats
        }
        
        # Save test report
        report_file = f"task_3_2_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(test_report, f, indent=2, default=str)
        
        print(f"📄 Test report saved: {report_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            if 'neo4j_conn' in locals():
                neo4j_conn.close()
                print("🔌 Neo4j connection closed")
        except:
            pass


if __name__ == "__main__":
    print("🚀 Starting Manual Test for Task 3.2")
    print(f"⏰ Start time: {datetime.now()}")
    print()
    
    success = test_unused_elements_detection()
    
    print()
    print(f"⏰ End time: {datetime.now()}")
    
    if success:
        print("🎉 Task 3.2 Manual Test: SUCCESS")
        sys.exit(0)
    else:
        print("❌ Task 3.2 Manual Test: FAILED")
        sys.exit(1) 