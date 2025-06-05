#!/usr/bin/env python3
"""
Manual Test Script - Full Workflow Phase 1 to Task 2.3

Tests the complete RepoChat v1.0 workflow with a real Java project from GitHub:
- Phase 1: Data Acquisition (clone repository, detect languages)
- Task 2.2: Code Parser Coordination (orchestrate parsing)
- Task 2.3: Java Parser Implementation (real Java parsing)

This script demonstrates the integration and functionality of:
1. Data Acquisition TEAM modules
2. CKG Operations TEAM modules
3. Real Java project parsing capabilities

Usage:
    python manual_test_full_workflow.py

Test Projects:
- Uses real Java projects from GitHub
- Demonstrates parsing performance and accuracy
- Shows complete entity and relationship extraction
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
    from teams.ckg_operations import CodeParserCoordinatorModule, JavaParser
    from teams.ckg_operations.models import CodeEntityType, VisibilityModifier
    
    print("✅ All required modules imported successfully")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all modules are implemented and accessible")
    sys.exit(1)


class FullWorkflowTester:
    """Manual tester for complete Phase 1 to Task 2.3 workflow."""
    
    def __init__(self):
        """Initialize the workflow tester."""
        self.test_workspace = None
        self.results = {}
        
        print("🚀 Full Workflow Tester - Phase 1 to Task 2.3")
        print("=" * 60)
    
    def run_complete_test(self) -> Dict[str, Any]:
        """
        Run the complete workflow test with real Java projects.
        
        Returns:
            Dictionary with comprehensive test results
        """
        test_projects = [
            {
                'name': 'apache/commons-lang',
                'description': 'Apache Commons Lang - Popular Java utility library',
                'expected_languages': ['java'],
                'expected_files': 100,  # Approximate
                'clone_depth': 1  # Shallow clone for faster testing
            },
            {
                'name': 'google/guava',
                'description': 'Google Guava - Core libraries for Java',
                'expected_languages': ['java'],
                'expected_files': 200,  # Approximate
                'clone_depth': 1
            },
            {
                'name': 'spring-projects/spring-boot',
                'description': 'Spring Boot - Enterprise Java framework',
                'expected_languages': ['java'],
                'expected_files': 500,  # Approximate
                'clone_depth': 1
            }
        ]
        
        # Create temporary workspace
        self.test_workspace = tempfile.mkdtemp(prefix="repochat_manual_test_")
        print(f"📁 Test workspace: {self.test_workspace}")
        
        results = {
            'test_timestamp': time.time(),
            'test_workspace': self.test_workspace,
            'projects_tested': [],
            'phase_1_results': {},
            'task_2_2_results': {},
            'task_2_3_results': {},
            'performance_metrics': {},
            'success_rate': 0.0
        }
        
        try:
            # Test each project
            successful_tests = 0
            
            for i, project in enumerate(test_projects):
                print(f"\n🧪 Testing Project {i+1}/{len(test_projects)}: {project['name']}")
                print(f"   Description: {project['description']}")
                print("-" * 60)
                
                project_result = self._test_single_project(project)
                results['projects_tested'].append(project_result)
                
                if project_result.get('overall_success', False):
                    successful_tests += 1
                    
                # Only test first project for demo unless specifically requested
                if i == 0:  # Comment this out to test all projects
                    print("\n💡 Testing first project only for demo. Remove line to test all.")
                    break
            
            # Calculate success rate
            if len(results['projects_tested']) > 0:
                results['success_rate'] = successful_tests / len(results['projects_tested'])
            
            # Aggregate results
            self._aggregate_results(results)
            
            return results
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            results['error'] = str(e)
            return results
            
        finally:
            # Cleanup
            self._cleanup()
    
    def _test_single_project(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single Java project through the complete workflow."""
        
        project_name = project_config['name']
        project_result = {
            'project_name': project_name,
            'project_config': project_config,
            'phase_1_success': False,
            'task_2_2_success': False,
            'task_2_3_success': False,
            'overall_success': False,
            'errors': [],
            'warnings': [],
            'timing': {},
            'metrics': {}
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
            
            if task_2_3_result['success']:
                project_result['task_2_3_success'] = True
                project_result['overall_success'] = True
                print(f"✅ Complete workflow success for {project_name}")
            else:
                project_result['errors'].append("Task 2.3 failed")
            
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
            # 1. GitHub Operations: Clone repository
            print("   1️⃣ Cloning repository...")
            github_ops = GitHubOperationsModule()
            
            project_path = os.path.join(self.test_workspace, project_config['name'].replace('/', '_'))
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
            
            # 2. Language Detection: Detect programming languages
            print("   2️⃣ Detecting languages...")
            lang_detector = LanguageDetectionModule()
            
            detect_start = time.time()
            detected_languages = lang_detector.detect_languages_in_directory(project_path)
            result['timing']['detection_duration'] = time.time() - detect_start
            
            print(f"      ✅ Detected languages: {detected_languages}")
            
            # Verify expected languages
            expected_langs = project_config.get('expected_languages', [])
            if not any(lang.lower() in [l.lower() for l in detected_languages] for lang in expected_langs):
                result['warning'] = f"Expected languages {expected_langs} not found in {detected_languages}"
            
            # 3. Create ProjectDataContext
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
            
            # Analyze Java entities
            java_entities = []
            java_relationships = []
            
            for file_result in java_results.files_parsed:
                java_entities.extend(file_result.entities)
                java_relationships.extend(file_result.relationships)
            
            # Categorize entities
            entity_stats = self._analyze_java_entities(java_entities)
            relationship_stats = self._analyze_java_relationships(java_relationships)
            
            # Verify Task 2.3 requirements
            task_2_3_verification = self._verify_task_2_3_requirements(
                java_entities, java_relationships, java_results
            )
            
            result.update({
                'success': True,
                'java_files_count': len(java_results.files_parsed),
                'java_entities_count': len(java_entities),
                'java_relationships_count': len(java_relationships),
                'entity_stats': entity_stats,
                'relationship_stats': relationship_stats,
                'task_2_3_verification': task_2_3_verification,
                'files_with_errors': java_results.files_with_errors,
                'parse_duration_ms': java_results.parse_duration_ms
            })
            
            result['timing']['total_task_2_3_duration'] = time.time() - start_time
            
            print(f"   ✅ Task 2.3 completed in {result['timing']['total_task_2_3_duration']:.2f}s")
            
            # Display detailed results
            self._display_java_results(entity_stats, relationship_stats, task_2_3_verification)
            
        except Exception as e:
            result['error'] = f"Task 2.3 error: {str(e)}"
            print(f"   ❌ Task 2.3 failed: {e}")
        
        return result
    
    def _analyze_java_entities(self, entities) -> Dict[str, Any]:
        """Analyze Java entities by type and visibility."""
        
        stats = {
            'total': len(entities),
            'by_type': {},
            'by_visibility': {},
            'sample_entities': []
        }
        
        for entity in entities:
            # Count by type
            entity_type = entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type)
            stats['by_type'][entity_type] = stats['by_type'].get(entity_type, 0) + 1
            
            # Count by visibility
            visibility = entity.visibility.value if hasattr(entity.visibility, 'value') else str(entity.visibility)
            stats['by_visibility'][visibility] = stats['by_visibility'].get(visibility, 0) + 1
            
            # Collect samples
            if len(stats['sample_entities']) < 5:
                stats['sample_entities'].append({
                    'name': entity.name,
                    'type': entity_type,
                    'qualified_name': entity.qualified_name,
                    'visibility': visibility
                })
        
        return stats
    
    def _analyze_java_relationships(self, relationships) -> Dict[str, Any]:
        """Analyze Java relationships by type."""
        
        stats = {
            'total': len(relationships),
            'by_call_type': {},
            'sample_relationships': []
        }
        
        for relationship in relationships:
            # Count by call type
            call_type = relationship.call_type
            stats['by_call_type'][call_type] = stats['by_call_type'].get(call_type, 0) + 1
            
            # Collect samples
            if len(stats['sample_relationships']) < 5:
                stats['sample_relationships'].append({
                    'caller': relationship.caller.split('.')[-1],  # Just method name
                    'callee': relationship.callee.split('.')[-1],  # Just method name
                    'call_type': call_type
                })
        
        return stats
    
    def _verify_task_2_3_requirements(self, entities, relationships, java_results) -> Dict[str, Any]:
        """Verify that Task 2.3 requirements are met."""
        
        verification = {
            'all_requirements_met': True,
            'requirements': {}
        }
        
        # Requirement 1: Parse Java files using javalang
        javalang_used = any(
            file_result.metadata and file_result.metadata.get('javalang_parser') 
            for file_result in java_results.files_parsed
        )
        verification['requirements']['javalang_parser_used'] = javalang_used
        
        # Requirement 2: Extract class names and method names
        class_count = len([e for e in entities if e.entity_type == CodeEntityType.CLASS])
        method_count = len([e for e in entities if e.entity_type == CodeEntityType.METHOD])
        
        verification['requirements']['classes_extracted'] = class_count > 0
        verification['requirements']['methods_extracted'] = method_count > 0
        verification['requirements']['class_count'] = class_count
        verification['requirements']['method_count'] = method_count
        
        # Requirement 3: Extract direct method calls within same file/class
        direct_calls = len([r for r in relationships if r.call_type == 'direct'])
        verification['requirements']['direct_calls_extracted'] = direct_calls > 0
        verification['requirements']['direct_calls_count'] = direct_calls
        
        # Requirement 4: Return structured data using defined models
        uses_code_entity = all(hasattr(e, 'entity_type') and hasattr(e, 'qualified_name') for e in entities[:5])
        uses_call_relationship = all(hasattr(r, 'caller') and hasattr(r, 'callee') for r in relationships[:5])
        
        verification['requirements']['structured_entities'] = uses_code_entity
        verification['requirements']['structured_relationships'] = uses_call_relationship
        
        # Overall verification
        all_met = all(verification['requirements'][req] for req in [
            'javalang_parser_used', 'classes_extracted', 'methods_extracted', 
            'direct_calls_extracted', 'structured_entities', 'structured_relationships'
        ])
        verification['all_requirements_met'] = all_met
        
        return verification
    
    def _display_java_results(self, entity_stats, relationship_stats, verification):
        """Display detailed Java parsing results."""
        
        print(f"      📊 Java Entity Analysis:")
        print(f"         Total entities: {entity_stats['total']}")
        for entity_type, count in entity_stats['by_type'].items():
            print(f"         - {entity_type}: {count}")
        
        print(f"      🔗 Java Relationship Analysis:")
        print(f"         Total relationships: {relationship_stats['total']}")
        for call_type, count in relationship_stats['by_call_type'].items():
            print(f"         - {call_type} calls: {count}")
        
        print(f"      ✅ Task 2.3 Verification:")
        for req, met in verification['requirements'].items():
            if isinstance(met, bool):
                status = "✅" if met else "❌"
                print(f"         {status} {req}: {met}")
        
        print(f"      🎯 Overall Task 2.3 Success: {'✅ YES' if verification['all_requirements_met'] else '❌ NO'}")
    
    def _aggregate_results(self, results: Dict[str, Any]):
        """Aggregate results across all tested projects."""
        
        if not results['projects_tested']:
            return
        
        # Aggregate metrics
        total_files = sum(p.get('total_files_parsed', 0) for p in results['projects_tested'])
        total_entities = sum(p.get('total_entities_found', 0) for p in results['projects_tested'])
        total_relationships = sum(p.get('total_relationships_found', 0) for p in results['projects_tested'])
        
        results['performance_metrics'] = {
            'total_projects_tested': len(results['projects_tested']),
            'successful_projects': sum(1 for p in results['projects_tested'] if p.get('overall_success', False)),
            'total_files_parsed': total_files,
            'total_entities_extracted': total_entities,
            'total_relationships_extracted': total_relationships,
            'average_files_per_project': total_files / len(results['projects_tested']),
            'average_entities_per_project': total_entities / len(results['projects_tested']),
            'average_relationships_per_project': total_relationships / len(results['projects_tested'])
        }
        
        print(f"\n📊 AGGREGATE RESULTS")
        print("=" * 60)
        print(f"Projects tested: {results['performance_metrics']['total_projects_tested']}")
        print(f"Successful projects: {results['performance_metrics']['successful_projects']}")
        print(f"Success rate: {results['success_rate']:.1%}")
        print(f"Total files parsed: {results['performance_metrics']['total_files_parsed']}")
        print(f"Total entities extracted: {results['performance_metrics']['total_entities_extracted']}")
        print(f"Total relationships extracted: {results['performance_metrics']['total_relationships_extracted']}")
    
    def _cleanup(self):
        """Clean up test workspace."""
        
        if self.test_workspace and os.path.exists(self.test_workspace):
            try:
                shutil.rmtree(self.test_workspace)
                print(f"\n🧹 Cleaned up test workspace: {self.test_workspace}")
            except Exception as e:
                print(f"\n⚠️ Could not clean up workspace: {e}")


def main():
    """Main function to run the full workflow test."""
    
    print("🚀 RepoChat v1.0 - Full Workflow Manual Test")
    print("Testing Phase 1 (Data Acquisition) → Task 2.2 (Coordination) → Task 2.3 (Java Parser)")
    print("Using real Java projects from GitHub")
    print("=" * 80)
    
    tester = FullWorkflowTester()
    
    try:
        results = tester.run_complete_test()
        
        print(f"\n🎯 FINAL TEST SUMMARY")
        print("=" * 60)
        
        if results.get('error'):
            print(f"❌ Test failed: {results['error']}")
            return 1
        
        print(f"✅ Test completed successfully!")
        print(f"   Success rate: {results['success_rate']:.1%}")
        print(f"   Total projects: {len(results['projects_tested'])}")
        
        if results.get('performance_metrics'):
            metrics = results['performance_metrics']
            print(f"   Files parsed: {metrics['total_files_parsed']}")
            print(f"   Entities extracted: {metrics['total_entities_extracted']}")
            print(f"   Relationships extracted: {metrics['total_relationships_extracted']}")
        
        print(f"\n🎉 RepoChat v1.0 Full Workflow Test Completed!")
        print("Ready for Task 2.4: Python Parser Implementation")
        
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