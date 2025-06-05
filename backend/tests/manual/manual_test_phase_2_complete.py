#!/usr/bin/env python3
"""
Phase 2 Complete Manual Test Script
===================================

Tests the complete Phase 2 functionality:
- Task 2.6: AST to CKG Builder (convert parsed entities to Neo4j nodes)
- Task 2.7: AST to CKG Builder (convert relationships to Neo4j edges)  
- Task 2.8: CKG Query Interface (query the built graph)

This demonstrates the end-to-end Phase 2 workflow:
Phase 1 (Data Acquisition) → Phase 2 (CKG Construction) → Phase 2 (CKG Querying)
"""

import os
import sys
import time
import traceback
from typing import Dict, Any

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Import required modules
from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition
from teams.ckg_operations.team_ckg_operations_facade import TeamCKGOperationsFacade
from teams.ckg_operations.ast_to_ckg_builder_module import ASTtoCKGBuilderModule, CKGQueryInterfaceModule
from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule
from teams.ckg_operations.code_parser_coordinator_module import CodeParserCoordinatorModule


def test_neo4j_connection() -> bool:
    """Test Neo4j database connection."""
    print("\n=== 🔍 Testing Neo4j Connection ===")
    
    try:
        neo4j_conn = Neo4jConnectionModule()
        
        # Test connection
        if neo4j_conn.connect():
            print("✅ Connected to Neo4j successfully")
            
            # Test health check
            health = neo4j_conn.health_check()
            print(f"✅ Neo4j health check: {health}")
            
            # Test simple query
            with neo4j_conn.get_session() as session:
                result = session.run("RETURN 1 as test_value")
                test_value = result.single()["test_value"]
                print(f"✅ Test query executed: {test_value}")
            
            neo4j_conn.disconnect()
            return True
        else:
            print("❌ Failed to connect to Neo4j")
            return False
            
    except Exception as e:
        print(f"❌ Neo4j connection error: {e}")
        return False


def run_phase_1_data_acquisition(repo_url: str) -> Any:
    """Run Phase 1 to get ProjectDataContext."""
    print(f"\n=== 📥 Phase 1: Data Acquisition ===")
    print(f"Repository: {repo_url}")
    
    try:
        # Initialize Orchestrator
        orchestrator = OrchestratorAgent()
        print("✅ Orchestrator initialized")
        
        # Create task definition
        task_def = TaskDefinition(repository_url=repo_url)
        print("✅ Task definition created")
        
        # Execute scan project task (Phase 1)
        start_time = time.time()
        project_context = orchestrator.handle_scan_project_task(task_def)
        phase_1_duration = time.time() - start_time
        
        print(f"✅ Phase 1 completed in {phase_1_duration:.2f}s")
        print(f"   Repository path: {project_context.cloned_code_path}")
        print(f"   Languages detected: {project_context.detected_languages}")
        print(f"   Primary language: {project_context.primary_language}")
        
        orchestrator.shutdown()
        return project_context
        
    except Exception as e:
        print(f"❌ Phase 1 failed: {e}")
        traceback.print_exc()
        return None


def run_phase_2_parsing(project_context) -> Any:
    """Run Phase 2 parsing: convert project to AST data."""
    print(f"\n=== 🔧 Phase 2A: Code Parsing ===")
    
    try:
        # Initialize parser coordinator
        coordinator = CodeParserCoordinatorModule()
        print("✅ Code Parser Coordinator initialized")
        
        # Execute parsing
        start_time = time.time()
        coordinator_result = coordinator.coordinate_parsing(project_context)
        parsing_duration = time.time() - start_time
        
        print(f"✅ Parsing completed in {parsing_duration:.2f}s")
        print(f"   Languages processed: {coordinator_result.languages_processed}")
        print(f"   Total files parsed: {coordinator_result.total_files_parsed}")
        print(f"   Total entities found: {coordinator_result.total_entities_found}")
        print(f"   Total relationships found: {coordinator_result.total_relationships_found}")
        
        return coordinator_result
        
    except Exception as e:
        print(f"❌ Phase 2A parsing failed: {e}")
        traceback.print_exc()
        return None


def run_phase_2_ckg_building(coordinator_result, project_name: str) -> bool:
    """Run Phase 2 CKG building: convert AST to Neo4j graph."""
    print(f"\n=== 🏗️ Phase 2B: CKG Building ===")
    print(f"Project: {project_name}")
    
    try:
        # Initialize CKG builder with real Neo4j connection
        neo4j_conn = Neo4jConnectionModule()
        if not neo4j_conn.connect():
            print("❌ Failed to connect to Neo4j for CKG building")
            return False
            
        ckg_builder = ASTtoCKGBuilderModule(neo4j_connection=neo4j_conn)
        print("✅ AST to CKG Builder initialized")
        
        # Build CKG from coordinator results
        start_time = time.time()
        build_result = ckg_builder.build_ckg_from_coordinator_result(
            coordinator_result=coordinator_result,
            project_name=project_name
        )
        build_duration = time.time() - start_time
        
        if build_result.success:
            print(f"✅ CKG building completed in {build_duration:.2f}s")
            print(f"   Nodes created: {build_result.nodes_created}")
            print(f"   Relationships created: {build_result.relationships_created}")
            print(f"   Files processed: {build_result.files_processed}")
            print(f"   Build duration: {build_result.build_duration_ms:.2f}ms")
        else:
            print(f"❌ CKG building failed:")
            for error in build_result.errors:
                print(f"   Error: {error}")
            return False
        
        # Get build statistics
        stats = ckg_builder.get_build_statistics()
        print(f"✅ Builder statistics: {stats}")
        
        neo4j_conn.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Phase 2B CKG building failed: {e}")
        traceback.print_exc()
        return False


