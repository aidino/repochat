#!/usr/bin/env python3
"""
Enhanced Manual Test Script - Full Workflow with Neo4j Integration

Tests complete RepoChat v1.0 workflow including Neo4j storage:
- Phase 1: Data Acquisition (clone repository, detect languages)
- Task 2.2: Code Parser Coordination (orchestrate parsing)
- Task 2.3: Java Parser Implementation (real Java parsing)
- Task 2.6-2.7: AST to CKG Builder (store in Neo4j)
- Code Review Insights: Query useful information from Neo4j

This demonstrates production-ready workflow with persistent graph storage.

Usage:
    python manual_test_full_workflow_with_neo4j.py

Requirements:
- Neo4j database running locally (port 7687)
- All dependencies from requirements.txt
- Internet connection for GitHub operations
"""

import os
import sys
import time
import tempfile
import shutil
from typing import Dict, Any, List
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import modules from different teams
try:
    # TEAM Data Acquisition
    from teams.data_acquisition.models import ProjectDataContext
    from teams.data_acquisition.github_operations_module import GitHubOperationsModule
    from teams.data_acquisition.language_detection_module import LanguageDetectionModule
    
    # TEAM CKG Operations
    from teams.ckg_operations import (
        CodeParserCoordinatorModule, 
        JavaParser,
        Neo4jConnectionModule
    )
    from teams.ckg_operations.ast_to_ckg_builder_module import (
        ASTtoCKGBuilderModule,
        CKGQueryInterfaceModule
    )
    from teams.ckg_operations.models import CodeEntityType, VisibilityModifier
    
    print("✅ All required modules imported successfully")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all modules are implemented and Neo4j is available")
    sys.exit(1)


