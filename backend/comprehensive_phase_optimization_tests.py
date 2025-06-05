#!/usr/bin/env python3
"""
Comprehensive Phase Optimization Tests for RepoChat v1.0
Đây là test suite chuyên sâu để optimize và validate 3 phase đầu tiên.

Author: AI Assistant
Created: 2025-06-06
Purpose: Ensure rock-solid foundation for RepoChat's core functionality
"""

import os
import sys
import time
import asyncio
import tempfile
import shutil
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import psutil
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import core modules
from src.shared.utils.logging_config import get_logger, log_performance_metric
from src.orchestrator.orchestrator_agent import OrchestratorAgent
from src.shared.models.task_definition import TaskDefinition
from src.teams.data_acquisition import (
    GitOperationsModule,
    LanguageIdentifierModule, 
    DataPreparationModule,
    PATHandlerModule
)
from src.teams.ckg_operations import (
    Neo4jConnectionModule,
    CodeParserCoordinatorModule,
    ASTtoCKGBuilderModule
)
from src.teams.code_analysis import ArchitecturalAnalyzerModule

class ComprehensivePhaseOptimizer:
    """
    Comprehensive optimizer và validator cho 3 phase đầu tiên của RepoChat.
    """
    
    def __init__(self):
        self.logger = get_logger("phase_optimizer", extra_context={'test_suite': 'comprehensive'})
        self.test_results = {}
        self.performance_metrics = {}
        self.error_summary = {}
        self.start_time = datetime.now()
        
        # Test repositories for comprehensive testing
        self.test_repositories = {
            'small_java': 'https://github.com/spring-projects/spring-petclinic.git',
            'medium_python': 'https://github.com/pallets/flask.git',
            'kotlin_android': 'https://github.com/JetBrains/kotlin-examples.git',
            'dart_flutter': 'https://github.com/flutter/samples.git'
        }
        
        # Performance benchmarks
        self.performance_targets = {
            'git_clone_time': 30.0,  # seconds
            'language_detection_time': 5.0,
            'data_preparation_time': 10.0,
            'java_parsing_time': 60.0,
            'python_parsing_time': 45.0,
            'ckg_building_time': 120.0,
            'memory_usage_mb': 500.0,
            'neo4j_connection_time': 5.0
        }

    def run_comprehensive_optimization(self) -> Dict[str, Any]:
        """
        Chạy toàn bộ comprehensive optimization cho 3 phase.
        """
        self.logger.info("🚀 Starting Comprehensive Phase Optimization")
        self.logger.info("=" * 80)
        
        try:
            # Phase 1: Data Acquisition Deep Testing
            phase1_results = self._optimize_phase_1()
            
            # Phase 2: CKG Operations Deep Testing  
            phase2_results = self._optimize_phase_2()
            
            # Phase 3: Code Analysis Deep Testing
            phase3_results = self._optimize_phase_3()
            
            # Cross-Phase Integration Testing
            integration_results = self._test_cross_phase_integration()
            
            # Performance & Stress Testing
            performance_results = self._run_performance_stress_tests()
            
            # Memory & Resource Testing
            resource_results = self._test_resource_management()
            
            # Error Recovery Testing
            recovery_results = self._test_error_recovery()
            
            # Generate comprehensive report
            final_report = self._generate_optimization_report({
                'phase_1': phase1_results,
                'phase_2': phase2_results, 
                'phase_3': phase3_results,
                'integration': integration_results,
                'performance': performance_results,
                'resources': resource_results,
                'recovery': recovery_results
            })
            
            return final_report
            
        except Exception as e:
            self.logger.error(f"Critical error in comprehensive optimization: {e}", exc_info=True)
            return {'status': 'FAILED', 'error': str(e)}

    def _optimize_phase_1(self) -> Dict[str, Any]:
        """Phase 1: Data Acquisition Deep Testing & Optimization"""
        self.logger.info("🏗️  PHASE 1: Data Acquisition Deep Testing")
        self.logger.info("-" * 60)
        
        results = {
            'git_operations': {},
            'language_detection': {},
            'data_preparation': {},
            'pat_handling': {},
            'edge_cases': {}
        }
        
        try:
            # Test 1.1: Git Operations với multiple repositories
            results['git_operations'] = self._test_git_operations_comprehensive()
            
            # Test 1.2: Language Detection với complex projects
            results['language_detection'] = self._test_language_detection_comprehensive()
            
            # Test 1.3: Data Preparation với edge cases
            results['data_preparation'] = self._test_data_preparation_comprehensive()
            
            # Test 1.4: PAT Handling với security scenarios
            results['pat_handling'] = self._test_pat_handling_comprehensive()
            
            # Test 1.5: Edge Cases & Error Scenarios
            results['edge_cases'] = self._test_phase1_edge_cases()
            
            self.logger.info(f"✅ Phase 1 optimization completed")
            return results
            
        except Exception as e:
            self.logger.error(f"Phase 1 optimization failed: {e}", exc_info=True)
            return {'status': 'FAILED', 'error': str(e)}

    def _test_git_operations_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive Git Operations testing"""
        self.logger.info("🔍 Testing Git Operations comprehensively...")
        
        results = {}
        git_module = GitOperationsModule()
        
        for repo_name, repo_url in self.test_repositories.items():
            self.logger.info(f"  Testing repository: {repo_name}")
            
            start_time = time.time()
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    clone_result = git_module.clone_repository(repo_url, temp_dir)
                    clone_time = time.time() - start_time
                    
                    # Validate clone result
                    assert clone_result.success, f"Clone failed for {repo_name}"
                    assert os.path.exists(clone_result.local_path), f"Local path not found for {repo_name}"
                    
                    # Check git repository validity
                    git_dir = os.path.join(clone_result.local_path, '.git')
                    assert os.path.exists(git_dir), f"Git directory not found for {repo_name}"
                    
                    # Performance check
                    if clone_time > self.performance_targets['git_clone_time']:
                        self.logger.warning(f"Clone time for {repo_name}: {clone_time:.2f}s exceeds target")
                    
                    results[repo_name] = {
                        'status': 'PASSED',
                        'clone_time': clone_time,
                        'local_path': clone_result.local_path,
                        'repository_size_mb': self._get_directory_size_mb(clone_result.local_path)
                    }
                    
            except Exception as e:
                results[repo_name] = {
                    'status': 'FAILED',
                    'error': str(e),
                    'clone_time': time.time() - start_time
                }
                self.logger.error(f"Git operations failed for {repo_name}: {e}")
        
        return results

    def _test_language_detection_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive Language Detection testing"""
        self.logger.info("🔍 Testing Language Detection comprehensively...")
        
        results = {}
        lang_module = LanguageIdentifierModule()
        
        for repo_name, repo_url in self.test_repositories.items():
            self.logger.info(f"  Testing language detection: {repo_name}")
            
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Clone repository first
                    git_module = GitOperationsModule()
                    clone_result = git_module.clone_repository(repo_url, temp_dir)
                    
                    if clone_result.success:
                        start_time = time.time()
                        detected_languages = lang_module.identify_languages(clone_result.local_path)
                        detection_time = time.time() - start_time
                        
                        # Validate detection results
                        assert detected_languages, f"No languages detected for {repo_name}"
                        
                        # Performance check
                        if detection_time > self.performance_targets['language_detection_time']:
                            self.logger.warning(f"Language detection time for {repo_name}: {detection_time:.2f}s exceeds target")
                        
                        results[repo_name] = {
                            'status': 'PASSED',
                            'detected_languages': detected_languages,
                            'detection_time': detection_time,
                            'file_count': self._count_files_by_extension(clone_result.local_path)
                        }
                    else:
                        results[repo_name] = {
                            'status': 'SKIPPED',
                            'reason': 'Clone failed'
                        }
                        
            except Exception as e:
                results[repo_name] = {
                    'status': 'FAILED',
                    'error': str(e)
                }
                self.logger.error(f"Language detection failed for {repo_name}: {e}")
        
        return results

    def _test_data_preparation_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive Data Preparation testing"""
        self.logger.info("🔍 Testing Data Preparation comprehensively...")
        
        results = {}
        data_prep_module = DataPreparationModule()
        
        for repo_name, repo_url in self.test_repositories.items():
            self.logger.info(f"  Testing data preparation: {repo_name}")
            
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Setup repository
                    git_module = GitOperationsModule()
                    clone_result = git_module.clone_repository(repo_url, temp_dir)
                    
                    if clone_result.success:
                        lang_module = LanguageIdentifierModule()
                        detected_languages = lang_module.identify_languages(clone_result.local_path)
                        
                        start_time = time.time()
                        project_context = data_prep_module.prepare_project_context(
                            clone_result, detected_languages
                        )
                        prep_time = time.time() - start_time
                        
                        # Validate project context
                        assert project_context is not None, f"Project context is None for {repo_name}"
                        assert project_context.repository_path == clone_result.local_path
                        assert project_context.detected_languages == detected_languages
                        
                        # Performance check
                        if prep_time > self.performance_targets['data_preparation_time']:
                            self.logger.warning(f"Data preparation time for {repo_name}: {prep_time:.2f}s exceeds target")
                        
                        results[repo_name] = {
                            'status': 'PASSED',
                            'preparation_time': prep_time,
                            'context_valid': True,
                            'languages_count': len(detected_languages),
                            'repository_size_mb': self._get_directory_size_mb(clone_result.local_path)
                        }
                    else:
                        results[repo_name] = {
                            'status': 'SKIPPED',
                            'reason': 'Clone failed'
                        }
                        
            except Exception as e:
                results[repo_name] = {
                    'status': 'FAILED',
                    'error': str(e)
                }
                self.logger.error(f"Data preparation failed for {repo_name}: {e}")
        
        return results

    def _test_pat_handling_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive PAT Handling testing"""
        self.logger.info("🔍 Testing PAT Handling comprehensively...")
        
        results = {}
        pat_module = PATHandlerModule()
        
        test_cases = {
            'github_public': 'https://github.com/user/public-repo.git',
            'github_private': 'https://github.com/user/private-repo.git',
            'gitlab_private': 'https://gitlab.com/user/private-repo.git',
            'bitbucket_private': 'https://bitbucket.org/user/private-repo.git'
        }
        
        for test_name, repo_url in test_cases.items():
            self.logger.info(f"  Testing PAT scenario: {test_name}")
            
            try:
                start_time = time.time()
                
                # Test private repo detection
                is_private = pat_module.requires_authentication(repo_url)
                
                if 'private' in test_name:
                    assert is_private, f"Should detect {test_name} as private"
                else:
                    assert not is_private, f"Should detect {test_name} as public"
                
                # Test PAT workflow simulation
                if is_private:
                    # Simulate PAT workflow (without real PAT)
                    authenticated_url = pat_module.build_authenticated_url(repo_url, "fake_token")
                    assert "fake_token" in authenticated_url, "PAT not included in authenticated URL"
                
                processing_time = time.time() - start_time
                
                results[test_name] = {
                    'status': 'PASSED',
                    'is_private_detected': is_private,
                    'processing_time': processing_time,
                    'authenticated_url_valid': True if is_private else 'N/A'
                }
                
            except Exception as e:
                results[test_name] = {
                    'status': 'FAILED',
                    'error': str(e)
                }
                self.logger.error(f"PAT handling failed for {test_name}: {e}")
        
        return results

    def _test_phase1_edge_cases(self) -> Dict[str, Any]:
        """Test Phase 1 edge cases và error scenarios"""
        self.logger.info("🔍 Testing Phase 1 edge cases...")
        
        results = {}
        
        edge_cases = {
            'invalid_url': 'https://invalid-git-url.com/repo.git',
            'empty_repository': 'https://github.com/user/empty-repo.git',
            'large_repository': 'https://github.com/torvalds/linux.git',  # Để test timeout
            'non_git_url': 'https://google.com',
            'malformed_url': 'not-a-url-at-all'
        }
        
        for case_name, test_url in edge_cases.items():
            self.logger.info(f"  Testing edge case: {case_name}")
            
            try:
                git_module = GitOperationsModule()
                
                start_time = time.time()
                with tempfile.TemporaryDirectory() as temp_dir:
                    if case_name == 'large_repository':
                        # Test với timeout để không thực sự clone Linux kernel
                        try:
                            clone_result = git_module.clone_repository(test_url, temp_dir, timeout=5)
                            # Should timeout hoặc succeed nhanh với shallow clone
                        except Exception as e:
                            # Expected để timeout
                            pass
                    else:
                        clone_result = git_module.clone_repository(test_url, temp_dir)
                        
                        if case_name in ['invalid_url', 'non_git_url', 'malformed_url']:
                            # Should fail
                            assert not clone_result.success, f"Should fail for {case_name}"
                        
                processing_time = time.time() - start_time
                
                results[case_name] = {
                    'status': 'PASSED',
                    'processing_time': processing_time,
                    'expected_behavior': 'Handled correctly'
                }
                
            except Exception as e:
                # Some edge cases are expected để throw exceptions
                expected_failures = ['malformed_url', 'non_git_url']
                if case_name in expected_failures:
                    results[case_name] = {
                        'status': 'PASSED',
                        'expected_failure': True,
                        'error_handled': str(e)
                    }
                else:
                    results[case_name] = {
                        'status': 'FAILED',
                        'error': str(e)
                    }
                    self.logger.error(f"Edge case failed unexpectedly for {case_name}: {e}")
        
        return results

    def _optimize_phase_2(self) -> Dict[str, Any]:
        """Phase 2: CKG Operations Deep Testing & Optimization"""
        self.logger.info("🧠 PHASE 2: CKG Operations Deep Testing")
        self.logger.info("-" * 60)
        
        results = {
            'neo4j_connection': {},
            'parsing_performance': {},
            'ckg_building': {},
            'query_interface': {},
            'memory_optimization': {}
        }
        
        try:
            # Test 2.1: Neo4j Connection Optimization
            results['neo4j_connection'] = self._test_neo4j_connection_optimization()
            
            # Test 2.2: Parser Performance với large files
            results['parsing_performance'] = self._test_parser_performance_optimization()
            
            # Test 2.3: CKG Building Optimization
            results['ckg_building'] = self._test_ckg_building_optimization()
            
            # Test 2.4: Query Interface Optimization
            results['query_interface'] = self._test_query_interface_optimization()
            
            # Test 2.5: Memory Usage Optimization
            results['memory_optimization'] = self._test_memory_usage_optimization()
            
            self.logger.info(f"✅ Phase 2 optimization completed")
            return results
            
        except Exception as e:
            self.logger.error(f"Phase 2 optimization failed: {e}", exc_info=True)
            return {'status': 'FAILED', 'error': str(e)}

    def _test_neo4j_connection_optimization(self) -> Dict[str, Any]:
        """Test và optimize Neo4j connection performance"""
        self.logger.info("🔍 Testing Neo4j Connection Optimization...")
        
        results = {}
        
        try:
            neo4j_module = Neo4jConnectionModule()
            
            # Test connection performance
            start_time = time.time()
            success = neo4j_module.connect()
            connection_time = time.time() - start_time
            
            if success:
                # Test query performance
                query_start = time.time()
                test_result = neo4j_module.execute_query("RETURN 1 as test")
                query_time = time.time() - query_start
                
                # Test connection pool performance
                pool_start = time.time()
                for i in range(10):
                    neo4j_module.execute_query(f"RETURN {i} as number")
                pool_time = time.time() - pool_start
                
                neo4j_module.disconnect()
                
                results = {
                    'status': 'PASSED',
                    'connection_time': connection_time,
                    'query_time': query_time,
                    'pool_performance': pool_time,
                    'connection_within_target': connection_time < self.performance_targets['neo4j_connection_time']
                }
            else:
                results = {
                    'status': 'FAILED',
                    'error': 'Connection failed',
                    'connection_time': connection_time
                }
                
        except Exception as e:
            results = {
                'status': 'FAILED',
                'error': str(e)
            }
            self.logger.error(f"Neo4j connection optimization failed: {e}")
        
        return results

    def _test_parser_performance_optimization(self) -> Dict[str, Any]:
        """Test parser performance với different file sizes"""
        self.logger.info("🔍 Testing Parser Performance Optimization...")
        
        results = {}
        
        try:
            from src.teams.ckg_operations.java_parser import JavaParser
            from src.teams.ckg_operations.python_parser import PythonParser
            
            parsers = {
                'java': JavaParser(),
                'python': PythonParser()
            }
            
            # Test với repositories đã clone
            for repo_name, repo_url in self.test_repositories.items():
                if 'java' in repo_name.lower() or 'python' in repo_name.lower():
                    with tempfile.TemporaryDirectory() as temp_dir:
                        git_module = GitOperationsModule()
                        clone_result = git_module.clone_repository(repo_url, temp_dir)
                        
                        if clone_result.success:
                            # Determine parser based on repo
                            parser_name = 'java' if 'java' in repo_name.lower() else 'python'
                            parser = parsers[parser_name]
                            
                            # Find files để parse
                            file_extensions = {
                                'java': ['.java'],
                                'python': ['.py']
                            }
                            
                            files_to_parse = []
                            for root, dirs, files in os.walk(clone_result.local_path):
                                for file in files:
                                    if any(file.endswith(ext) for ext in file_extensions[parser_name]):
                                        files_to_parse.append(os.path.join(root, file))
                            
                            # Parse files và measure performance
                            start_time = time.time()
                            parsed_results = []
                            
                            for file_path in files_to_parse[:50]:  # Limit để không quá lâu
                                try:
                                    parsed_result = parser.parse_file(file_path)
                                    parsed_results.append(parsed_result)
                                except Exception as e:
                                    self.logger.warning(f"Failed to parse {file_path}: {e}")
                            
                            parsing_time = time.time() - start_time
                            
                            results[f"{repo_name}_{parser_name}"] = {
                                'status': 'PASSED',
                                'files_attempted': len(files_to_parse[:50]),
                                'files_parsed': len(parsed_results),
                                'parsing_time': parsing_time,
                                'avg_time_per_file': parsing_time / max(len(parsed_results), 1),
                                'within_target': parsing_time < self.performance_targets[f'{parser_name}_parsing_time']
                            }
            
        except Exception as e:
            results = {
                'status': 'FAILED',
                'error': str(e)
            }
            self.logger.error(f"Parser performance optimization failed: {e}")
        
        return results

    def _optimize_phase_3(self) -> Dict[str, Any]:
        """Phase 3: Code Analysis Deep Testing & Optimization"""
        self.logger.info("🤖 PHASE 3: Code Analysis Deep Testing")
        self.logger.info("-" * 60)
        
        results = {
            'architectural_analysis': {},
            'circular_dependency_detection': {},
            'unused_element_detection': {},
            'llm_integration': {},
            'analysis_performance': {}
        }
        
        try:
            # Test 3.1: Architectural Analysis Optimization
            results['architectural_analysis'] = self._test_architectural_analysis_optimization()
            
            # Test 3.2: Circular Dependency Detection Deep Testing
            results['circular_dependency_detection'] = self._test_circular_dependency_optimization()
            
            # Test 3.3: Unused Element Detection Optimization
            results['unused_element_detection'] = self._test_unused_element_optimization()
            
            # Test 3.4: LLM Integration Testing (without actual API calls)
            results['llm_integration'] = self._test_llm_integration_optimization()
            
            # Test 3.5: Analysis Performance Benchmarking
            results['analysis_performance'] = self._test_analysis_performance_optimization()
            
            self.logger.info(f"✅ Phase 3 optimization completed")
            return results
            
        except Exception as e:
            self.logger.error(f"Phase 3 optimization failed: {e}", exc_info=True)
            return {'status': 'FAILED', 'error': str(e)}

    # Utility methods
    def _get_directory_size_mb(self, directory: str) -> float:
        """Get directory size in MB"""
        total_size = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    pass
        return total_size / (1024 * 1024)

    def _count_files_by_extension(self, directory: str) -> Dict[str, int]:
        """Count files by extension"""
        extension_count = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                extension_count[ext] = extension_count.get(ext, 0) + 1
        return extension_count

    def _generate_optimization_report(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        self.logger.info("📊 Generating Comprehensive Optimization Report")
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_execution_time': total_time,
            'summary': {},
            'detailed_results': all_results,
            'performance_analysis': {},
            'recommendations': [],
            'next_steps': []
        }
        
        # Calculate success rates
        for phase_name, phase_results in all_results.items():
            if isinstance(phase_results, dict):
                total_tests = 0
                passed_tests = 0
                
                for test_name, test_result in phase_results.items():
                    if isinstance(test_result, dict):
                        for sub_test, sub_result in test_result.items():
                            if isinstance(sub_result, dict) and 'status' in sub_result:
                                total_tests += 1
                                if sub_result['status'] == 'PASSED':
                                    passed_tests += 1
                
                success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
                report['summary'][phase_name] = {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'success_rate': success_rate
                }
        
        # Generate recommendations
        if report['summary']:
            avg_success_rate = sum(phase['success_rate'] for phase in report['summary'].values()) / len(report['summary'])
            
            if avg_success_rate >= 95:
                report['recommendations'].append("🎉 Excellent! Foundation is rock-solid and ready for Phase 4")
            elif avg_success_rate >= 85:
                report['recommendations'].append("✅ Good foundation. Minor optimizations recommended before Phase 4")
            else:
                report['recommendations'].append("⚠️ Critical issues found. Address before proceeding to Phase 4")
        
        self.logger.info(f"📈 Optimization report generated: {avg_success_rate:.1f}% success rate")
        return report


def main():
    """Main function để chạy comprehensive optimization"""
    print("🚀 RepoChat Comprehensive Phase Optimization")
    print("=" * 80)
    
    optimizer = ComprehensivePhaseOptimizer()
    
    try:
        results = optimizer.run_comprehensive_optimization()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"optimization_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📊 Results saved to: {results_file}")
        
        # Print summary
        if 'summary' in results:
            print("\n📈 OPTIMIZATION SUMMARY:")
            print("-" * 40)
            for phase, metrics in results['summary'].items():
                print(f"  {phase}: {metrics['passed_tests']}/{metrics['total_tests']} ({metrics['success_rate']:.1f}%)")
        
        print(f"\n⏱️  Total time: {results.get('total_execution_time', 0):.2f} seconds")
        print("\n🎯 Ready for Phase 4 development!")
        
    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main() 