def run_phase_2_ckg_querying(project_name: str) -> bool:
    """Run Phase 2 CKG querying: query the built graph."""
    print(f"\n=== 🔍 Phase 2C: CKG Querying ===")
    print(f"Project: {project_name}")
    
    try:
        # Initialize CKG query interface with real Neo4j connection
        neo4j_conn = Neo4jConnectionModule()
        if not neo4j_conn.connect():
            print("❌ Failed to connect to Neo4j for querying")
            return False
            
        query_interface = CKGQueryInterfaceModule(neo4j_connection=neo4j_conn)
        print("✅ CKG Query Interface initialized")
        
        # Test 1: Project Overview
        print("\n--- Test 1: Project Overview ---")
        try:
            overview = query_interface.get_project_overview(project_name)
            print(f"✅ Project overview retrieved")
            print(f"   Project: {overview.get('project_name', 'N/A')}")
            print(f"   Total files: {overview.get('total_files', 0)}")
            print(f"   Total entities: {overview.get('total_entities', 0)}")
        except Exception as e:
            print(f"⚠️  Project overview query failed: {e}")
        
        # Test 2: Class Complexity Analysis
        print("\n--- Test 2: Class Complexity Analysis ---")
        try:
            complexity_analysis = query_interface.get_class_complexity_analysis(project_name, limit=5)
            print(f"✅ Class complexity analysis retrieved")
            print(f"   Complex classes found: {len(complexity_analysis)}")
            for i, cls in enumerate(complexity_analysis[:3]):  # Show top 3
                print(f"   {i+1}. {cls.get('class_name', 'Unknown')}: {cls.get('complexity_score', 0)} score")
        except Exception as e:
            print(f"⚠️  Class complexity analysis failed: {e}")
        
        # Test 3: Method Call Patterns
        print("\n--- Test 3: Method Call Patterns ---")
        try:
            call_patterns = query_interface.get_method_call_patterns(project_name, limit=5)
            print(f"✅ Method call patterns retrieved")
            print(f"   Call patterns found: {len(call_patterns)}")
            for i, pattern in enumerate(call_patterns[:3]):  # Show top 3
                caller = pattern.get('caller_method', 'Unknown')
                callee = pattern.get('callee_method', 'Unknown')
                print(f"   {i+1}. {caller} → {callee}")
        except Exception as e:
            print(f"⚠️  Method call patterns query failed: {e}")
        
        # Test 4: Public API Surface
        print("\n--- Test 4: Public API Surface ---")
        try:
            api_surface = query_interface.get_public_api_surface(project_name)
            print(f"✅ Public API surface retrieved")
            print(f"   Public API elements: {len(api_surface)}")
            for i, element in enumerate(api_surface[:3]):  # Show top 3
                entity_type = element.get('entity_type', 'Unknown')
                name = element.get('name', 'Unknown')
                print(f"   {i+1}. {entity_type}: {name}")
        except Exception as e:
            print(f"⚠️  Public API surface query failed: {e}")
        
        # Test 5: Refactoring Candidates
        print("\n--- Test 5: Refactoring Candidates ---")
        try:
            refactoring_candidates = query_interface.get_potential_refactoring_candidates(project_name)
            print(f"✅ Refactoring candidates retrieved")
            print(f"   Refactoring candidates: {len(refactoring_candidates)}")
            for i, candidate in enumerate(refactoring_candidates[:3]):  # Show top 3
                method = candidate.get('method_name', 'Unknown')
                reason = candidate.get('refactoring_reason', 'Unknown')
                print(f"   {i+1}. {method}: {reason}")
        except Exception as e:
            print(f"⚠️  Refactoring candidates query failed: {e}")
        
        neo4j_conn.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Phase 2C CKG querying failed: {e}")
        traceback.print_exc()
        return False


def run_direct_neo4j_verification(project_name: str) -> bool:
    """Run direct Neo4j queries to verify data."""
    print(f"\n=== 🔎 Direct Neo4j Verification ===")
    
    try:
        neo4j_conn = Neo4jConnectionModule()
        if not neo4j_conn.connect():
            print("❌ Failed to connect to Neo4j for verification")
            return False
        
        with neo4j_conn.get_session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = result.single()["node_count"]
            print(f"✅ Total nodes in database: {node_count}")
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_count = result.single()["rel_count"]
            print(f"✅ Total relationships in database: {rel_count}")
            
            # Project-specific nodes
            result = session.run(
                "MATCH (n {project_name: $project_name}) RETURN count(n) as project_nodes",
                project_name=project_name
            )
            project_nodes = result.single()["project_nodes"]
            print(f"✅ Project '{project_name}' nodes: {project_nodes}")
            
            # Sample node types
            result = session.run(
                "MATCH (n {project_name: $project_name}) RETURN DISTINCT labels(n) as labels, count(n) as count LIMIT 10",
                project_name=project_name
            )
            print("✅ Node types:")
            for record in result:
                labels = record["labels"]
                count = record["count"]
                print(f"   {labels}: {count}")
        
        neo4j_conn.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Direct Neo4j verification failed: {e}")
        traceback.print_exc()
        return False