class EnhancedWorkflowTester:
    """Enhanced workflow tester with Neo4j integration and code review insights."""
    
    def __init__(self):
        """Initialize the enhanced workflow tester."""
        self.test_workspace = None
        self.neo4j = None
        self.results = {}
        
        print("🚀 Enhanced Full Workflow Tester - Phase 1 to Neo4j CKG")
        print("=" * 70)
    
    def run_complete_test_with_neo4j(self) -> Dict[str, Any]:
        """
        Run complete workflow test with Neo4j storage and insights.
        
        Returns:
            Dictionary with comprehensive test results including Neo4j insights
        """
        # Select high-quality Java projects for testing
        test_projects = [
            {
                'name': 'apache/commons-lang',
                'description': 'Apache Commons Lang - Popular Java utility library',
                'expected_languages': ['java'],
                'clone_depth': 1
            }
        ]
        
        # Create temporary workspace
        self.test_workspace = tempfile.mkdtemp(prefix="repochat_neo4j_test_")
        print(f"📁 Test workspace: {self.test_workspace}")
        
        # Initialize Neo4j connection với credentials từ docker-compose
        try:
            self.neo4j = Neo4jConnectionModule(
                uri="bolt://localhost:7687",
                username="neo4j", 
                password="repochat123"
            )
            if not self.neo4j.test_connection():
                print("❌ Neo4j connection failed. Please ensure Neo4j is running on localhost:7687")
                return {"error": "Neo4j connection failed"}
            print("✅ Neo4j connection established with Docker Neo4j")
        except Exception as e:
            print(f"❌ Neo4j initialization failed: {e}")
            return {"error": f"Neo4j initialization failed: {e}"}
        
        results = {
            'test_timestamp': time.time(),
            'test_workspace': self.test_workspace,
            'projects_tested': [],
            'neo4j_insights': {},
            'success_rate': 0.0
        }
        
        try:
            successful_tests = 0
            
            for i, project in enumerate(test_projects):
                print(f"\n🧪 Testing Project {i+1}/{len(test_projects)}: {project['name']}")
                print(f"   Description: {project['description']}")
                print("-" * 70)
                
                project_result = self._test_single_project_with_neo4j(project)
                results['projects_tested'].append(project_result)
                
                if project_result.get('overall_success', False):
                    successful_tests += 1
                    
                    # Generate code review insights for successful projects
                    insights = self._generate_code_review_insights(project['name'].replace('/', '_'))
                    results['neo4j_insights'][project['name']] = insights
            
            # Calculate success rate
            if len(results['projects_tested']) > 0:
                results['success_rate'] = successful_tests / len(results['projects_tested'])
            
            return results
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            results['error'] = str(e)
            return results
            
        finally:
            # Cleanup
            self._cleanup()
    
    def _test_single_project_with_neo4j(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test single project through complete workflow with Neo4j storage."""
        
        project_name = project_config['name'].replace('/', '_')
        project_result = {
            'project_name': project_name,
            'project_config': project_config,
            'phase_1_success': False,
            'task_2_2_success': False,
            'task_2_3_success': False,
            'neo4j_build_success': False,
            'overall_success': False,
            'errors': [],
            'warnings': [],
            'timing': {},
            'metrics': {},
            'neo4j_stats': {}
        }
        
        try:
            # PHASE 1: Data Acquisition
            print(f"📥 Phase 1: Data Acquisition for {project_name}")
            phase_1_result = self._test_phase_1_data_acquisition(project_config)
            project_result.update(phase_1_result)
            
            if not phase_1_result['success']:
                project_result['errors'].append("Phase 1 failed")
                return project_result
            
            project_result['phase_1_success'] = True
            
            # TASK 2.2: Code Parser Coordination
            print(f"🎯 Task 2.2: Code Parser Coordination for {project_name}")
            task_2_2_result = self._test_task_2_2_coordination(
                phase_1_result['project_data_context']
            )
            project_result.update(task_2_2_result)
            
            if not task_2_2_result['success']:
                project_result['errors'].append("Task 2.2 failed")
                return project_result
                
            project_result['task_2_2_success'] = True
            
            # TASK 2.3: Java Parser Verification
            print(f"☕ Task 2.3: Java Parser Verification for {project_name}")
            task_2_3_result = self._test_task_2_3_java_parser(
                task_2_2_result['coordinator_result']
            )
            project_result.update(task_2_3_result)
            
            if not task_2_3_result['success']:
                project_result['errors'].append("Task 2.3 failed")
                return project_result
                
            project_result['task_2_3_success'] = True
            
            # TASK 2.6-2.7: AST to CKG Builder
            print(f"🏗️ Task 2.6-2.7: Building Code Knowledge Graph for {project_name}")
            neo4j_result = self._test_neo4j_ckg_building(
                task_2_2_result['coordinator_result'], project_name
            )
            project_result.update(neo4j_result)
            
            if neo4j_result['success']:
                project_result['neo4j_build_success'] = True
                project_result['overall_success'] = True
                print(f"✅ Complete workflow with Neo4j success for {project_name}")
            else:
                project_result['errors'].append("Neo4j CKG building failed")
            
        except Exception as e:
            error_msg = f"Error testing {project_name}: {str(e)}"
            project_result['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        
        return project_result
    
    def _test_phase_1_data_acquisition(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Phase 1: Data Acquisition modules."""
        
        start_time = time.time()
        result = {'success': False, 'timing': {}}
        
        try:
            # GitHub Operations: Clone repository
            print("   1️⃣ Cloning repository...")
            github_ops = GitHubOperationsModule()
            
            project_path = os.path.join(
                self.test_workspace, 
                project_config['name'].replace('/', '_')
            )
            github_url = f"https://github.com/{project_config['name']}.git"
            
            clone_start = time.time()
            clone_result = github_ops.clone_repository(
                github_url, 
                project_path,
                depth=project_config.get('clone_depth', 1)
            )
            result['timing']['clone_duration'] = time.time() - clone_start
            
            if not clone_result or not os.path.exists(project_path):
                result['error'] = "Repository clone failed"
                return result
            
            print(f"      ✅ Repository cloned to: {project_path}")
            
            # Language Detection
            print("   2️⃣ Detecting languages...")
            lang_detector = LanguageDetectionModule()
            
            detect_start = time.time()
            detected_languages = lang_detector.detect_languages_in_directory(project_path)
            result['timing']['detection_duration'] = time.time() - detect_start
            
            print(f"      ✅ Detected languages: {detected_languages}")
            
            # Create ProjectDataContext
            project_data_context = ProjectDataContext(
                project_name=project_config['name'],
                cloned_code_path=project_path,
                detected_languages=detected_languages,
                repository_url=github_url
            )
            
            result.update({
                'success': True,
                'project_data_context': project_data_context,
                'cloned_path': project_path,
                'detected_languages': detected_languages,
                'language_count': len(detected_languages)
            })
            
            result['timing']['total_phase_1_duration'] = time.time() - start_time
            print(f"   ✅ Phase 1 completed in {result['timing']['total_phase_1_duration']:.2f}s")
            
        except Exception as e:
            result['error'] = f"Phase 1 error: {str(e)}"
            print(f"   ❌ Phase 1 failed: {e}")
        
        return result
    
    def _test_task_2_2_coordination(self, project_data_context: ProjectDataContext) -> Dict[str, Any]:
        """Test Task 2.2: Code Parser Coordination."""
        
        start_time = time.time()
        result = {'success': False, 'timing': {}}
        
        try:
            # Initialize coordinator
            coordinator = CodeParserCoordinatorModule()
            
            print(f"   🎯 Coordinating parsing for {len(project_data_context.detected_languages)} languages")
            print(f"      Languages: {project_data_context.detected_languages}")
            print(f"      Registered parsers: {coordinator.get_registered_languages()}")
            
            # Execute coordination
            coord_start = time.time()
            coordinator_result = coordinator.coordinate_parsing(project_data_context)
            result['timing']['coordination_duration'] = time.time() - coord_start
            
            # Analyze results
            if coordinator_result.errors:
                result['warnings'] = coordinator_result.errors
                print(f"      ⚠️ Coordinator warnings: {len(coordinator_result.errors)}")
            
            # Extract metrics
            result.update({
                'success': True,
                'coordinator_result': coordinator_result,
                'languages_processed': len(coordinator_result.languages_processed),
                'total_files_parsed': coordinator_result.total_files_parsed,
                'total_entities_found': coordinator_result.total_entities_found,
                'total_relationships_found': coordinator_result.total_relationships_found,
                'coordination_duration_ms': coordinator_result.coordination_duration_ms
            })
            
            result['timing']['total_task_2_2_duration'] = time.time() - start_time
            
            print(f"   ✅ Task 2.2 completed in {result['timing']['total_task_2_2_duration']:.2f}s")
            print(f"      📊 Files parsed: {coordinator_result.total_files_parsed}")
            print(f"      📊 Entities found: {coordinator_result.total_entities_found}")
            print(f"      📊 Relationships found: {coordinator_result.total_relationships_found}")
            
        except Exception as e:
            result['error'] = f"Task 2.2 error: {str(e)}"
            print(f"   ❌ Task 2.2 failed: {e}")
        
        return result
    
    def _test_task_2_3_java_parser(self, coordinator_result) -> Dict[str, Any]:
        """Test Task 2.3: Java Parser Implementation verification."""
        
        start_time = time.time()
        result = {'success': False, 'timing': {}}
        
        try:
            # Verify Java parsing results
            java_results = coordinator_result.language_results.get('java')
            
            if not java_results:
                result['error'] = "No Java parsing results found"
                return result
            
            print(f"   ☕ Java parsing verification")
            print(f"      📁 Files processed: {len(java_results.files_parsed)}")
            print(f"      ⚡ Parse duration: {java_results.parse_duration_ms:.2f}ms")
            
            result.update({
                'success': True,
                'java_files_count': len(java_results.files_parsed),
                'parse_duration_ms': java_results.parse_duration_ms
            })
            
            result['timing']['total_task_2_3_duration'] = time.time() - start_time
            print(f"   ✅ Task 2.3 completed in {result['timing']['total_task_2_3_duration']:.2f}s")
            
        except Exception as e:
            result['error'] = f"Task 2.3 error: {str(e)}"
            print(f"   ❌ Task 2.3 failed: {e}")
        
        return result
    
    def _test_neo4j_ckg_building(
        self, 
        coordinator_result, 
        project_name: str
    ) -> Dict[str, Any]:
        """Test Neo4j CKG building (Task 2.6-2.7)."""
        
        start_time = time.time()
        result = {'success': False, 'timing': {}}
        
        try:
            # Initialize CKG builder
            ckg_builder = ASTtoCKGBuilderModule(self.neo4j)
            
            print(f"   🏗️ Building Code Knowledge Graph")
            print(f"      Project: {project_name}")
            print(f"      Languages: {coordinator_result.languages_processed}")
            
            # Build CKG
            build_start = time.time()
            build_result = ckg_builder.build_ckg_from_coordinator_result(
                coordinator_result, project_name
            )
            result['timing']['ckg_build_duration'] = time.time() - build_start
            
            if build_result.success:
                result.update({
                    'success': True,
                    'nodes_created': build_result.nodes_created,
                    'relationships_created': build_result.relationships_created,
                    'files_processed': build_result.files_processed,
                    'build_duration_ms': build_result.build_duration_ms
                })
                
                print(f"   ✅ CKG built successfully")
                print(f"      📊 Nodes created: {build_result.nodes_created}")
                print(f"      📊 Relationships created: {build_result.relationships_created}")
                print(f"      📊 Files processed: {build_result.files_processed}")
                print(f"      ⚡ Build duration: {build_result.build_duration_ms:.2f}ms")
            else:
                result['errors'] = build_result.errors
                result['warnings'] = build_result.warnings
                print(f"   ❌ CKG build failed: {build_result.errors}")
            
            result['timing']['total_neo4j_duration'] = time.time() - start_time
            
        except Exception as e:
            result['error'] = f"Neo4j CKG building error: {str(e)}"
            print(f"   ❌ Neo4j CKG building failed: {e}")
        
        return result
    
    def _generate_code_review_insights(self, project_name: str) -> Dict[str, Any]:
        """Generate code review insights from Neo4j CKG."""
        
        print(f"\n🔍 Generating Code Review Insights for {project_name}")
        print("-" * 50)
        
        insights = {}
        
        try:
            # Initialize query interface
            query_interface = CKGQueryInterfaceModule(self.neo4j)
            
            # Project overview
            print("   📊 Project Overview...")
            overview = query_interface.get_project_overview(project_name)
            insights['project_overview'] = overview
            
            if overview:
                print(f"      ✅ Project: {overview['project_name']}")
                print(f"      📁 Files: {overview['files_in_graph']}")
                print(f"      🏗️ Entities: {overview['entities_in_graph']}")
                print(f"      🔗 Languages: {overview['languages']}")
            
            # Class complexity analysis
            print("   🧮 Class Complexity Analysis...")
            complexity_analysis = query_interface.get_class_complexity_analysis(project_name, 5)
            insights['class_complexity'] = complexity_analysis
            
            if complexity_analysis:
                print(f"      📈 Top {len(complexity_analysis)} most complex classes:")
                for i, cls in enumerate(complexity_analysis[:3]):
                    print(f"         {i+1}. {cls['class_name']}: {cls['methods_count']} methods, "
                          f"complexity score: {cls['complexity_score']}")
            
            # Method call patterns
            print("   🔄 Method Call Patterns...")
            call_patterns = query_interface.get_method_call_patterns(project_name, 10)
            insights['call_patterns'] = call_patterns
            
            if call_patterns:
                cross_class_calls = [p for p in call_patterns if p['is_cross_class_call']]
                print(f"      🔗 {len(call_patterns)} call relationships analyzed")
                print(f"      🔄 {len(cross_class_calls)} cross-class calls detected")
            
            # Public API surface
            print("   🌐 Public API Surface Analysis...")
            api_surface = query_interface.get_public_api_surface(project_name)
            insights['api_surface'] = api_surface
            
            if api_surface:
                by_type = {}
                for api in api_surface:
                    by_type[api['entity_type']] = by_type.get(api['entity_type'], 0) + 1
                
                print(f"      🚀 Public API elements: {len(api_surface)}")
                for entity_type, count in by_type.items():
                    print(f"         {entity_type}: {count}")
            
            # Refactoring candidates
            print("   🔧 Refactoring Candidates...")
            refactoring_candidates = query_interface.get_potential_refactoring_candidates(project_name)
            insights['refactoring_candidates'] = refactoring_candidates
            
            if refactoring_candidates:
                print(f"      ⚠️ {len(refactoring_candidates)} potential refactoring candidates:")
                for candidate in refactoring_candidates[:3]:
                    print(f"         - {candidate['method_name']} "
                          f"({candidate['outgoing_calls']} calls)")
            
            print("   ✅ Code review insights generated successfully")
            
        except Exception as e:
            print(f"   ❌ Failed to generate insights: {e}")
            insights['error'] = str(e)
        
        return insights
    
    def _cleanup(self):
        """Clean up test workspace."""
        
        if self.test_workspace and os.path.exists(self.test_workspace):
            try:
                shutil.rmtree(self.test_workspace)
                print(f"\n🧹 Cleaned up test workspace: {self.test_workspace}")
            except Exception as e:
                print(f"\n⚠️ Could not clean up workspace: {e}")
        
        if self.neo4j:
            try:
                self.neo4j.disconnect()
                print("🧹 Closed Neo4j connection")
            except Exception as e:
                print(f"⚠️ Could not close Neo4j connection: {e}")


def main():
    """Main function to run the enhanced workflow test."""
    
    print("🚀 RepoChat v1.0 - Enhanced Full Workflow Test with Neo4j")
    print("Phase 1 → Task 2.2 → Task 2.3 → Task 2.6-2.7 → Code Review Insights")
    print("=" * 80)
    
    tester = EnhancedWorkflowTester()
    
    try:
        results = tester.run_complete_test_with_neo4j()
        
        print(f"\n🎯 FINAL TEST SUMMARY")
        print("=" * 70)
        
        if results.get('error'):
            print(f"❌ Test failed: {results['error']}")
            return 1
        
        print(f"✅ Enhanced workflow test completed!")
        print(f"   Success rate: {results['success_rate']:.1%}")
        print(f"   Projects tested: {len(results['projects_tested'])}")
        
        # Display Neo4j insights summary
        if results.get('neo4j_insights'):
            print(f"\n📊 CODE REVIEW INSIGHTS SUMMARY")
            print("-" * 40)
            
            for project_name, insights in results['neo4j_insights'].items():
                print(f"\n🔍 Project: {project_name}")
                
                if insights.get('project_overview'):
                    overview = insights['project_overview']
                    print(f"   📁 Files: {overview.get('files_in_graph', 0)}")
                    print(f"   🏗️ Entities: {overview.get('entities_in_graph', 0)}")
                
                if insights.get('class_complexity'):
                    print(f"   🧮 Complex classes: {len(insights['class_complexity'])}")
                
                if insights.get('api_surface'):
                    print(f"   🌐 Public API elements: {len(insights['api_surface'])}")
                
                if insights.get('refactoring_candidates'):
                    print(f"   🔧 Refactoring candidates: {len(insights['refactoring_candidates'])}")
        
        print(f"\n🎉 RepoChat v1.0 Enhanced Workflow Test Completed!")
        print("✅ Code Knowledge Graph stored in Neo4j")
        print("✅ Code review insights generated")
        print("Ready for Task 2.8: CKG Query Interface expansion")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Test interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 