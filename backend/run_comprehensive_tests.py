#!/usr/bin/env python3
"""
Comprehensive Manual Test Suite for Phase 1 & 2
Testing RepoChat với Spring PetClinic Java Project

Usage:
    python run_comprehensive_tests.py

Prerequisites:
    - Docker environment running (docker-compose.test.yml)
    - Neo4j accessible at localhost:7687
    - Internet connection for git clone
"""

import sys
import os
import time
import traceback
import tempfile
import shutil
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from orchestrator.orchestrator_agent import OrchestratorAgent
from shared.models.task_definition import TaskDefinition
from teams.data_acquisition import GitOperationsModule, LanguageIdentifierModule, DataPreparationModule
from teams.ckg_operations import Neo4jConnectionModule, CodeParserCoordinatorModule, ASTtoCKGBuilderModule, CKGQueryInterfaceModule


class TestRunner:
    """Comprehensive test runner for Phase 1 & 2"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        self.test_repo_url = "https://github.com/spring-projects/spring-petclinic.git"
        self.neo4j_config = {
            "uri": "bolt://localhost:7687",
            "user": "neo4j", 
            "password": "repochat123"
        }
        
    def log_test_start(self, test_name):
        """Log test start"""
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 50)
        
    def log_test_result(self, test_name, success, message="", duration=0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results[test_name] = {
            "status": status,
            "message": message,
            "duration": duration
        }
        print(f"{status} - {test_name} ({duration:.2f}s)")
        if message:
            print(f"    {message}")
    
    def test_orchestrator_initialization(self):
        """Test OrchestratorAgent initialization"""
        self.log_test_start("OrchestratorAgent Initialization")
        
        start_time = time.time()
        try:
            orchestrator = OrchestratorAgent()
            
            # Verify initialization
            assert orchestrator._is_initialized == True
            assert orchestrator.agent_id is not None
            assert hasattr(orchestrator, 'git_operations')
            assert hasattr(orchestrator, 'language_identifier')
            assert hasattr(orchestrator, 'data_preparation')
            assert hasattr(orchestrator, 'pat_handler')
            assert hasattr(orchestrator, 'ckg_operations')
            
            # Test stats
            stats = orchestrator.get_agent_stats()
            assert isinstance(stats, dict)
            
            orchestrator.shutdown()
            
            duration = time.time() - start_time
            self.log_test_result(
                "orchestrator_init", 
                True, 
                f"Agent ID: {orchestrator.agent_id[:8]}", 
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("orchestrator_init", False, str(e), duration)
            raise
    
    def test_git_operations(self):
        """Test GitOperationsModule with real repository"""
        self.log_test_start("Git Operations - Spring PetClinic Clone")
        
        start_time = time.time()
        try:
            git_ops = GitOperationsModule()
            
            # Clone repository
            cloned_path = git_ops.clone_repository(self.test_repo_url)
            
            # Verify clone
            assert os.path.exists(cloned_path)
            assert os.path.isdir(cloned_path)
            
            # Count Java files
            java_files = []
            for root, dirs, files in os.walk(cloned_path):
                for file in files:
                    if file.endswith('.java'):
                        java_files.append(os.path.join(root, file))
            
            assert len(java_files) > 20, f"Expected >20 Java files, found {len(java_files)}"
            
            # Check main source directory
            src_main = os.path.join(cloned_path, "src", "main", "java")
            assert os.path.exists(src_main), "Main source directory not found"
            
            duration = time.time() - start_time
            self.log_test_result(
                "git_operations",
                True,
                f"Cloned to {cloned_path}, {len(java_files)} Java files",
                duration
            )
            
            return cloned_path
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("git_operations", False, str(e), duration)
            raise
    
    def test_language_identification(self, cloned_path):
        """Test LanguageIdentifierModule"""
        self.log_test_start("Language Identification")
        
        start_time = time.time()
        try:
            lang_identifier = LanguageIdentifierModule()
            
            # Detect languages
            detected_languages = lang_identifier.identify_languages(cloned_path)
            
            assert len(detected_languages) > 0, "No languages detected"
            assert "java" in detected_languages, "Java not detected"
            
            # Analyze project structure
            analysis = lang_identifier.analyze_project_structure(cloned_path)
            java_count = analysis['language_breakdown'].get('java', 0)
            assert java_count > 20, f"Expected >20 Java files, found {java_count}"
            
            duration = time.time() - start_time
            self.log_test_result(
                "language_identification",
                True,
                f"Languages: {detected_languages}, Java files: {java_count}",
                duration
            )
            
            return detected_languages
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("language_identification", False, str(e), duration)
            raise
    
    def test_data_preparation(self, cloned_path, detected_languages):
        """Test DataPreparationModule"""
        self.log_test_start("Data Preparation")
        
        start_time = time.time()
        try:
            data_prep = DataPreparationModule()
            
            # Create ProjectDataContext
            project_context = data_prep.create_project_context(
                cloned_code_path=cloned_path,
                detected_languages=detected_languages,
                repository_url=self.test_repo_url
            )
            
            # Verify context
            assert project_context.cloned_code_path == cloned_path
            assert project_context.detected_languages == detected_languages
            assert project_context.repository_url == self.test_repo_url
            assert project_context.has_languages == True
            assert project_context.primary_language == "java"
            
            duration = time.time() - start_time
            self.log_test_result(
                "data_preparation", 
                True,
                f"Primary: {project_context.primary_language}, Count: {project_context.language_count}",
                duration
            )
            
            return project_context
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("data_preparation", False, str(e), duration)
            raise
    
    def test_neo4j_connection(self):
        """Test Neo4j connection"""
        self.log_test_start("Neo4j Connection")
        
        start_time = time.time()
        try:
            neo4j_conn = Neo4jConnectionModule(**self.neo4j_config)
            
            # Test connection
            connected = neo4j_conn.connect()
            assert connected, "Failed to connect to Neo4j"
            
            # Test health check
            health = neo4j_conn.health_check()
            assert health, "Neo4j health check failed"
            
            # Test basic query
            session = neo4j_conn.get_session()
            try:
                result = session.run("RETURN 'Hello Neo4j' as message")
                record = result.single()
                assert record["message"] == "Hello Neo4j"
            finally:
                session.close()
            
            neo4j_conn.close()
            
            duration = time.time() - start_time
            self.log_test_result("neo4j_connection", True, "Connected successfully", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("neo4j_connection", False, str(e), duration)
            raise
    
    def test_java_parsing(self, project_context):
        """Test Java parsing with CodeParserCoordinatorModule"""
        self.log_test_start("Java Code Parsing")
        
        start_time = time.time()
        try:
            parser_coordinator = CodeParserCoordinatorModule()
            
            # Execute parsing
            parse_result = parser_coordinator.coordinate_parsing(project_context)
            
            # Verify results
            assert parse_result.total_files_parsed > 0, "No files parsed"
            assert parse_result.total_entities_found > 0, "No entities found"
            assert "java" in parse_result.languages_processed, "Java not processed"
            
            # Count entities by type
            java_results = parse_result.parser_results.get("java", [])
            total_classes = sum(1 for result in java_results 
                              for entity in result.entities 
                              if entity.entity_type.value == "CLASS")
            total_methods = sum(1 for result in java_results 
                               for entity in result.entities 
                               if entity.entity_type.value == "METHOD")
            
            assert total_classes > 10, f"Expected >10 classes, found {total_classes}"
            
            duration = time.time() - start_time
            self.log_test_result(
                "java_parsing",
                True,
                f"Files: {parse_result.total_files_parsed}, Classes: {total_classes}, Methods: {total_methods}",
                duration
            )
            
            return parse_result
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("java_parsing", False, str(e), duration)
            raise
    
    def test_ckg_building(self, parse_result):
        """Test CKG building with ASTtoCKGBuilderModule"""
        self.log_test_start("Code Knowledge Graph Building")
        
        start_time = time.time()
        try:
            # Setup Neo4j connection
            neo4j_conn = Neo4jConnectionModule(**self.neo4j_config)
            connected = neo4j_conn.connect()
            assert connected, "Failed to connect to Neo4j"
            
            # Clear existing data
            session = neo4j_conn.get_session()
            try:
                session.run("MATCH (n) DETACH DELETE n")
            finally:
                session.close()
            
            # Build CKG
            ckg_builder = ASTtoCKGBuilderModule(neo4j_conn)
            project_name = "spring-petclinic-test"
            
            build_result = ckg_builder.build_ckg_from_coordinator_result(
                parse_result, 
                project_name
            )
            
            # Verify results
            assert build_result.success, f"CKG build failed: {build_result.errors}"
            assert build_result.nodes_created > 0, "No nodes created"
            assert build_result.relationships_created > 0, "No relationships created"
            
            # Verify graph structure
            session = neo4j_conn.get_session()
            try:
                # Count total nodes
                result = session.run("MATCH (n) RETURN count(n) as total")
                total_nodes = result.single()["total"]
                assert total_nodes == build_result.nodes_created
                
                # Count total relationships
                result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
                total_rels = result.single()["total"]
                assert total_rels == build_result.relationships_created
                
            finally:
                session.close()
            
            neo4j_conn.close()
            
            duration = time.time() - start_time
            self.log_test_result(
                "ckg_building",
                True,
                f"Nodes: {build_result.nodes_created}, Relationships: {build_result.relationships_created}",
                duration
            )
            
            return build_result
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("ckg_building", False, str(e), duration)
            raise
    
    def test_ckg_queries(self):
        """Test CKG querying with CKGQueryInterfaceModule"""
        self.log_test_start("CKG Query Interface")
        
        start_time = time.time()
        try:
            # Setup connection
            neo4j_conn = Neo4jConnectionModule(**self.neo4j_config)
            connected = neo4j_conn.connect()
            assert connected, "Failed to connect to Neo4j"
            
            query_interface = CKGQueryInterfaceModule(neo4j_conn)
            
            # Test queries
            classes = query_interface.get_all_classes()
            assert len(classes) > 0, "No classes found"
            
            # Test class methods
            if classes:
                test_class = classes[0]['name']
                methods = query_interface.get_class_methods(test_class)
                # Methods can be 0 for some classes
                
                # Test definition location
                location = query_interface.get_class_definition_location(test_class)
                assert location is not None, f"Location not found for {test_class}"
            
            # Test call relationships
            call_relationships = query_interface.get_call_relationships()
            # Relationships can be 0 depending on parsing
            
            # Test Spring-specific queries
            controllers = query_interface.execute_custom_query("""
                MATCH (c:Class) 
                WHERE c.name ENDS WITH "Controller"
                RETURN c.name as name
            """)
            
            neo4j_conn.close()
            
            duration = time.time() - start_time
            self.log_test_result(
                "ckg_queries",
                True,
                f"Classes: {len(classes)}, Controllers: {len(controllers)}",
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("ckg_queries", False, str(e), duration)
            raise
    
    def test_complete_workflow(self):
        """Test complete Phase 1+2 workflow"""
        self.log_test_start("Complete Workflow (Phase 1 + 2)")
        
        start_time = time.time()
        try:
            orchestrator = OrchestratorAgent()
            
            task_definition = TaskDefinition(repository_url=self.test_repo_url)
            
            # Execute complete workflow
            project_context, ckg_result = orchestrator.handle_scan_project_with_ckg_task(
                task_definition
            )
            
            # Verify Phase 1 results
            assert project_context is not None
            assert len(project_context.detected_languages) > 0
            assert "java" in project_context.detected_languages
            
            # Verify Phase 2 results
            assert ckg_result.success, f"CKG failed: {ckg_result.errors}"
            assert ckg_result.files_parsed > 0
            assert ckg_result.nodes_created > 0
            assert ckg_result.relationships_created > 0
            
            orchestrator.shutdown()
            
            duration = time.time() - start_time
            self.log_test_result(
                "complete_workflow",
                True,
                f"Total time: {ckg_result.operation_duration_ms:.0f}ms",
                duration
            )
            
            return project_context, ckg_result
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("complete_workflow", False, str(e), duration)
            raise
    
    def run_all_tests(self):
        """Execute all tests in sequence"""
        print("🚀 Starting Comprehensive Manual Test Suite")
        print("📋 Testing Phase 1 & 2 with Spring PetClinic")
        print("=" * 60)
        
        try:
            # Phase 1 Tests
            print("\n🔵 PHASE 1: DATA ACQUISITION TESTING")
            
            self.test_orchestrator_initialization()
            cloned_path = self.test_git_operations()
            detected_languages = self.test_language_identification(cloned_path)
            project_context = self.test_data_preparation(cloned_path, detected_languages)
            
            # Phase 2 Tests
            print("\n🟢 PHASE 2: CKG OPERATIONS TESTING")
            
            self.test_neo4j_connection()
            parse_result = self.test_java_parsing(project_context)
            build_result = self.test_ckg_building(parse_result)
            self.test_ckg_queries()
            
            # Complete Workflow Test
            print("\n🔄 COMPLETE WORKFLOW TESTING")
            
            self.test_complete_workflow()
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            traceback.print_exc()
        
        finally:
            self.print_final_results()
    
    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 FINAL TEST RESULTS")
        print("=" * 60)
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        passed = 0
        failed = 0
        
        for test_name, result in self.results.items():
            status = result["status"]
            duration = result["duration"]
            message = result["message"]
            
            if status.startswith("✅"):
                passed += 1
            else:
                failed += 1
            
            print(f"{test_name:25} | {status:8} | {duration:6.2f}s | {message}")
        
        print("-" * 60)
        print(f"📈 Summary: {passed} passed, {failed} failed")
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Phase 1 & 2 are fully functional with Spring PetClinic!")
        else:
            print(f"\n⚠️  {failed} tests failed. Check logs for details.")
            return False
            
        return True


def main():
    """Main entry point"""
    print("RepoChat Comprehensive Manual Test Suite")
    print("Testing Phase 1 & 2 Implementation")
    print()
    
    # Check environment
    if not os.path.exists("src"):
        print("❌ Error: Run from backend directory")
        sys.exit(1)
    
    # Run tests
    runner = TestRunner()
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 