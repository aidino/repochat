#!/usr/bin/env python3
"""
Comprehensive Performance Test Suite for RepoChat Phase 1 + 2
Testing with Real-World Projects for Each Language

Languages Tested:
- Java: Spring Boot projects, Android projects  
- Kotlin: Android Kotlin projects
- Dart: Flutter projects
- Python: Popular Python libraries

This script tests complete Phase 1 + 2 workflow with performance metrics.
"""

import os
import sys
import time
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.shared.utils.logging_config import setup_logging
from src.teams.data_acquisition.git_operations_module import GitOperationsModule
from src.teams.data_acquisition.language_identifier_module import LanguageIdentifierModule
from src.teams.data_acquisition.data_preparation_module import DataPreparationModule
from src.teams.ckg_operations.code_parser_coordinator_module import CodeParserCoordinatorModule
from src.teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule
from src.teams.ckg_operations.ast_to_ckg_builder_module import ASTtoCKGBuilderModule

@dataclass
class ProjectTestCase:
    """Test case definition for a real project"""
    name: str
    url: str
    language: str
    description: str
    expected_files_min: int
    expected_classes_min: int = 0
    expected_methods_min: int = 0

@dataclass
class PerformanceMetrics:
    """Performance metrics for a test"""
    clone_time: float
    language_detect_time: float
    parsing_time: float
    ckg_build_time: float
    total_time: float
    files_parsed: int
    entities_found: int
    relationships_created: int
    nodes_created: int

@dataclass
class TestResult:
    """Complete test result"""
    project: ProjectTestCase
    success: bool
    error_message: str = ""
    metrics: PerformanceMetrics = None
    details: Dict[str, Any] = None

