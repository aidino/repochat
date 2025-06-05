#!/usr/bin/env python3
"""
RepoChat Phase 1-3 Comprehensive Manual Testing Suite

This script provides complete manual testing for all Phase 1-3 functionality
using real OpenAI API and real repositories.

Usage:
    python comprehensive_phase_1_3_manual_test.py [--repo-url REPO_URL] [--openai-test]

Requirements:
    - OpenAI API key in .env file
    - Neo4j running (for CKG operations)
    - Internet connection for repository cloning
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import asdict

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import all Phase 1-3 components
from teams.data_acquisition.git_operations_module import GitOperationsModule
from teams.data_acquisition.language_identifier_module import LanguageIdentifierModule
from teams.data_acquisition.data_preparation_module import DataPreparationModule
from teams.ckg_operations.code_parser_coordinator_module import CodeParserCoordinatorModule
from teams.ckg_operations.neo4j_connection_module import Neo4jConnectionModule
from teams.ckg_operations.ast_to_ckg_builder_module import ASTtoCKGBuilderModule
from teams.ckg_operations.ckg_query_interface_module import CKGQueryInterfaceModule
from teams.code_analysis.architectural_analyzer_module import ArchitecturalAnalyzerModule
from teams.code_analysis.pr_impact_analyzer_module import PRImpactAnalyzerModule
from teams.code_analysis.llm_analysis_support_module import LLMAnalysisSupportModule
from teams.code_analysis.static_analysis_integrator_module import StaticAnalysisIntegratorModule
from teams.llm_services.llm_gateway_module import LLMGatewayModule
from teams.llm_services.team_llm_services import TeamLLMServices
from orchestrator.orchestrator_agent import OrchestratorAgent
from data_models.project_data_context import ProjectDataContext, PRDiffInfo
from data_models.task_definition import TaskDefinition


class ComprehensivePhase13TestSuite:
    """Comprehensive testing suite for Phase 1-3 functionality."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize test suite with configuration.
        
        Args:
            config: Configuration dictionary with API keys, URLs, etc.
        """
        self.config = config
        self.test_results = []
        self.setup_logging()
        
        # Test repositories for different scenarios
        self.test_repos = {
            'java_spring': 'https://github.com/spring-projects/spring-petclinic.git',
            'python_flask': 'https://github.com/pallets/flask.git',
            'multi_lang': 'https://github.com/microsoft/vscode.git',
            'small_repo': 'https://github.com/octocat/Hello-World.git'
        }
        
        # Initialize components
        self.components = {}
        self.initialize_components()

    def setup_logging(self):
        """Setup comprehensive logging for testing."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"comprehensive_test_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Starting comprehensive Phase 1-3 testing: {timestamp}")

    def initialize_components(self):
        """Initialize all Phase 1-3 components."""
        try:
            # Phase 1: Data Acquisition
            self.components['git_ops'] = GitOperationsModule()
            self.components['lang_id'] = LanguageIdentifierModule()
            self.components['data_prep'] = DataPreparationModule()
            
            # Phase 1: CKG Operations
            self.components['parser_coord'] = CodeParserCoordinatorModule()
            self.components['neo4j'] = Neo4jConnectionModule(
                uri=self.config.get('neo4j_uri', 'bolt://localhost:7687'),
                username=self.config.get('neo4j_username', 'neo4j'),
                password=self.config.get('neo4j_password', 'password')
            )
            self.components['ast_to_ckg'] = ASTtoCKGBuilderModule(self.components['neo4j'])
            self.components['ckg_query'] = CKGQueryInterfaceModule(self.components['neo4j'])
            
            # Phase 2: Code Analysis
            self.components['arch_analyzer'] = ArchitecturalAnalyzerModule()
            self.components['pr_impact'] = PRImpactAnalyzerModule()
            self.components['llm_support'] = LLMAnalysisSupportModule()
            self.components['static_analysis'] = StaticAnalysisIntegratorModule()
            
            # Phase 2: LLM Services
            self.components['llm_gateway'] = LLMGatewayModule()
            self.components['team_llm'] = TeamLLMServices()
            
            # Phase 3: Orchestrator
            self.components['orchestrator'] = OrchestratorAgent()
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise

    async def test_phase_1_data_acquisition(self, repo_url: str) -> Dict[str, Any]:
        """
        Test Phase 1: Data Acquisition functionality.
        
        Args:
            repo_url: Repository URL to test with
            
        Returns:
            Test results dictionary
        """
        self.logger.info("=== TESTING PHASE 1: DATA ACQUISITION ===")
        
        phase_results = {
            'phase': 'Phase 1 - Data Acquisition',
            'tests': [],
            'success': True,
            'start_time': datetime.now().isoformat(),
            'repo_url': repo_url
        }
        
        try:
            # Test 1.1: Git Operations - Repository Cloning
            self.logger.info("Test 1.1: Repository Cloning")
            start_time = datetime.now()
            
            cloned_path = await self.components['git_ops'].clone_repository(repo_url)
            
            test_result = {
                'test_name': 'Repository Cloning',
                'success': cloned_path is not None,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'cloned_path': str(cloned_path) if cloned_path else None,
                    'exists': cloned_path.exists() if cloned_path else False
                }
            }
            phase_results['tests'].append(test_result)
            
            if not test_result['success']:
                phase_results['success'] = False
                return phase_results
            
            # Test 1.2: Language Identification
            self.logger.info("Test 1.2: Language Identification")
            start_time = datetime.now()
            
            detected_languages = await self.components['lang_id'].analyze_project_languages(cloned_path)
            
            test_result = {
                'test_name': 'Language Identification',
                'success': len(detected_languages) > 0,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'detected_languages': detected_languages,
                    'language_count': len(detected_languages)
                }
            }
            phase_results['tests'].append(test_result)
            
            # Test 1.3: Data Preparation
            self.logger.info("Test 1.3: Data Preparation")
            start_time = datetime.now()
            
            context = ProjectDataContext(
                cloned_code_path=str(cloned_path),
                detected_languages=detected_languages,
                repository_url=repo_url
            )
            
            prepared_context = await self.components['data_prep'].prepare_project_data(context)
            
            test_result = {
                'test_name': 'Data Preparation',
                'success': prepared_context is not None,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'context_valid': prepared_context is not None,
                    'has_languages': len(prepared_context.detected_languages) > 0 if prepared_context else False
                }
            }
            phase_results['tests'].append(test_result)
            
            # Store context for next phases
            phase_results['project_context'] = prepared_context
            
        except Exception as e:
            self.logger.error(f"Phase 1 testing failed: {e}")
            phase_results['success'] = False
            phase_results['error'] = str(e)
        
        phase_results['end_time'] = datetime.now().isoformat()
        return phase_results

    async def test_phase_1_ckg_operations(self, project_context: ProjectDataContext) -> Dict[str, Any]:
        """
        Test Phase 1: CKG Operations functionality.
        
        Args:
            project_context: Project context from data acquisition
            
        Returns:
            Test results dictionary
        """
        self.logger.info("=== TESTING PHASE 1: CKG OPERATIONS ===")
        
        phase_results = {
            'phase': 'Phase 1 - CKG Operations',
            'tests': [],
            'success': True,
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Test 1.4: Code Parser Coordinator
            self.logger.info("Test 1.4: Code Parsing")
            start_time = datetime.now()
            
            parsed_entities = await self.components['parser_coord'].parse_project(project_context)
            
            test_result = {
                'test_name': 'Code Parsing',
                'success': len(parsed_entities) > 0,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'total_entities': len(parsed_entities),
                    'entity_types': list(set(entity.entity_type.value for entity in parsed_entities))
                }
            }
            phase_results['tests'].append(test_result)
            
            # Test 1.5: Neo4j Connection
            self.logger.info("Test 1.5: Neo4j Connection")
            start_time = datetime.now()
            
            connection_result = await self.components['neo4j'].test_connection()
            
            test_result = {
                'test_name': 'Neo4j Connection',
                'success': connection_result,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'connected': connection_result,
                    'uri': self.config.get('neo4j_uri', 'bolt://localhost:7687')
                }
            }
            phase_results['tests'].append(test_result)
            
            if not connection_result:
                self.logger.warning("Neo4j connection failed - skipping CKG operations")
                phase_results['success'] = False
                return phase_results
            
            # Test 1.6: AST to CKG Building
            self.logger.info("Test 1.6: CKG Construction")
            start_time = datetime.now()
            
            ckg_result = await self.components['ast_to_ckg'].build_ckg(parsed_entities)
            
            test_result = {
                'test_name': 'CKG Construction',
                'success': ckg_result,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'ckg_built': ckg_result,
                    'entities_processed': len(parsed_entities)
                }
            }
            phase_results['tests'].append(test_result)
            
            # Test 1.7: CKG Query Interface
            self.logger.info("Test 1.7: CKG Queries")
            start_time = datetime.now()
            
            # Test basic query
            query_result = await self.components['ckg_query'].find_circular_dependencies()
            
            test_result = {
                'test_name': 'CKG Queries',
                'success': query_result is not None,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'query_executed': query_result is not None,
                    'circular_deps_found': len(query_result) if query_result else 0
                }
            }
            phase_results['tests'].append(test_result)
            
            # Store parsed entities for next phases
            phase_results['parsed_entities'] = parsed_entities
            
        except Exception as e:
            self.logger.error(f"Phase 1 CKG operations testing failed: {e}")
            phase_results['success'] = False
            phase_results['error'] = str(e)
        
        phase_results['end_time'] = datetime.now().isoformat()
        return phase_results

    async def test_phase_2_code_analysis(self, project_context: ProjectDataContext) -> Dict[str, Any]:
        """
        Test Phase 2: Code Analysis functionality.
        
        Args:
            project_context: Project context from Phase 1
            
        Returns:
            Test results dictionary
        """
        self.logger.info("=== TESTING PHASE 2: CODE ANALYSIS ===")
        
        phase_results = {
            'phase': 'Phase 2 - Code Analysis',
            'tests': [],
            'success': True,
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Test 2.1: Architectural Analysis
            self.logger.info("Test 2.1: Architectural Analysis")
            start_time = datetime.now()
            
            arch_result = await self.components['arch_analyzer'].analyze_project_architecture(project_context)
            
            test_result = {
                'test_name': 'Architectural Analysis',
                'success': arch_result is not None,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'analysis_completed': arch_result is not None,
                    'findings_count': len(arch_result.findings) if arch_result else 0
                }
            }
            phase_results['tests'].append(test_result)
            
            # Test 2.2: PR Impact Analysis (with sample PR data)
            self.logger.info("Test 2.2: PR Impact Analysis")
            start_time = datetime.now()
            
            # Create sample PR diff info
            pr_diff = PRDiffInfo(
                pr_id="test-pr-123",
                pr_url="https://github.com/test/repo/pull/123",
                base_branch="main",
                head_branch="feature/test",
                raw_diff="sample diff content",
                changed_files=["src/main/java/TestFile.java"],
                file_changes={"src/main/java/TestFile.java": "modified"},
                function_changes=["testFunction"]
            )
            
            context_with_pr = ProjectDataContext(
                cloned_code_path=project_context.cloned_code_path,
                detected_languages=project_context.detected_languages,
                repository_url=project_context.repository_url,
                pr_diff_info=pr_diff
            )
            
            pr_result = await self.components['pr_impact'].analyze_pr_impact(context_with_pr)
            
            test_result = {
                'test_name': 'PR Impact Analysis',
                'success': pr_result is not None,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'analysis_completed': pr_result is not None,
                    'impact_findings': len(pr_result.findings) if pr_result else 0
                }
            }
            phase_results['tests'].append(test_result)
            
            # Test 2.3: Static Analysis Integration
            self.logger.info("Test 2.3: Static Analysis Integration")
            start_time = datetime.now()
            
            static_result = await self.components['static_analysis'].run_linter(
                project_context.cloned_code_path, ["python"]
            )
            
            test_result = {
                'test_name': 'Static Analysis Integration',
                'success': static_result is not None,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'linter_executed': static_result is not None,
                    'placeholder_working': True  # Since it's a placeholder
                }
            }
            phase_results['tests'].append(test_result)
            
            # Store analysis results
            phase_results['analysis_results'] = {
                'architectural': arch_result,
                'pr_impact': pr_result,
                'static_analysis': static_result
            }
            
        except Exception as e:
            self.logger.error(f"Phase 2 code analysis testing failed: {e}")
            phase_results['success'] = False
            phase_results['error'] = str(e)
        
        phase_results['end_time'] = datetime.now().isoformat()
        return phase_results

    async def test_phase_2_llm_services(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test Phase 2: LLM Services functionality.
        
        Args:
            analysis_results: Results from code analysis
            
        Returns:
            Test results dictionary
        """
        self.logger.info("=== TESTING PHASE 2: LLM SERVICES ===")
        
        phase_results = {
            'phase': 'Phase 2 - LLM Services',
            'tests': [],
            'success': True,
            'start_time': datetime.now().isoformat()
        }
        
        # Skip LLM tests if no API key
        if not self.config.get('openai_api_key'):
            self.logger.warning("No OpenAI API key found - skipping LLM tests")
            phase_results['success'] = False
            phase_results['error'] = "No OpenAI API key configured"
            return phase_results
        
        try:
            # Test 2.4: LLM Gateway
            self.logger.info("Test 2.4: LLM Gateway")
            start_time = datetime.now()
            
            # Create test LLM request
            from data_models.llm_models import LLMServiceRequest
            
            test_request = LLMServiceRequest(
                request_id="test-request-123",
                prompt="Analyze this code structure: public class Test { public void method() {} }",
                context={"language": "java", "purpose": "architecture_analysis"},
                max_tokens=100,
                temperature=0.1
            )
            
            gateway_result = await self.components['llm_gateway'].process_request(test_request)
            
            test_result = {
                'test_name': 'LLM Gateway',
                'success': gateway_result is not None,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'request_processed': gateway_result is not None,
                    'has_response': gateway_result.content is not None if gateway_result else False
                }
            }
            phase_results['tests'].append(test_result)
            
            # Test 2.5: Team LLM Services
            self.logger.info("Test 2.5: Team LLM Services")
            start_time = datetime.now()
            
            team_llm_result = await self.components['team_llm'].process_request(test_request)
            
            test_result = {
                'test_name': 'Team LLM Services',
                'success': team_llm_result is not None,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'team_service_working': team_llm_result is not None,
                    'response_content': team_llm_result.content[:100] if team_llm_result and team_llm_result.content else None
                }
            }
            phase_results['tests'].append(test_result)
            
            # Test 2.6: LLM Analysis Support
            self.logger.info("Test 2.6: LLM Analysis Support")
            start_time = datetime.now()
            
            if analysis_results.get('architectural'):
                enhanced_result = await self.components['llm_support'].enhance_analysis(
                    analysis_results['architectural']
                )
                
                test_result = {
                    'test_name': 'LLM Analysis Support',
                    'success': enhanced_result is not None,
                    'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                    'details': {
                        'enhancement_completed': enhanced_result is not None,
                        'enhanced_findings': len(enhanced_result.findings) if enhanced_result else 0
                    }
                }
            else:
                test_result = {
                    'test_name': 'LLM Analysis Support',
                    'success': False,
                    'duration_ms': 0,
                    'details': {'error': 'No architectural analysis results to enhance'}
                }
            
            phase_results['tests'].append(test_result)
            
        except Exception as e:
            self.logger.error(f"Phase 2 LLM services testing failed: {e}")
            phase_results['success'] = False
            phase_results['error'] = str(e)
        
        phase_results['end_time'] = datetime.now().isoformat()
        return phase_results

    async def test_phase_3_orchestrator(self, repo_url: str) -> Dict[str, Any]:
        """
        Test Phase 3: Orchestrator Integration.
        
        Args:
            repo_url: Repository URL for orchestration test
            
        Returns:
            Test results dictionary
        """
        self.logger.info("=== TESTING PHASE 3: ORCHESTRATOR INTEGRATION ===")
        
        phase_results = {
            'phase': 'Phase 3 - Orchestrator Integration',
            'tests': [],
            'success': True,
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Test 3.1: Task Definition Creation
            self.logger.info("Test 3.1: Task Definition")
            start_time = datetime.now()
            
            task_def = TaskDefinition(
                task_id="test-task-123",
                task_type="repository_analysis",
                repository_url=repo_url,
                user_id="test-user",
                llm_config={"model": "gpt-4", "temperature": 0.1},
                metadata={"test": True}
            )
            
            test_result = {
                'test_name': 'Task Definition Creation',
                'success': task_def is not None,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'task_created': task_def is not None,
                    'task_id': task_def.task_id if task_def else None
                }
            }
            phase_results['tests'].append(test_result)
            
            # Test 3.2: Orchestrator Execution
            self.logger.info("Test 3.2: Orchestrator Execution")
            start_time = datetime.now()
            
            # Execute task through orchestrator
            orchestrator_result = await self.components['orchestrator'].execute_task(task_def)
            
            test_result = {
                'test_name': 'Orchestrator Execution',
                'success': orchestrator_result is not None,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': {
                    'execution_completed': orchestrator_result is not None,
                    'has_results': len(orchestrator_result) > 0 if orchestrator_result else False
                }
            }
            phase_results['tests'].append(test_result)
            
            # Test 3.3: End-to-End Integration
            self.logger.info("Test 3.3: End-to-End Integration")
            start_time = datetime.now()
            
            # Test complete workflow through orchestrator
            integration_success = True
            integration_details = {}
            
            try:
                # This should orchestrate all phases
                full_result = await self.components['orchestrator'].execute_task(task_def)
                integration_details = {
                    'full_workflow_completed': full_result is not None,
                    'result_count': len(full_result) if full_result else 0
                }
            except Exception as e:
                integration_success = False
                integration_details = {'error': str(e)}
            
            test_result = {
                'test_name': 'End-to-End Integration',
                'success': integration_success,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'details': integration_details
            }
            phase_results['tests'].append(test_result)
            
        except Exception as e:
            self.logger.error(f"Phase 3 orchestrator testing failed: {e}")
            phase_results['success'] = False
            phase_results['error'] = str(e)
        
        phase_results['end_time'] = datetime.now().isoformat()
        return phase_results

    async def run_comprehensive_test(self, repo_url: str) -> Dict[str, Any]:
        """
        Run comprehensive test suite for all phases.
        
        Args:
            repo_url: Repository URL to test with
            
        Returns:
            Complete test results
        """
        self.logger.info(f"Starting comprehensive test with repository: {repo_url}")
        
        overall_results = {
            'test_suite': 'Comprehensive Phase 1-3 Testing',
            'start_time': datetime.now().isoformat(),
            'repo_url': repo_url,
            'config': {
                'has_openai_key': bool(self.config.get('openai_api_key')),
                'has_neo4j_config': bool(self.config.get('neo4j_uri')),
                'test_repo': repo_url
            },
            'phases': [],
            'summary': {}
        }
        
        try:
            # Phase 1: Data Acquisition
            phase1_data = await self.test_phase_1_data_acquisition(repo_url)
            overall_results['phases'].append(phase1_data)
            
            if not phase1_data['success']:
                self.logger.error("Phase 1 Data Acquisition failed - stopping tests")
                overall_results['summary']['status'] = 'Failed at Phase 1 Data Acquisition'
                return overall_results
            
            # Phase 1: CKG Operations (if we have project context)
            if 'project_context' in phase1_data:
                phase1_ckg = await self.test_phase_1_ckg_operations(phase1_data['project_context'])
                overall_results['phases'].append(phase1_ckg)
            
            # Phase 2: Code Analysis
            if 'project_context' in phase1_data:
                phase2_analysis = await self.test_phase_2_code_analysis(phase1_data['project_context'])
                overall_results['phases'].append(phase2_analysis)
                
                # Phase 2: LLM Services
                if 'analysis_results' in phase2_analysis:
                    phase2_llm = await self.test_phase_2_llm_services(phase2_analysis['analysis_results'])
                    overall_results['phases'].append(phase2_llm)
            
            # Phase 3: Orchestrator Integration
            phase3_results = await self.test_phase_3_orchestrator(repo_url)
            overall_results['phases'].append(phase3_results)
            
            # Generate summary
            total_tests = sum(len(phase.get('tests', [])) for phase in overall_results['phases'])
            successful_tests = sum(
                len([test for test in phase.get('tests', []) if test.get('success', False)])
                for phase in overall_results['phases']
            )
            
            overall_results['summary'] = {
                'total_phases': len(overall_results['phases']),
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                'overall_success': all(phase.get('success', False) for phase in overall_results['phases'])
            }
            
        except Exception as e:
            self.logger.error(f"Comprehensive test failed: {e}")
            overall_results['summary'] = {
                'status': 'Failed',
                'error': str(e)
            }
        
        overall_results['end_time'] = datetime.now().isoformat()
        return overall_results

    def save_test_results(self, results: Dict[str, Any], filename: Optional[str] = None):
        """Save test results to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_test_results_{timestamp}.json"
        
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / filename
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Test results saved to: {results_file}")
        return results_file

    def print_test_summary(self, results: Dict[str, Any]):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print("REPOCHAT PHASE 1-3 COMPREHENSIVE TEST RESULTS")
        print("="*80)
        
        summary = results.get('summary', {})
        print(f"Repository: {results.get('repo_url', 'Unknown')}")
        print(f"Total Phases: {summary.get('total_phases', 0)}")
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Successful Tests: {summary.get('successful_tests', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"Overall Success: {'✅ PASS' if summary.get('overall_success', False) else '❌ FAIL'}")
        
        print("\nPHASE BREAKDOWN:")
        for phase in results.get('phases', []):
            phase_name = phase.get('phase', 'Unknown Phase')
            phase_success = '✅' if phase.get('success', False) else '❌'
            test_count = len(phase.get('tests', []))
            
            print(f"  {phase_success} {phase_name} ({test_count} tests)")
            
            # Show individual test results
            for test in phase.get('tests', []):
                test_success = '✅' if test.get('success', False) else '❌'
                test_name = test.get('test_name', 'Unknown Test')
                duration = test.get('duration_ms', 0)
                print(f"    {test_success} {test_name} ({duration:.0f}ms)")
        
        print("\n" + "="*80)


def load_config_from_env() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    config = {}
    
    # Try to load from .env file
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    # Load OpenAI configuration
    config['openai_api_key'] = os.getenv('OPENAI_API_KEY')
    config['openai_org_id'] = os.getenv('OPENAI_ORG_ID')
    config['openai_model'] = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Load Neo4j configuration
    config['neo4j_uri'] = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    config['neo4j_username'] = os.getenv('NEO4J_USERNAME', 'neo4j')
    config['neo4j_password'] = os.getenv('NEO4J_PASSWORD', 'password')
    
    # Load Git configuration
    config['github_token'] = os.getenv('GITHUB_TOKEN')
    
    return config


async def main():
    """Main test execution function."""
    parser = argparse.ArgumentParser(description='RepoChat Phase 1-3 Comprehensive Testing')
    parser.add_argument('--repo-url', default='https://github.com/spring-projects/spring-petclinic.git',
                       help='Repository URL to test with')
    parser.add_argument('--openai-test', action='store_true',
                       help='Include OpenAI API tests (requires API key)')
    parser.add_argument('--output', help='Output file for test results')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config_from_env()
    
    # Validate required configuration
    if args.openai_test and not config.get('openai_api_key'):
        print("❌ OpenAI API key required for LLM tests. Set OPENAI_API_KEY in .env file.")
        return 1
    
    # Initialize test suite
    test_suite = ComprehensivePhase13TestSuite(config)
    
    try:
        # Run comprehensive tests
        results = await test_suite.run_comprehensive_test(args.repo_url)
        
        # Save results
        results_file = test_suite.save_test_results(results, args.output)
        
        # Print summary
        test_suite.print_test_summary(results)
        
        # Return appropriate exit code
        return 0 if results.get('summary', {}).get('overall_success', False) else 1
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 