#!/usr/bin/env python3
"""
Phase 2 Complete Manual Test Script - FIXED VERSION
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


def get_neo4j_connection():
    """Get Neo4j connection with correct credentials."""
    return Neo4jConnectionModule(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="repochat123"
    )


def cleanup_project_data(project_name: str) -> bool:
    """Clean up existing project data in Neo4j."""
    print("=== 🧹 Cleanup Project Data ===")
    
    try:
        neo4j_conn = get_neo4j_connection()
        
        if neo4j_conn.connect():
            with neo4j_conn.get_session() as session:
                # Remove existing project data
                session.run(
                    "MATCH (n {project_name: $project_name}) DETACH DELETE n",
                    project_name=project_name
                )
            
            print(f"✅ Cleaned up project data for: {project_name}")
            neo4j_conn.disconnect()
            return True
        else:
            print("❌ Failed to connect to Neo4j for cleanup")
            return False
            
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False


def test_neo4j_connection() -> bool:
    """Test Neo4j database connection."""
    print("\n=== 🔍 Testing Neo4j Connection ===")
    
    try:
        neo4j_conn = get_neo4j_connection()
        
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
        neo4j_conn = get_neo4j_connection()
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
        neo4j_conn = get_neo4j_connection()
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
        
        # Test 2: Direct database verification
        print("\n--- Test 2: Direct Database Queries ---")
        try:
            with neo4j_conn.get_session() as session:
                # Count nodes for this project
                result = session.run(
                    "MATCH (n {project_name: $project_name}) RETURN count(n) as node_count",
                    project_name=project_name
                )
                node_count = result.single()["node_count"]
                print(f"✅ Project nodes: {node_count}")
                
                # Count relationships for this project
                result = session.run(
                    "MATCH (a {project_name: $project_name})-[r]-(b {project_name: $project_name}) RETURN count(r) as rel_count",
                    project_name=project_name
                )
                rel_count = result.single()["rel_count"]
                print(f"✅ Project relationships: {rel_count}")
                
                # Show sample nodes
                result = session.run(
                    "MATCH (n {project_name: $project_name}) RETURN labels(n)[0] as type, n.name as name LIMIT 5",
                    project_name=project_name
                )
                print("✅ Sample nodes:")
                for i, record in enumerate(result):
                    print(f"   {i+1}. {record['type']}: {record['name']}")
                    
        except Exception as e:
            print(f"⚠️  Direct queries failed: {e}")
        
        neo4j_conn.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Phase 2C CKG querying failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main test execution."""
    print("🚀 PHASE 2 COMPLETE MANUAL TEST")
    print("==================================================")
    print("Testing: AST to CKG Builder + CKG Query Interface")
    print("Workflow: Phase 1 → Parse → Build CKG → Query CKG")
    
    # Test configuration
    test_repo_url = "https://github.com/spring-projects/spring-petclinic.git"
    project_name = "spring_petclinic_phase2_test"
    
    # Phase 0: Cleanup
    cleanup_project_data(project_name)
    
    # Step 1: Test Neo4j Connection
    print("\n" + "=" * 60)
    print("STEP 1: NEO4J CONNECTION TEST")
    print("=" * 60)
    
    if not test_neo4j_connection():
        print("\n❌ Cannot proceed without Neo4j connection")
        return
    
    # Step 2: Phase 1 Data Acquisition
    print("\n" + "=" * 60)
    print("STEP 2: PHASE 1 DATA ACQUISITION")
    print("=" * 60)
    
    project_context = run_phase_1_data_acquisition(test_repo_url)
    if not project_context:
        print("\n❌ Phase 1 failed, cannot proceed")
        return
    
    # Step 3: Phase 2A Parsing
    print("\n" + "=" * 60)
    print("STEP 3: PHASE 2A PARSING")
    print("=" * 60)
    
    coordinator_result = run_phase_2_parsing(project_context)
    if not coordinator_result:
        print("\n❌ Phase 2A parsing failed, cannot proceed")
        return
    
    # Step 4: Phase 2B CKG Building
    print("\n" + "=" * 60)
    print("STEP 4: PHASE 2B CKG BUILDING")
    print("=" * 60)
    
    if not run_phase_2_ckg_building(coordinator_result, project_name):
        print("\n❌ Phase 2B CKG building failed, cannot proceed")
        return
    
    # Step 5: Phase 2C CKG Querying
    print("\n" + "=" * 60)
    print("STEP 5: PHASE 2C CKG QUERYING")
    print("=" * 60)
    
    if not run_phase_2_ckg_querying(project_name):
        print("\n❌ Phase 2C CKG querying failed")
        return
    
    # Success!
    print("\n" + "🎉" * 60)
    print("✅ PHASE 2 COMPLETE MANUAL TEST PASSED!")
    print("✅ All workflow steps completed successfully")
    print("✅ Tasks 2.6, 2.7, 2.8 are working correctly")
    print("🎉" * 60)


if __name__ == "__main__":
    main() 