class RealProjectPerformanceTester:
    """Performance tester for real-world projects"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.neo4j_config = {
            "uri": "bolt://localhost:7687",
            "username": "neo4j", 
            "password": "repochat123"
        }
        
        # Define test cases
        self.test_cases = [
            # Java Projects
            ProjectTestCase(
                name="Spring PetClinic",
                url="https://github.com/spring-projects/spring-petclinic.git",
                language="java",
                description="Classic Spring Boot application",
                expected_files_min=30,
                expected_classes_min=25,
                expected_methods_min=100
            ),
            ProjectTestCase(
                name="Spring Boot Sample",
                url="https://github.com/spring-projects/spring-boot.git",
                language="java", 
                description="Spring Boot framework (large codebase)",
                expected_files_min=500,
                expected_classes_min=200,
                expected_methods_min=1000
            ),
            
            # Kotlin Projects  
            ProjectTestCase(
                name="KMP Production Sample",
                url="https://github.com/Kotlin/kmp-production-sample.git",
                language="kotlin",
                description="Official Kotlin Multiplatform Mobile RSS reader production sample",
                expected_files_min=30,
                expected_classes_min=15,
                expected_methods_min=50
            ),
            ProjectTestCase(
                name="Android Architecture Samples",
                url="https://github.com/android/architecture-samples.git", 
                language="kotlin",
                description="Android MVVM architecture samples",
                expected_files_min=30,
                expected_classes_min=15,
                expected_methods_min=50
            ),
            
            # Dart/Flutter Projects
            ProjectTestCase(
                name="Flutter Samples",
                url="https://github.com/flutter/samples.git",
                language="dart",
                description="Official Flutter samples",
                expected_files_min=100,
                expected_classes_min=50,
                expected_methods_min=200
            ),
            ProjectTestCase(
                name="FlutterFire",
                url="https://github.com/firebase/flutterfire.git",
                language="dart", 
                description="Firebase Flutter plugins",
                expected_files_min=200,
                expected_classes_min=100,
                expected_methods_min=500
            ),
            
            # Python Projects
            ProjectTestCase(
                name="FastAPI",
                url="https://github.com/tiangolo/fastapi.git",
                language="python",
                description="Modern Python web framework",
                expected_files_min=50,
                expected_classes_min=30,
                expected_methods_min=200
            ),
            ProjectTestCase(
                name="Requests",
                url="https://github.com/psf/requests.git", 
                language="python",
                description="HTTP library for Python",
                expected_files_min=20,
                expected_classes_min=10,
                expected_methods_min=50
            )
        ]
    
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_project(self, project: ProjectTestCase) -> TestResult:
        """Test a single project with complete Phase 1 + 2 workflow"""
        self.log(f"\n🚀 Testing Project: {project.name}")
        self.log(f"📋 Language: {project.language.upper()}")
        self.log(f"🔗 Repository: {project.url}")
        self.log(f"📝 Description: {project.description}")
        self.log("=" * 80)
        
        start_time = time.time()
        cloned_path = None
        
        try:
            # Phase 1: Data Acquisition
            self.log("🔵 PHASE 1: Data Acquisition Starting...")
            
            # Step 1: Git Clone
            clone_start = time.time()
            git_ops = GitOperationsModule()
            cloned_path = git_ops.clone_repository(project.url)
            clone_time = time.time() - clone_start
            
            self.log(f"✅ Git Clone: {clone_time:.2f}s -> {cloned_path}")
            
            # Step 2: Language Detection
            detect_start = time.time()
            lang_identifier = LanguageIdentifierModule()
            detected_languages = lang_identifier.identify_languages(cloned_path)
            detect_time = time.time() - detect_start
            
            self.log(f"✅ Language Detection: {detect_time:.2f}s -> {detected_languages}")
            
            # Verify expected language is detected
            if project.language not in detected_languages:
                raise ValueError(f"Expected language '{project.language}' not detected. Found: {detected_languages}")
            
            # Step 3: Data Preparation
            data_prep = DataPreparationModule()
            project_context = data_prep.create_project_context(
                cloned_code_path=cloned_path,
                detected_languages=detected_languages,
                repository_url=project.url
            )
            
            self.log(f"✅ Data Preparation: Primary={project_context.primary_language}, Count={project_context.language_count}")
            
            # Phase 2: Code Knowledge Graph Operations
            self.log("🟢 PHASE 2: CKG Operations Starting...")
            
            # Step 4: Code Parsing
            parse_start = time.time()
            parser_coordinator = CodeParserCoordinatorModule()
            parse_result = parser_coordinator.coordinate_parsing(project_context)
            parse_time = time.time() - parse_start
            
            self.log(f"✅ Code Parsing: {parse_time:.2f}s")
            self.log(f"   📊 Files: {parse_result.total_files_parsed}")
            self.log(f"   📊 Entities: {parse_result.total_entities_found}")
            self.log(f"   📊 Languages: {list(parse_result.language_results.keys())}")
            
            # Verify parsing results
            if parse_result.total_files_parsed < project.expected_files_min:
                self.log(f"⚠️  Warning: Expected >={project.expected_files_min} files, got {parse_result.total_files_parsed}", "WARN")
            
            # Step 5: CKG Building
            ckg_start = time.time()
            neo4j_conn = Neo4jConnectionModule(**self.neo4j_config)
            
            # Test connection
            if not neo4j_conn.connect():
                raise RuntimeError("Failed to connect to Neo4j")
            
            # Clear existing data for clean test
            with neo4j_conn.get_session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            
            # Build CKG
            ckg_builder = ASTtoCKGBuilderModule(neo4j_conn)
            project_name = f"{project.name.lower().replace(' ', '-')}-test"
            
            build_result = ckg_builder.build_ckg_from_coordinator_result(
                parse_result, 
                project_name
            )
            ckg_time = time.time() - ckg_start
            
            # Verify CKG build success
            if not build_result.success:
                raise RuntimeError(f"CKG build failed: {build_result.errors}")
            
            self.log(f"✅ CKG Building: {ckg_time:.2f}s")
            self.log(f"   📊 Nodes: {build_result.nodes_created}")
            self.log(f"   📊 Relationships: {build_result.relationships_created}")
            
            # Verify graph in Neo4j
            with neo4j_conn.get_session() as session:
                result = session.run("MATCH (n) RETURN count(n) as total")
                total_nodes = result.single()["total"]
                
                result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
                total_rels = result.single()["total"]
            
            neo4j_conn.disconnect()
            
            # Calculate total time
            total_time = time.time() - start_time
            
            # Create performance metrics
            metrics = PerformanceMetrics(
                clone_time=clone_time,
                language_detect_time=detect_time,
                parsing_time=parse_time,
                ckg_build_time=ckg_time,
                total_time=total_time,
                files_parsed=parse_result.total_files_parsed,
                entities_found=parse_result.total_entities_found,
                relationships_created=build_result.relationships_created,
                nodes_created=build_result.nodes_created
            )
            
            # Create detailed results
            details = {
                "cloned_path": cloned_path,
                "detected_languages": detected_languages,
                "primary_language": project_context.primary_language,
                "parse_result_summary": {
                    "languages_processed": list(parse_result.language_results.keys()),
                    "total_files": parse_result.total_files_parsed,
                    "total_entities": parse_result.total_entities_found
                },
                "ckg_summary": {
                    "project_name": project_name,
                    "nodes_in_db": total_nodes,
                    "relationships_in_db": total_rels,
                    "build_success": build_result.success
                }
            }
            
            self.log(f"🎉 SUCCESS: {project.name} completed in {total_time:.2f}s")
            
            return TestResult(
                project=project,
                success=True,
                metrics=metrics,
                details=details
            )
            
        except Exception as e:
            total_time = time.time() - start_time
            error_msg = str(e)
            
            self.log(f"❌ FAILED: {project.name} - {error_msg}", "ERROR")
            
            return TestResult(
                project=project,
                success=False,
                error_message=error_msg,
                metrics=PerformanceMetrics(
                    clone_time=0, language_detect_time=0, parsing_time=0,
                    ckg_build_time=0, total_time=total_time,
                    files_parsed=0, entities_found=0, relationships_created=0, nodes_created=0
                )
            )
        
        finally:
            # Cleanup
            if cloned_path and os.path.exists(cloned_path):
                try:
                    shutil.rmtree(cloned_path)
                    self.log(f"🧹 Cleaned up: {cloned_path}")
                except Exception as e:
                    self.log(f"⚠️  Cleanup failed: {e}", "WARN")
    
    def run_all_tests(self, limit: int = None) -> List[TestResult]:
        """Run all test cases"""
        self.log("🚀 Starting Real Project Performance Test Suite")
        self.log(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"🎯 Target Languages: Java, Kotlin, Dart, Python")
        
        test_cases = self.test_cases[:limit] if limit else self.test_cases
        self.log(f"📋 Total Projects: {len(test_cases)}")
        
        results = []
        
        for i, project in enumerate(test_cases, 1):
            self.log(f"\n📍 Progress: {i}/{len(test_cases)}")
            result = self.test_project(project)
            results.append(result)
            self.results.append(result)
            
            # Brief summary after each test
            if result.success:
                self.log(f"✅ {project.name}: {result.metrics.total_time:.1f}s, "
                        f"{result.metrics.files_parsed} files, "
                        f"{result.metrics.entities_found} entities")
            else:
                self.log(f"❌ {project.name}: FAILED - {result.error_message}")
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.results:
            return {"error": "No test results available"}
        
        # Overall statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        
        # Performance statistics for successful tests
        successful_results = [r for r in self.results if r.success]
        
        performance_stats = {}
        if successful_results:
            total_times = [r.metrics.total_time for r in successful_results]
            clone_times = [r.metrics.clone_time for r in successful_results]
            parse_times = [r.metrics.parsing_time for r in successful_results]
            ckg_times = [r.metrics.ckg_build_time for r in successful_results]
            
            performance_stats = {
                "total_time": {
                    "min": min(total_times),
                    "max": max(total_times),
                    "avg": sum(total_times) / len(total_times),
                    "sum": sum(total_times)
                },
                "clone_time": {
                    "min": min(clone_times),
                    "max": max(clone_times),
                    "avg": sum(clone_times) / len(clone_times)
                },
                "parsing_time": {
                    "min": min(parse_times),
                    "max": max(parse_times),
                    "avg": sum(parse_times) / len(parse_times)
                },
                "ckg_build_time": {
                    "min": min(ckg_times),
                    "max": max(ckg_times),
                    "avg": sum(ckg_times) / len(ckg_times)
                }
            }
        
        # Language breakdown
        language_stats = {}
        for result in self.results:
            lang = result.project.language
            if lang not in language_stats:
                language_stats[lang] = {"total": 0, "success": 0, "failed": 0}
            
            language_stats[lang]["total"] += 1
            if result.success:
                language_stats[lang]["success"] += 1
            else:
                language_stats[lang]["failed"] += 1
        
        # Generate detailed results
        detailed_results = []
        for result in self.results:
            detailed_results.append({
                "project_name": result.project.name,
                "language": result.project.language,
                "success": result.success,
                "error_message": result.error_message,
                "metrics": asdict(result.metrics) if result.metrics else None,
                "details": result.details
            })
        
        return {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0
            },
            "performance_statistics": performance_stats,
            "language_breakdown": language_stats,
            "detailed_results": detailed_results,
            "test_timestamp": datetime.now().isoformat(),
            "phase_coverage": "Phase 1 (Data Acquisition) + Phase 2 (CKG Operations)"
        }
    
    def print_summary_report(self):
        """Print formatted summary report"""
        report = self.generate_report()
        
        print("\n" + "="*80)
        print("📊 REAL PROJECT PERFORMANCE TEST REPORT")
        print("="*80)
        
        # Test Summary
        summary = report["test_summary"]
        print(f"\n🎯 TEST SUMMARY:")
        print(f"   Total Projects Tested: {summary['total_tests']}")
        print(f"   ✅ Successful: {summary['successful_tests']}")
        print(f"   ❌ Failed: {summary['failed_tests']}")
        print(f"   📈 Success Rate: {summary['success_rate']:.1%}")
        
        # Performance Statistics
        if "performance_statistics" in report and report["performance_statistics"]:
            perf = report["performance_statistics"]
            print(f"\n⚡ PERFORMANCE STATISTICS (Successful Tests):")
            print(f"   Total Execution Time:")
            print(f"     • Average: {perf['total_time']['avg']:.2f}s")
            print(f"     • Range: {perf['total_time']['min']:.2f}s - {perf['total_time']['max']:.2f}s")
            print(f"     • Combined: {perf['total_time']['sum']:.2f}s")
            
            print(f"   Phase Breakdown (Average):")
            print(f"     • Git Clone: {perf['clone_time']['avg']:.2f}s")
            print(f"     • Code Parsing: {perf['parsing_time']['avg']:.2f}s")
            print(f"     • CKG Building: {perf['ckg_build_time']['avg']:.2f}s")
        
        # Language Breakdown
        lang_stats = report["language_breakdown"]
        print(f"\n🔤 LANGUAGE BREAKDOWN:")
        for lang, stats in lang_stats.items():
            success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            print(f"   {lang.upper()}:")
            print(f"     • Tests: {stats['total']} | Success: {stats['success']} | Failed: {stats['failed']}")
            print(f"     • Success Rate: {success_rate:.1%}")
        
        # Detailed Results
        print(f"\n📋 DETAILED RESULTS:")
        for result in report["detailed_results"]:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status} | {result['project_name']} ({result['language']})")
            
            if result["success"] and result["metrics"]:
                m = result["metrics"]
                print(f"       ⏱️  Time: {m['total_time']:.2f}s | Files: {m['files_parsed']} | Entities: {m['entities_found']} | Nodes: {m['nodes_created']}")
            elif not result["success"]:
                print(f"       💥 Error: {result['error_message']}")
        
        print("\n" + "="*80)
        print(f"✅ Report Generated: {report['test_timestamp']}")
        print(f"🎯 Phase Coverage: {report['phase_coverage']}")
        print("="*80)

def main():
    """Main test execution"""
    # Setup logging
    setup_logging()
    
    # Create tester
    tester = RealProjectPerformanceTester()
    
    # Check if limit argument provided
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            print(f"🎯 Testing limited to first {limit} projects")
        except ValueError:
            print("⚠️  Invalid limit argument, testing all projects")
    
    # Run tests
    start_time = time.time()
    results = tester.run_all_tests(limit=limit)
    total_time = time.time() - start_time
    
    # Generate report
    tester.print_summary_report()
    
    # Save detailed report to file
    report = tester.generate_report()
    report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: {report_file}")
    print(f"⏱️  Total test suite execution time: {total_time:.2f}s")

if __name__ == "__main__":
    main() 