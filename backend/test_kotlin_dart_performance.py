#!/usr/bin/env python3
"""
Performance Testing for Kotlin and Dart Parsers

Tests the newly implemented Kotlin and Dart parsers with real-world projects
to validate performance and accuracy.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from teams.data_acquisition.git_operations_module import GitOperationsModule
from teams.ckg_operations.kotlin_parser import KotlinParser
from teams.ckg_operations.dart_parser import DartParser
from teams.ckg_operations.code_parser_coordinator_module import CodeParserCoordinatorModule


class PerformanceTestRunner:
    """Runs performance tests for Kotlin and Dart parsers with real projects."""
    
    def __init__(self):
        self.git_module = GitOperationsModule()
        self.kotlin_parser = KotlinParser()
        self.dart_parser = DartParser()
        self.coordinator = CodeParserCoordinatorModule()
        
        # Test projects for each language
        self.test_projects = {
            'kotlin': [
                {
                    'name': 'Kotlin Examples',
                    'url': 'https://github.com/JetBrains/kotlin-examples.git',
                    'description': 'JetBrains official Kotlin examples'
                },
                {
                    'name': 'OkHttp',
                    'url': 'https://github.com/square/okhttp.git',
                    'description': 'Popular HTTP client library written in Kotlin'
                }
            ],
            'dart': [
                {
                    'name': 'Flutter Samples',
                    'url': 'https://github.com/flutter/samples.git',
                    'description': 'Official Flutter sample applications'
                },
                {
                    'name': 'Dart SDK Samples',
                    'url': 'https://github.com/dart-lang/samples.git',
                    'description': 'Dart language samples and examples'
                }
            ]
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run performance tests for all languages."""
        print("🚀 Starting Kotlin and Dart Parser Performance Tests")
        print("=" * 60)
        
        results = {
            'kotlin': [],
            'dart': [],
            'summary': {}
        }
        
        # Test Kotlin projects
        print("\n📱 Testing Kotlin Projects")
        print("-" * 30)
        for project in self.test_projects['kotlin']:
            result = self.test_project(project, 'kotlin')
            results['kotlin'].append(result)
        
        # Test Dart projects
        print("\n🎯 Testing Dart Projects")
        print("-" * 30)
        for project in self.test_projects['dart']:
            result = self.test_project(project, 'dart')
            results['dart'].append(result)
        
        # Generate summary
        results['summary'] = self.generate_summary(results)
        
        return results
    
    def test_project(self, project: Dict[str, str], language: str) -> Dict[str, Any]:
        """Test a single project."""
        print(f"\n🔍 Testing: {project['name']}")
        print(f"   URL: {project['url']}")
        print(f"   Description: {project['description']}")
        
        result = {
            'name': project['name'],
            'url': project['url'],
            'language': language,
            'success': False,
            'error': None,
            'metrics': {}
        }
        
        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix=f'repochat_test_{language}_')
            
            # Clone project
            print(f"   📥 Cloning to: {temp_dir}")
            clone_start = time.time()
            try:
                clone_result = self.git_module.clone_repository(project['url'], temp_dir)
                clone_time = time.time() - clone_start
                
                if not clone_result:
                    result['error'] = f"Failed to clone: No result returned"
                    return result
            except Exception as e:
                clone_time = time.time() - clone_start
                result['error'] = f"Failed to clone: {str(e)}"
                return result
            
            print(f"   ✅ Cloned in {clone_time:.2f}s")
            
            # Find source files
            parser = self.kotlin_parser if language == 'kotlin' else self.dart_parser
            files = parser.find_source_files(temp_dir)
            
            if not files:
                result['error'] = f"No {language} files found in project"
                return result
            
            print(f"   📁 Found {len(files)} {language} files")
            
            # Parse files
            print(f"   🔧 Parsing {language} files...")
            parse_start = time.time()
            
            total_entities = 0
            total_relationships = 0
            successful_files = 0
            failed_files = 0
            
            for file_path in files:
                try:
                    file_result = parser.parse_file(file_path, temp_dir)
                    if file_result.errors:
                        failed_files += 1
                    else:
                        successful_files += 1
                        total_entities += len(file_result.entities)
                        total_relationships += len(file_result.relationships)
                except Exception as e:
                    failed_files += 1
                    print(f"     ❌ Error parsing {file_path}: {e}")
            
            parse_time = time.time() - parse_start
            
            # Get parser statistics
            stats = parser.get_stats()
            
            result['success'] = True
            result['metrics'] = {
                'clone_time_s': clone_time,
                'parse_time_s': parse_time,
                'total_files': len(files),
                'successful_files': successful_files,
                'failed_files': failed_files,
                'success_rate': (successful_files / len(files)) * 100 if files else 0,
                'total_entities': total_entities,
                'total_relationships': total_relationships,
                'avg_parse_time_ms': (parse_time / len(files)) * 1000 if files else 0,
                'entities_per_file': total_entities / successful_files if successful_files else 0,
                'relationships_per_file': total_relationships / successful_files if successful_files else 0,
                'parser_stats': stats
            }
            
            # Print results
            metrics = result['metrics']
            print(f"   📊 Results:")
            print(f"      • Total files: {metrics['total_files']}")
            print(f"      • Successful: {metrics['successful_files']}")
            print(f"      • Failed: {metrics['failed_files']}")
            print(f"      • Success rate: {metrics['success_rate']:.1f}%")
            print(f"      • Parse time: {metrics['parse_time_s']:.2f}s")
            print(f"      • Avg per file: {metrics['avg_parse_time_ms']:.1f}ms")
            print(f"      • Total entities: {metrics['total_entities']}")
            print(f"      • Total relationships: {metrics['total_relationships']}")
            print(f"      • Entities per file: {metrics['entities_per_file']:.1f}")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"   ❌ Test failed: {e}")
        
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"   ⚠️  Failed to cleanup {temp_dir}: {e}")
        
        return result
    
    def generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics."""
        summary = {
            'total_projects_tested': 0,
            'successful_projects': 0,
            'failed_projects': 0,
            'languages_tested': ['kotlin', 'dart'],
            'total_files_parsed': 0,
            'total_entities_found': 0,
            'total_relationships_found': 0,
            'average_success_rate': 0,
            'performance_benchmarks': {}
        }
        
        all_projects = results['kotlin'] + results['dart']
        summary['total_projects_tested'] = len(all_projects)
        
        successful_projects = [p for p in all_projects if p['success']]
        summary['successful_projects'] = len(successful_projects)
        summary['failed_projects'] = summary['total_projects_tested'] - summary['successful_projects']
        
        if successful_projects:
            summary['total_files_parsed'] = sum(p['metrics']['total_files'] for p in successful_projects)
            summary['total_entities_found'] = sum(p['metrics']['total_entities'] for p in successful_projects)
            summary['total_relationships_found'] = sum(p['metrics']['total_relationships'] for p in successful_projects)
            summary['average_success_rate'] = sum(p['metrics']['success_rate'] for p in successful_projects) / len(successful_projects)
            
            # Performance benchmarks by language
            for lang in ['kotlin', 'dart']:
                lang_projects = [p for p in results[lang] if p['success']]
                if lang_projects:
                    total_parse_time = sum(p['metrics']['parse_time_s'] for p in lang_projects)
                    total_files = sum(p['metrics']['total_files'] for p in lang_projects)
                    
                    summary['performance_benchmarks'][lang] = {
                        'projects_tested': len(lang_projects),
                        'total_files': total_files,
                        'total_parse_time_s': total_parse_time,
                        'avg_time_per_file_ms': (total_parse_time / total_files) * 1000 if total_files else 0,
                        'files_per_second': total_files / total_parse_time if total_parse_time > 0 else 0
                    }
        
        return summary
    
    def print_final_report(self, results: Dict[str, Any]):
        """Print final performance report."""
        print("\n" + "=" * 80)
        print("📋 KOTLIN & DART PARSERS PERFORMANCE REPORT")
        print("=" * 80)
        
        summary = results['summary']
        
        print(f"\n🎯 Overall Results:")
        print(f"   • Projects tested: {summary['total_projects_tested']}")
        print(f"   • Successful: {summary['successful_projects']}")
        print(f"   • Failed: {summary['failed_projects']}")
        print(f"   • Success rate: {(summary['successful_projects']/summary['total_projects_tested']*100):.1f}%" if summary['total_projects_tested'] > 0 else "   • Success rate: N/A")
        
        print(f"\n📊 Parsing Statistics:")
        print(f"   • Total files parsed: {summary['total_files_parsed']}")
        print(f"   • Total entities found: {summary['total_entities_found']}")
        print(f"   • Total relationships found: {summary['total_relationships_found']}")
        print(f"   • Average success rate: {summary['average_success_rate']:.1f}%")
        
        print(f"\n⚡ Performance Benchmarks:")
        for lang, bench in summary['performance_benchmarks'].items():
            print(f"   {lang.upper()}:")
            print(f"     • Projects: {bench['projects_tested']}")
            print(f"     • Files: {bench['total_files']}")
            print(f"     • Parse time: {bench['total_parse_time_s']:.2f}s")
            print(f"     • Avg per file: {bench['avg_time_per_file_ms']:.1f}ms")
            print(f"     • Throughput: {bench['files_per_second']:.1f} files/sec")
        
        # Print detailed results
        print(f"\n📋 Detailed Results:")
        for lang in ['kotlin', 'dart']:
            print(f"\n  {lang.upper()} Projects:")
            for project in results[lang]:
                status = "✅" if project['success'] else "❌"
                print(f"    {status} {project['name']}")
                if not project['success']:
                    print(f"       Error: {project['error']}")
                elif project['metrics']:
                    m = project['metrics']
                    print(f"       Files: {m['total_files']}, Entities: {m['total_entities']}, Success: {m['success_rate']:.1f}%")
        
        print("\n" + "=" * 80)
        print("🎉 Task 2.5 Performance Testing Completed!")
        print("=" * 80)


def main():
    """Main function to run performance tests."""
    print("🚀 RepoChat v1.0 - Kotlin & Dart Parser Performance Testing")
    print("Testing newly implemented parsers with real-world projects")
    print()
    
    runner = PerformanceTestRunner()
    
    try:
        results = runner.run_all_tests()
        runner.print_final_report(results)
        
        # Check if tests passed minimum criteria
        summary = results['summary']
        min_success_rate = 80  # Minimum 80% project success rate
        
        if summary['successful_projects'] / summary['total_projects_tested'] >= (min_success_rate / 100):
            print(f"✅ Performance tests PASSED (≥{min_success_rate}% success rate)")
            return True
        else:
            print(f"❌ Performance tests FAILED (<{min_success_rate}% success rate)")
            return False
            
    except Exception as e:
        print(f"❌ Performance testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 