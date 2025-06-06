"""
RepoChat v1.0 - Migration Testing Script
Test và validate migration process từ legacy sang enhanced orchestrator.
"""

import asyncio
import json
import time
from typing import Dict, Any, List
from datetime import datetime

from .migration_manager import MigrationManager, MigrationPhase
from .monitoring_dashboard import MonitoringDashboard
from ..shared.utils.logging_config import get_logger

logger = get_logger(__name__)

class MigrationTester:
    """
    Comprehensive testing suite cho migration process.
    
    Features:
    - Load testing với different request patterns
    - Failure simulation và recovery testing
    - Performance comparison between systems
    - Automated phase advancement testing
    """
    
    def __init__(self):
        """Initialize migration tester."""
        self.config = {
            'migration_enabled': True,
            'success_threshold': 0.95,
            'performance_threshold': 2.0,
            'circuit_breaker_threshold': 3,
            'legacy_config': {},
            'enhanced_config': {}
        }
        
        self.migration_manager = MigrationManager(self.config)
        self.dashboard = MonitoringDashboard(self.migration_manager)
        
        # Test results storage
        self.test_results = []

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """
        Run complete migration test suite.
        
        Returns:
            Test results summary
        """
        logger.info("🚀 Starting comprehensive migration tests")
        
        results = {
            'start_time': datetime.now(),
            'tests': {},
            'overall_success': True
        }
        
        try:
            # Test 1: Basic functionality test
            logger.info("📋 Test 1: Basic functionality")
            results['tests']['basic_functionality'] = await self._test_basic_functionality()
            
            # Test 2: Load testing
            logger.info("⚡ Test 2: Load testing")
            results['tests']['load_testing'] = await self._test_load_performance()
            
            # Test 3: Phase advancement
            logger.info("📈 Test 3: Phase advancement")
            results['tests']['phase_advancement'] = await self._test_phase_advancement()
            
            # Test 4: Circuit breaker
            logger.info("🔧 Test 4: Circuit breaker")
            results['tests']['circuit_breaker'] = await self._test_circuit_breaker()
            
            # Test 5: Rollback mechanism
            logger.info("⏪ Test 5: Rollback mechanism")
            results['tests']['rollback'] = await self._test_rollback_mechanism()
            
            # Calculate overall success
            results['overall_success'] = all(
                test.get('success', False) for test in results['tests'].values()
            )
            
        except Exception as e:
            logger.error(f"Test suite error: {e}")
            results['overall_success'] = False
            results['error'] = str(e)
            
        finally:
            results['end_time'] = datetime.now()
            results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
            
        # Log final results
        if results['overall_success']:
            logger.info("✅ All migration tests PASSED")
        else:
            logger.error("❌ Some migration tests FAILED")
            
        return results

    async def _test_basic_functionality(self) -> Dict[str, Any]:
        """Test basic request processing functionality."""
        test_requests = [
            {
                'type': 'scan_repository',
                'repository_url': 'https://github.com/test/repo1',
                'language': 'python'
            },
            {
                'type': 'analyze_pr',
                'pr_url': 'https://github.com/test/repo1/pull/123',
                'language': 'java'
            },
            {
                'type': 'generate_report',
                'scan_id': 'test-scan-001'
            }
        ]
        
        results = {
            'success': True,
            'processed': 0,
            'errors': []
        }
        
        for i, request in enumerate(test_requests):
            try:
                logger.debug(f"Processing test request {i+1}/{len(test_requests)}")
                result = await self.migration_manager.process_request(request)
                
                if result.get('success', False):
                    results['processed'] += 1
                else:
                    results['errors'].append(f"Request {i+1} failed: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                results['errors'].append(f"Request {i+1} exception: {str(e)}")
                results['success'] = False
                
        results['success'] = results['processed'] == len(test_requests)
        logger.info(f"Basic functionality: {results['processed']}/{len(test_requests)} requests successful")
        
        return results

    async def _test_load_performance(self) -> Dict[str, Any]:
        """Test system performance under load."""
        concurrent_requests = 20
        requests_per_batch = 5
        
        results = {
            'success': True,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'peak_response_time': 0,
            'errors': []
        }
        
        async def process_batch():
            """Process a batch of concurrent requests."""
            tasks = []
            batch_start = time.time()
            
            for i in range(requests_per_batch):
                request = {
                    'type': 'scan_repository',
                    'repository_url': f'https://github.com/test/repo{i}',
                    'language': 'python',
                    'batch_id': f'load_test_{int(batch_start)}_{i}'
                }
                task = asyncio.create_task(self.migration_manager.process_request(request))
                tasks.append(task)
                
            # Wait for all requests in batch
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            batch_end = time.time()
            batch_duration = batch_end - batch_start
            
            return batch_results, batch_duration
            
        # Run multiple batches
        total_time = 0
        response_times = []
        
        for batch_num in range(concurrent_requests // requests_per_batch):
            logger.debug(f"Running load test batch {batch_num + 1}")
            
            batch_results, batch_duration = await process_batch()
            total_time += batch_duration
            response_times.append(batch_duration)
            
            results['total_requests'] += len(batch_results)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results['failed_requests'] += 1
                    results['errors'].append(str(result))
                elif result.get('success', False):
                    results['successful_requests'] += 1
                else:
                    results['failed_requests'] += 1
                    results['errors'].append(result.get('error', 'Unknown error'))
                    
            # Small delay between batches
            await asyncio.sleep(0.1)
            
        # Calculate performance metrics
        if response_times:
            results['average_response_time'] = sum(response_times) / len(response_times)
            results['peak_response_time'] = max(response_times)
            
        success_rate = results['successful_requests'] / results['total_requests'] if results['total_requests'] > 0 else 0
        results['success'] = success_rate >= 0.9  # 90% success rate threshold
        
        logger.info(f"Load test: {results['successful_requests']}/{results['total_requests']} successful "
                   f"(Success rate: {success_rate:.1%})")
                   
        return results

    async def _test_phase_advancement(self) -> Dict[str, Any]:
        """Test automatic phase advancement logic."""
        results = {
            'success': True,
            'phases_advanced': 0,
            'final_phase': None,
            'errors': []
        }
        
        # Enable migration
        self.migration_manager.enable_migration()
        initial_phase = self.migration_manager.current_phase
        
        # Simulate successful requests to trigger advancement
        success_requests = 15  # More than minimum required
        
        for i in range(success_requests):
            try:
                # Create request that will likely succeed
                request = {
                    'type': 'simple_analysis',
                    'data': f'test_data_{i}',
                    'phase_test': True
                }
                
                result = await self.migration_manager.process_request(request)
                
                # Try to advance phase after some requests
                if i > 10 and i % 5 == 0:
                    advanced = await self.migration_manager.advance_migration_phase()
                    if advanced:
                        results['phases_advanced'] += 1
                        logger.info(f"Advanced to phase: {self.migration_manager.current_phase.value}")
                        
            except Exception as e:
                results['errors'].append(f"Phase advancement test error: {str(e)}")
                
        results['final_phase'] = self.migration_manager.current_phase.value
        results['success'] = results['phases_advanced'] > 0
        
        logger.info(f"Phase advancement: Advanced {results['phases_advanced']} phases "
                   f"(Final: {results['final_phase']})")
                   
        return results

    async def _test_circuit_breaker(self) -> Dict[str, Any]:
        """Test circuit breaker functionality."""
        results = {
            'success': True,
            'circuit_breaker_triggered': False,
            'recovery_successful': False,
            'errors': []
        }
        
        # Force enhanced orchestrator to fail by simulating errors
        original_threshold = self.migration_manager.circuit_breaker_threshold
        self.migration_manager.circuit_breaker_threshold = 3  # Lower threshold for testing
        
        try:
            # Send requests that will trigger failures
            for i in range(5):
                request = {
                    'type': 'force_failure',  # This should trigger enhanced orchestrator errors
                    'test_id': f'circuit_breaker_{i}'
                }
                
                result = await self.migration_manager.process_request(request)
                
                # Check if circuit breaker is triggered
                if self.migration_manager.circuit_breaker_open:
                    results['circuit_breaker_triggered'] = True
                    logger.info("Circuit breaker triggered successfully")
                    break
                    
            # Test recovery - send some successful requests
            if results['circuit_breaker_triggered']:
                await asyncio.sleep(1)  # Brief delay
                
                # Send successful requests to test recovery
                for i in range(3):
                    request = {
                        'type': 'simple_success',
                        'test_id': f'recovery_{i}'
                    }
                    
                    await self.migration_manager.process_request(request)
                    
                # Check if circuit breaker recovered
                if not self.migration_manager.circuit_breaker_open:
                    results['recovery_successful'] = True
                    logger.info("Circuit breaker recovery successful")
                    
        except Exception as e:
            results['errors'].append(f"Circuit breaker test error: {str(e)}")
            results['success'] = False
            
        finally:
            # Restore original threshold
            self.migration_manager.circuit_breaker_threshold = original_threshold
            
        results['success'] = results['circuit_breaker_triggered']  # At minimum, breaker should trigger
        
        logger.info(f"Circuit breaker test: Triggered={results['circuit_breaker_triggered']}, "
                   f"Recovered={results['recovery_successful']}")
                   
        return results

    async def _test_rollback_mechanism(self) -> Dict[str, Any]:
        """Test migration rollback functionality."""
        results = {
            'success': True,
            'rollback_successful': False,
            'final_phase': None,
            'errors': []
        }
        
        # Record initial phase
        initial_phase = self.migration_manager.current_phase
        
        try:
            # Try to advance to a higher phase first
            await self.migration_manager.advance_migration_phase()
            advanced_phase = self.migration_manager.current_phase
            
            # Now test rollback
            rollback_success = await self.migration_manager.rollback_migration()
            final_phase = self.migration_manager.current_phase
            
            results['rollback_successful'] = rollback_success
            results['final_phase'] = final_phase.value
            results['success'] = rollback_success
            
            logger.info(f"Rollback test: {initial_phase.value} -> {advanced_phase.value} -> {final_phase.value}")
            
        except Exception as e:
            results['errors'].append(f"Rollback test error: {str(e)}")
            results['success'] = False
            
        return results

    async def generate_test_report(self, results: Dict[str, Any]) -> str:
        """
        Generate detailed test report.
        
        Args:
            results: Test results from run_comprehensive_tests()
            
        Returns:
            Formatted test report
        """
        report = []
        report.append("=" * 80)
        report.append("REPOCHAT MIGRATION TEST REPORT")
        report.append("=" * 80)
        
        # Overview
        status = "✅ PASSED" if results['overall_success'] else "❌ FAILED"
        report.append(f"Overall Status: {status}")
        report.append(f"Test Duration: {results['duration']:.2f} seconds")
        report.append(f"Start Time: {results['start_time']}")
        report.append(f"End Time: {results['end_time']}")
        report.append("")
        
        # Individual test results
        report.append("INDIVIDUAL TEST RESULTS:")
        report.append("-" * 40)
        
        for test_name, test_result in results['tests'].items():
            status = "✅ PASSED" if test_result.get('success', False) else "❌ FAILED"
            report.append(f"{test_name.replace('_', ' ').title()}: {status}")
            
            # Add specific metrics if available
            if 'processed' in test_result:
                report.append(f"  - Requests processed: {test_result['processed']}")
            if 'successful_requests' in test_result:
                report.append(f"  - Successful requests: {test_result['successful_requests']}")
                report.append(f"  - Failed requests: {test_result['failed_requests']}")
            if 'average_response_time' in test_result:
                report.append(f"  - Average response time: {test_result['average_response_time']:.3f}s")
            if 'phases_advanced' in test_result:
                report.append(f"  - Phases advanced: {test_result['phases_advanced']}")
            if 'circuit_breaker_triggered' in test_result:
                report.append(f"  - Circuit breaker triggered: {test_result['circuit_breaker_triggered']}")
            if 'rollback_successful' in test_result:
                report.append(f"  - Rollback successful: {test_result['rollback_successful']}")
                
            # Show errors if any
            if test_result.get('errors'):
                report.append(f"  - Errors: {len(test_result['errors'])}")
                for error in test_result['errors'][:3]:  # Show first 3 errors
                    report.append(f"    * {error}")
                if len(test_result['errors']) > 3:
                    report.append(f"    * ... and {len(test_result['errors']) - 3} more")
                    
            report.append("")
            
        # Current system state
        metrics = self.migration_manager.get_current_metrics()
        report.append("CURRENT SYSTEM STATE:")
        report.append("-" * 40)
        report.append(f"Migration Phase: {metrics['phase']}")
        report.append(f"Enhanced Traffic: {metrics['enhanced_traffic_percentage']}%")
        report.append(f"Circuit Breaker: {'OPEN' if metrics['circuit_breaker_open'] else 'CLOSED'}")
        
        if metrics['legacy']['requests'] > 0:
            report.append(f"Legacy Success Rate: {metrics['legacy']['success_rate']:.1%}")
            report.append(f"Legacy Avg Time: {metrics['legacy']['average_time']:.3f}s")
            
        if metrics['enhanced']['requests'] > 0:
            report.append(f"Enhanced Success Rate: {metrics['enhanced']['success_rate']:.1%}")
            report.append(f"Enhanced Avg Time: {metrics['enhanced']['average_time']:.3f}s")
            report.append(f"Performance Ratio: {metrics['enhanced']['performance_ratio']:.2f}x")
            
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

async def main():
    """Main test execution function."""
    tester = MigrationTester()
    
    logger.info("🧪 Starting RepoChat Migration Test Suite")
    
    # Run comprehensive tests
    results = await tester.run_comprehensive_tests()
    
    # Generate and display report
    report = await tester.generate_test_report(results)
    print(report)
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"migration_test_report_{timestamp}.txt"
    
    with open(report_file, 'w') as f:
        f.write(report)
        
    logger.info(f"📄 Test report saved to: {report_file}")
    
    # Return exit code based on results
    return 0 if results['overall_success'] else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main()) 