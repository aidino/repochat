"""
RepoChat v1.0 - Migration Manager
Gradual rollout của EnhancedOrchestratorAgent từ current system.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from .enhanced_orchestrator_agent import EnhancedOrchestratorAgent
from .orchestrator_agent import OrchestratorAgent
from ..shared.utils.logging_config import get_logger

logger = get_logger(__name__)

class MigrationPhase(Enum):
    """Migration phases theo plan."""
    PHASE_0_BASELINE = "baseline"           # Current system only
    PHASE_1_CANARY = "canary"               # 10% traffic to enhanced
    PHASE_2_PARTIAL = "partial"             # 50% traffic to enhanced  
    PHASE_3_MAJORITY = "majority"           # 90% traffic to enhanced
    PHASE_4_COMPLETE = "complete"           # 100% enhanced system

class MigrationManager:
    """
    Manages gradual migration from OrchestratorAgent to EnhancedOrchestratorAgent.
    
    Features:
    - Traffic splitting với configurable percentage
    - Performance monitoring và rollback capability
    - Circuit breaker pattern for safety
    - Metrics collection for comparison
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Migration Manager.
        
        Args:
            config: Migration configuration including phases, thresholds
        """
        self.config = config
        self.current_phase = MigrationPhase.PHASE_0_BASELINE
        self.start_time = datetime.now()
        
        # Initialize both orchestrators
        self.legacy_orchestrator = OrchestratorAgent(config.get('legacy_config', {}))
        self.enhanced_orchestrator = EnhancedOrchestratorAgent(config.get('enhanced_config', {}))
        
        # Migration state
        self.migration_enabled = config.get('migration_enabled', False)
        self.enhanced_traffic_percentage = 0
        self.success_threshold = config.get('success_threshold', 0.95)
        self.performance_threshold = config.get('performance_threshold', 2.0)  # 2x slower max
        
        # Metrics tracking
        self.metrics = {
            'legacy': {'requests': 0, 'successes': 0, 'failures': 0, 'total_time': 0},
            'enhanced': {'requests': 0, 'successes': 0, 'failures': 0, 'total_time': 0}
        }
        
        # Circuit breaker state
        self.circuit_breaker_open = False
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = config.get('circuit_breaker_threshold', 5)
        
        logger.info(f"MigrationManager initialized - Phase: {self.current_phase.value}")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process request through appropriate orchestrator based on migration phase.
        
        Args:
            request_data: Request to process
            
        Returns:
            Processing result with metadata
        """
        start_time = datetime.now()
        
        try:
            # Determine which orchestrator to use
            use_enhanced = self._should_use_enhanced()
            
            if use_enhanced and not self.circuit_breaker_open:
                logger.debug("Routing to EnhancedOrchestratorAgent")
                result = await self._process_with_enhanced(request_data, start_time)
            else:
                logger.debug("Routing to Legacy OrchestratorAgent")
                result = await self._process_with_legacy(request_data, start_time)
                
            return result
            
        except Exception as e:
            logger.error(f"Migration processing error: {e}")
            # Fallback to legacy on any error
            return await self._process_with_legacy(request_data, start_time)

    async def _process_with_enhanced(self, request_data: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """Process request with EnhancedOrchestratorAgent."""
        try:
            result = await self.enhanced_orchestrator.execute_workflow(request_data)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Record metrics
            self.metrics['enhanced']['requests'] += 1
            self.metrics['enhanced']['total_time'] += duration
            
            if result.get('success', False):
                self.metrics['enhanced']['successes'] += 1
                self._reset_circuit_breaker()
            else:
                self.metrics['enhanced']['failures'] += 1
                self._handle_enhanced_failure()
                
            result['orchestrator_used'] = 'enhanced'
            result['duration'] = duration
            return result
            
        except Exception as e:
            logger.error(f"Enhanced orchestrator error: {e}")
            self.metrics['enhanced']['failures'] += 1
            self._handle_enhanced_failure()
            
            # Fallback to legacy
            return await self._process_with_legacy(request_data, start_time)

    async def _process_with_legacy(self, request_data: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """Process request with Legacy OrchestratorAgent."""
        try:
            result = await self.legacy_orchestrator.execute_workflow(request_data)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Record metrics  
            self.metrics['legacy']['requests'] += 1
            self.metrics['legacy']['total_time'] += duration
            
            if result.get('success', False):
                self.metrics['legacy']['successes'] += 1
            else:
                self.metrics['legacy']['failures'] += 1
                
            result['orchestrator_used'] = 'legacy'
            result['duration'] = duration
            return result
            
        except Exception as e:
            logger.error(f"Legacy orchestrator error: {e}")
            self.metrics['legacy']['failures'] += 1
            raise

    def _should_use_enhanced(self) -> bool:
        """Determine if request should use enhanced orchestrator."""
        if not self.migration_enabled:
            return False
            
        if self.current_phase == MigrationPhase.PHASE_0_BASELINE:
            return False
        elif self.current_phase == MigrationPhase.PHASE_4_COMPLETE:
            return True
            
        # Traffic splitting based on phase
        import random
        return random.random() < self.enhanced_traffic_percentage / 100

    def _handle_enhanced_failure(self):
        """Handle failure in enhanced orchestrator."""
        self.circuit_breaker_failures += 1
        
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            self.circuit_breaker_open = True
            logger.warning(f"Circuit breaker OPENED - Enhanced orchestrator failures: {self.circuit_breaker_failures}")

    def _reset_circuit_breaker(self):
        """Reset circuit breaker on success."""
        if self.circuit_breaker_failures > 0:
            self.circuit_breaker_failures = max(0, self.circuit_breaker_failures - 1)
            
        if self.circuit_breaker_open and self.circuit_breaker_failures == 0:
            self.circuit_breaker_open = False
            logger.info("Circuit breaker CLOSED - Enhanced orchestrator recovered")

    async def advance_migration_phase(self) -> bool:
        """
        Advance to next migration phase if conditions are met.
        
        Returns:
            True if phase advanced, False otherwise
        """
        if not self.migration_enabled:
            return False
            
        current_metrics = self.get_current_metrics()
        
        if not self._can_advance_phase(current_metrics):
            logger.info(f"Cannot advance from phase {self.current_phase.value} - metrics don't meet threshold")
            return False
            
        # Advance to next phase
        next_phase = self._get_next_phase()
        if next_phase:
            self.current_phase = next_phase
            self._update_traffic_percentage()
            logger.info(f"Advanced to migration phase: {self.current_phase.value} (Traffic: {self.enhanced_traffic_percentage}%)")
            return True
            
        return False

    def _can_advance_phase(self, metrics: Dict[str, Any]) -> bool:
        """Check if metrics allow advancing to next phase."""
        enhanced_metrics = metrics.get('enhanced', {})
        
        if enhanced_metrics.get('requests', 0) < 10:  # Need minimum sample size
            return False
            
        success_rate = enhanced_metrics.get('success_rate', 0)
        performance_ratio = enhanced_metrics.get('performance_ratio', float('inf'))
        
        return (success_rate >= self.success_threshold and 
                performance_ratio <= self.performance_threshold)

    def _get_next_phase(self) -> Optional[MigrationPhase]:
        """Get next migration phase."""
        phase_order = [
            MigrationPhase.PHASE_0_BASELINE,
            MigrationPhase.PHASE_1_CANARY,
            MigrationPhase.PHASE_2_PARTIAL,
            MigrationPhase.PHASE_3_MAJORITY,
            MigrationPhase.PHASE_4_COMPLETE
        ]
        
        try:
            current_index = phase_order.index(self.current_phase)
            if current_index < len(phase_order) - 1:
                return phase_order[current_index + 1]
        except ValueError:
            pass
            
        return None

    def _update_traffic_percentage(self):
        """Update traffic percentage based on current phase."""
        phase_percentages = {
            MigrationPhase.PHASE_0_BASELINE: 0,
            MigrationPhase.PHASE_1_CANARY: 10,
            MigrationPhase.PHASE_2_PARTIAL: 50,
            MigrationPhase.PHASE_3_MAJORITY: 90,
            MigrationPhase.PHASE_4_COMPLETE: 100
        }
        
        self.enhanced_traffic_percentage = phase_percentages.get(self.current_phase, 0)

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics for both orchestrators."""
        result = {
            'phase': self.current_phase.value,
            'enhanced_traffic_percentage': self.enhanced_traffic_percentage,
            'circuit_breaker_open': self.circuit_breaker_open,
            'migration_duration': (datetime.now() - self.start_time).total_seconds()
        }
        
        for orchestrator_type in ['legacy', 'enhanced']:
            metrics = self.metrics[orchestrator_type]
            requests = metrics['requests']
            
            if requests > 0:
                avg_time = metrics['total_time'] / requests
                success_rate = metrics['successes'] / requests
            else:
                avg_time = 0
                success_rate = 0
                
            result[orchestrator_type] = {
                'requests': requests,
                'successes': metrics['successes'],
                'failures': metrics['failures'],
                'success_rate': success_rate,
                'average_time': avg_time
            }
            
        # Calculate performance ratio
        legacy_time = result['legacy'].get('average_time', 1)
        enhanced_time = result['enhanced'].get('average_time', 1)
        
        if legacy_time > 0:
            result['enhanced']['performance_ratio'] = enhanced_time / legacy_time
        else:
            result['enhanced']['performance_ratio'] = 1.0
            
        return result

    async def rollback_migration(self) -> bool:
        """
        Rollback migration to previous phase or disable enhanced orchestrator.
        
        Returns:
            True if rollback successful
        """
        if self.current_phase == MigrationPhase.PHASE_0_BASELINE:
            logger.warning("Already at baseline phase, cannot rollback further")
            return False
            
        # Move back one phase
        phase_order = [
            MigrationPhase.PHASE_0_BASELINE,
            MigrationPhase.PHASE_1_CANARY,
            MigrationPhase.PHASE_2_PARTIAL,
            MigrationPhase.PHASE_3_MAJORITY,
            MigrationPhase.PHASE_4_COMPLETE
        ]
        
        try:
            current_index = phase_order.index(self.current_phase)
            if current_index > 0:
                self.current_phase = phase_order[current_index - 1]
                self._update_traffic_percentage()
                
                # Reset circuit breaker
                self.circuit_breaker_open = False
                self.circuit_breaker_failures = 0
                
                logger.warning(f"Migration ROLLED BACK to phase: {self.current_phase.value}")
                return True
                
        except ValueError:
            pass
            
        return False

    def enable_migration(self):
        """Enable migration process."""
        self.migration_enabled = True
        logger.info("Migration process ENABLED")

    def disable_migration(self):
        """Disable migration process."""
        self.migration_enabled = False
        self.current_phase = MigrationPhase.PHASE_0_BASELINE
        self.enhanced_traffic_percentage = 0
        logger.info("Migration process DISABLED") 