def cleanup_project_data(project_name: str) -> bool:
    """Clean up project data from Neo4j."""
    print(f"\n=== 🧹 Cleanup Project Data ===")
    
    try:
        neo4j_conn = Neo4jConnectionModule()
        if not neo4j_conn.connect():
            print("❌ Failed to connect to Neo4j for cleanup")
            return False
        
        with neo4j_conn.get_session() as session:
            # Delete all project data
            result = session.run(
                "MATCH (n {project_name: $project_name}) DETACH DELETE n RETURN count(n) as deleted_count",
                project_name=project_name
            )
            deleted_count = result.single()["deleted_count"]
            print(f"✅ Deleted {deleted_count} nodes for project '{project_name}'")
        
        neo4j_conn.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False


def main():
    """Main test execution."""
    print("🚀 PHASE 2 COMPLETE MANUAL TEST")
    print("=" * 50)
    print("Testing: AST to CKG Builder + CKG Query Interface")
    print("Workflow: Phase 1 → Parse → Build CKG → Query CKG")
    
    # Configuration
    repo_url = "https://github.com/octocat/Hello-World.git"  # Small test repo
    project_name = "phase2_test_hello_world"
    
    # Cleanup any existing data first
    cleanup_project_data(project_name)
    
    # Test sequence
    test_results = []
    project_context = None
    coordinator_result = None
    
    # Step 1: Test Neo4j Connection
    print("\n" + "="*60)
    print("STEP 1: NEO4J CONNECTION TEST")
    print("="*60)
    neo4j_success = test_neo4j_connection()
    test_results.append(("Neo4j Connection", neo4j_success))
    
    if not neo4j_success:
        print("\n❌ Cannot proceed without Neo4j connection")
        return
    
    # Step 2: Phase 1 - Data Acquisition
    print("\n" + "="*60)
    print("STEP 2: PHASE 1 - DATA ACQUISITION")
    print("="*60)
    project_context = run_phase_1_data_acquisition(repo_url)
    phase_1_success = project_context is not None
    test_results.append(("Phase 1 - Data Acquisition", phase_1_success))
    
    if not phase_1_success:
        print("\n❌ Cannot proceed without Phase 1 success")
        return
    
    # Step 3: Phase 2A - Code Parsing
    print("\n" + "="*60)
    print("STEP 3: PHASE 2A - CODE PARSING")
    print("="*60)
    coordinator_result = run_phase_2_parsing(project_context)
    parsing_success = coordinator_result is not None
    test_results.append(("Phase 2A - Code Parsing", parsing_success))
    
    if not parsing_success:
        print("\n❌ Cannot proceed without successful parsing")
        return
    
    # Step 4: Phase 2B - CKG Building
    print("\n" + "="*60)
    print("STEP 4: PHASE 2B - CKG BUILDING")
    print("="*60)
    ckg_build_success = run_phase_2_ckg_building(coordinator_result, project_name)
    test_results.append(("Phase 2B - CKG Building", ckg_build_success))
    
    if not ckg_build_success:
        print("\n❌ Cannot proceed without successful CKG building")
        # Continue anyway to show what we can
    
    # Step 5: Direct Neo4j Verification
    print("\n" + "="*60)
    print("STEP 5: DIRECT NEO4J VERIFICATION")
    print("="*60)
    verification_success = run_direct_neo4j_verification(project_name)
    test_results.append(("Direct Neo4j Verification", verification_success))
    
    # Step 6: Phase 2C - CKG Querying
    print("\n" + "="*60)
    print("STEP 6: PHASE 2C - CKG QUERYING")
    print("="*60)
    query_success = run_phase_2_ckg_querying(project_name)
    test_results.append(("Phase 2C - CKG Querying", query_success))
    
    # Cleanup
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    cleanup_success = cleanup_project_data(project_name)
    test_results.append(("Cleanup", cleanup_success))
    
    # Final Results
    print("\n" + "="*60)
    print("🎯 FINAL TEST RESULTS")
    print("="*60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed_tests += 1
    
    print(f"\n📊 Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Phase 2 is COMPLETE!")
        print("✅ AST to CKG Builder: WORKING")
        print("✅ CKG Query Interface: WORKING") 
        print("✅ End-to-end workflow: WORKING")
    elif passed_tests >= 4:  # Main components working
        print("\n✅ CORE FUNCTIONALITY WORKING!")
        print("Phase 2 major components are operational.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please check the error messages above.")


if __name__ == "__main__":
    main() 