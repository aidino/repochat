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
import tempfile
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.shared.utils.logging_config import get_logger
from src.teams.data_acquisition import (
    GitOperationsModule,
    LanguageIdentifierModule, 
    DataPreparationModule,
    PATHandlerModule
)

class ComprehensivePhaseOptimizer:
    """
    Comprehensive optimizer và validator cho 3 phase đầu tiên của RepoChat.
    """
    
    def __init__(self):
        self.logger = get_logger("phase_optimizer", extra_context={'test_suite': 'comprehensive'})
        self.test_results = {}
        self.start_time = datetime.now()
        
        # Test repositories for comprehensive testing
        self.test_repositories = {
            'small_java': 'https://github.com/spring-projects/spring-petclinic.git',
            'medium_python': 'https://github.com/pallets/flask.git',
        }
        
        # Performance benchmarks
        self.performance_targets = {
            'git_clone_time': 30.0,  # seconds
            'language_detection_time': 5.0,
            'data_preparation_time': 10.0,
            'memory_usage_mb': 500.0,
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
            
            # Generate comprehensive report
            final_report = self._generate_optimization_report({
                'phase_1': phase1_results,
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
                    
                    # Handle both string and CloneResult
                    if isinstance(clone_result, str):
                        # Old API - create CloneResult-like object
                        class TempResult:
                            success = True
                            local_path = clone_result
                        clone_result = TempResult()
                    
                    # Validate clone result
                    assert clone_result.success, f"Clone failed for {repo_name}"
                    assert os.path.exists(clone_result.local_path), f"Local path not found for {repo_name}"
                    
                    # Check git repository validity
                    git_dir = os.path.join(clone_result.local_path, '.git')
                    assert os.path.exists(git_dir), f"Git directory not found for {repo_name}"
                    
                    results[repo_name] = {
                        'status': 'PASSED',
                        'clone_time': clone_time,
                        'local_path': clone_result.local_path,
                        'repository_size_mb': self._get_directory_size_mb(clone_result.local_path),
                        'within_target': clone_time < self.performance_targets['git_clone_time']
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
                        
                        results[repo_name] = {
                            'status': 'PASSED',
                            'detected_languages': detected_languages,
                            'detection_time': detection_time,
                            'file_count': self._count_files_by_extension(clone_result.local_path),
                            'within_target': detection_time < self.performance_targets['language_detection_time']
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
                        
                        results[repo_name] = {
                            'status': 'PASSED',
                            'preparation_time': prep_time,
                            'context_valid': True,
                            'languages_count': len(detected_languages),
                            'within_target': prep_time < self.performance_targets['data_preparation_time']
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
            'recommendations': [],
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
        
    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main() 