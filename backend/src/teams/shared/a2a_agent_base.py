"""
RepoChat v1.0 - A2A Compatible Agent Base
Base class cho tất cả agents để support Google A2A Protocol communication.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum

try:
    # Try to import Google ADK if available
    from google_adk import A2AProtocol, AgentCapability, MessageType
    A2A_AVAILABLE = True
except ImportError:
    # Fallback mode without A2A Protocol
    A2A_AVAILABLE = False
    
    # Mock classes for graceful fallback
    class A2AProtocol:
        pass
    
    class AgentCapability:
        pass
        
    class MessageType:
        REQUEST = "request"
        RESPONSE = "response"
        NOTIFICATION = "notification"

from ...shared.utils.logging_config import get_logger

logger = get_logger(__name__)

class AgentStatus(Enum):
    """Agent operational status."""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class AgentMetadata:
    """Agent identification và capability metadata."""
    agent_id: str
    name: str
    version: str
    capabilities: List[str]
    status: AgentStatus
    created_at: datetime
    last_heartbeat: datetime
    load_factor: float  # 0.0 to 1.0

@dataclass
class A2AMessage:
    """Standard A2A Protocol message format."""
    message_id: str
    message_type: str
    sender_id: str
    receiver_id: str
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: Optional[int] = None  # Time to live in seconds

class A2AAgentBase(ABC):
    """
    Abstract base class cho tất cả RepoChat agents với A2A Protocol support.
    
    Features:
    - Google A2A Protocol integration với graceful fallback
    - Standard message format và routing
    - Health monitoring và load reporting
    - Service discovery và capability advertisement
    - Circuit breaker pattern for resilience
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize A2A compatible agent.
        
        Args:
            config: Agent configuration including A2A settings
        """
        self.config = config
        self.agent_id = config.get('agent_id', str(uuid.uuid4()))
        self.name = config.get('name', self.__class__.__name__)
        self.version = config.get('version', '1.0.0')
        
        # Agent metadata
        self.metadata = AgentMetadata(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            capabilities=self._get_capabilities(),
            status=AgentStatus.INITIALIZING,
            created_at=datetime.now(),
            last_heartbeat=datetime.now(),
            load_factor=0.0
        )
        
        # A2A Protocol setup
        self.a2a_enabled = config.get('a2a_enabled', A2A_AVAILABLE)
        self.a2a_protocol = None
        
        if self.a2a_enabled and A2A_AVAILABLE:
            try:
                self.a2a_protocol = A2AProtocol(
                    agent_id=self.agent_id,
                    capabilities=self._get_a2a_capabilities()
                )
                logger.info(f"Agent {self.name} initialized with A2A Protocol")
            except Exception as e:
                logger.warning(f"A2A Protocol initialization failed: {e}. Using fallback mode.")
                self.a2a_enabled = False
        else:
            logger.info(f"Agent {self.name} initialized in fallback mode (no A2A Protocol)")
        
        # Message handling
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        
        # Circuit breaker state
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = config.get('circuit_breaker_threshold', 5)
        self.circuit_breaker_open = False
        self.circuit_breaker_reset_time = None
        
        # Performance tracking
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_processing_time = 0.0
        
        # Setup message handlers
        self._setup_message_handlers()
        
        logger.info(f"A2A Agent {self.name} ({self.agent_id}) initialized")

    @abstractmethod
    def _get_capabilities(self) -> List[str]:
        """
        Return list of capabilities this agent provides.
        
        Returns:
            List of capability names
        """
        pass

    @abstractmethod
    async def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming request. Must be implemented by subclass.
        
        Args:
            request: Request data
            
        Returns:
            Response data
        """
        pass

    def _get_a2a_capabilities(self) -> List[AgentCapability]:
        """Convert string capabilities to A2A capability objects."""
        if not A2A_AVAILABLE:
            return []
            
        capabilities = []
        for capability_name in self._get_capabilities():
            try:
                capability = AgentCapability(
                    name=capability_name,
                    version="1.0.0",
                    description=f"{capability_name} capability provided by {self.name}"
                )
                capabilities.append(capability)
            except Exception as e:
                logger.warning(f"Failed to create A2A capability {capability_name}: {e}")
                
        return capabilities

    def _setup_message_handlers(self):
        """Setup standard message handlers."""
        self.message_handlers.update({
            'request': self._handle_request,
            'ping': self._handle_ping,
            'health_check': self._handle_health_check,
            'capability_query': self._handle_capability_query,
            'shutdown': self._handle_shutdown
        })

    async def start(self):
        """Start the agent and begin listening for messages."""
        try:
            self.metadata.status = AgentStatus.READY
            
            if self.a2a_enabled and self.a2a_protocol:
                # Register with A2A Protocol
                await self._register_with_a2a()
                
            # Start heartbeat
            asyncio.create_task(self._heartbeat_loop())
            
            logger.info(f"Agent {self.name} started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start agent {self.name}: {e}")
            self.metadata.status = AgentStatus.ERROR
            raise

    async def stop(self):
        """Stop the agent gracefully."""
        try:
            self.metadata.status = AgentStatus.OFFLINE
            
            if self.a2a_enabled and self.a2a_protocol:
                # Unregister from A2A Protocol
                await self._unregister_from_a2a()
                
            logger.info(f"Agent {self.name} stopped")
            
        except Exception as e:
            logger.error(f"Error stopping agent {self.name}: {e}")

    async def _register_with_a2a(self):
        """Register agent with A2A Protocol service discovery."""
        if not self.a2a_protocol:
            return
            
        try:
            await self.a2a_protocol.register_agent(
                self.metadata.agent_id,
                self.metadata.name,
                self._get_a2a_capabilities()
            )
            logger.info(f"Agent {self.name} registered with A2A Protocol")
        except Exception as e:
            logger.error(f"Failed to register with A2A Protocol: {e}")

    async def _unregister_from_a2a(self):
        """Unregister agent from A2A Protocol."""
        if not self.a2a_protocol:
            return
            
        try:
            await self.a2a_protocol.unregister_agent(self.metadata.agent_id)
            logger.info(f"Agent {self.name} unregistered from A2A Protocol")
        except Exception as e:
            logger.error(f"Failed to unregister from A2A Protocol: {e}")

    async def send_message(
        self, 
        receiver_id: str, 
        message_type: str, 
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Send message to another agent.
        
        Args:
            receiver_id: Target agent ID
            message_type: Type of message
            payload: Message payload
            correlation_id: Optional correlation ID for request tracking
            timeout: Timeout in seconds
            
        Returns:
            Response if expecting reply, None otherwise
        """
        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            payload=payload,
            timestamp=datetime.now(),
            correlation_id=correlation_id,
            ttl=timeout
        )
        
        try:
            if self.a2a_enabled and self.a2a_protocol:
                # Use A2A Protocol
                response = await self._send_via_a2a(message, timeout)
            else:
                # Use fallback mechanism
                response = await self._send_via_fallback(message, timeout)
                
            return response
            
        except Exception as e:
            logger.error(f"Failed to send message to {receiver_id}: {e}")
            self._record_failure()
            return None

    async def _send_via_a2a(self, message: A2AMessage, timeout: int) -> Optional[Dict[str, Any]]:
        """Send message using A2A Protocol."""
        try:
            response = await self.a2a_protocol.send_message(
                message.receiver_id,
                message.message_type,
                message.payload,
                timeout=timeout
            )
            
            self._record_success()
            return response
            
        except Exception as e:
            logger.error(f"A2A Protocol send failed: {e}")
            self._record_failure()
            raise

    async def _send_via_fallback(self, message: A2AMessage, timeout: int) -> Optional[Dict[str, Any]]:
        """Send message using fallback mechanism (direct agent communication)."""
        # For now, this is a placeholder. In real implementation,
        # this would use REST API, message queue, or other transport
        logger.debug(f"Sending message via fallback: {message.message_type} to {message.receiver_id}")
        
        # Simulate successful delivery for testing
        await asyncio.sleep(0.1)  # Simulate network delay
        
        return {
            'success': True,
            'message': f'Fallback delivery to {message.receiver_id}',
            'timestamp': datetime.now().isoformat()
        }

    async def receive_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """
        Handle incoming message.
        
        Args:
            message: Incoming A2A message
            
        Returns:
            Response if required
        """
        start_time = datetime.now()
        
        try:
            # Check circuit breaker
            if self._is_circuit_breaker_open():
                logger.warning(f"Circuit breaker open, rejecting message {message.message_id}")
                return {
                    'success': False,
                    'error': 'Circuit breaker open',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Update heartbeat
            self.metadata.last_heartbeat = datetime.now()
            self.metadata.status = AgentStatus.BUSY
            
            # Dispatch to appropriate handler
            handler = self.message_handlers.get(message.message_type)
            if handler:
                response = await handler(message)
            else:
                response = await self._handle_unknown_message(message)
                
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._record_request(processing_time, success=True)
            
            self.metadata.status = AgentStatus.READY
            return response
            
        except Exception as e:
            logger.error(f"Error processing message {message.message_id}: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            self._record_request(processing_time, success=False)
            self.metadata.status = AgentStatus.ERROR
            
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def _handle_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle general request message."""
        try:
            result = await self._process_request(message.payload)
            return {
                'success': True,
                'result': result,
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }

    async def _handle_ping(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle ping message."""
        return {
            'success': True,
            'agent_id': self.agent_id,
            'status': self.metadata.status.value,
            'timestamp': datetime.now().isoformat()
        }

    async def _handle_health_check(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle health check message."""
        return {
            'success': True,
            'agent_id': self.agent_id,
            'metadata': asdict(self.metadata),
            'metrics': self._get_performance_metrics(),
            'timestamp': datetime.now().isoformat()
        }

    async def _handle_capability_query(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle capability query message."""
        return {
            'success': True,
            'agent_id': self.agent_id,
            'capabilities': self._get_capabilities(),
            'timestamp': datetime.now().isoformat()
        }

    async def _handle_shutdown(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle shutdown message."""
        asyncio.create_task(self.stop())
        return {
            'success': True,
            'message': 'Shutdown initiated',
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat()
        }

    async def _handle_unknown_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle unknown message type."""
        logger.warning(f"Unknown message type: {message.message_type}")
        return {
            'success': False,
            'error': f'Unknown message type: {message.message_type}',
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat()
        }

    async def _heartbeat_loop(self):
        """Send periodic heartbeat to maintain agent registry."""
        while self.metadata.status != AgentStatus.OFFLINE:
            try:
                self.metadata.last_heartbeat = datetime.now()
                
                # Update load factor based on current activity
                self._update_load_factor()
                
                # Send heartbeat if A2A enabled
                if self.a2a_enabled and self.a2a_protocol:
                    await self.a2a_protocol.send_heartbeat(
                        self.agent_id,
                        {
                            'status': self.metadata.status.value,
                            'load_factor': self.metadata.load_factor,
                            'timestamp': datetime.now().isoformat()
                        }
                    )
                
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(60)  # Longer delay on error

    def _update_load_factor(self):
        """Update current load factor based on activity."""
        # Simple load calculation based on recent activity
        if self.metadata.status == AgentStatus.BUSY:
            self.metadata.load_factor = min(1.0, self.metadata.load_factor + 0.1)
        else:
            self.metadata.load_factor = max(0.0, self.metadata.load_factor - 0.05)

    def _record_request(self, processing_time: float, success: bool):
        """Record request metrics."""
        self.request_count += 1
        self.total_processing_time += processing_time
        
        if success:
            self.success_count += 1
            self._record_success()
        else:
            self.error_count += 1
            self._record_failure()

    def _record_success(self):
        """Record successful operation."""
        if self.circuit_breaker_failures > 0:
            self.circuit_breaker_failures = max(0, self.circuit_breaker_failures - 1)
            
        if self.circuit_breaker_open and self.circuit_breaker_failures == 0:
            self.circuit_breaker_open = False
            self.circuit_breaker_reset_time = None
            logger.info(f"Circuit breaker closed for agent {self.name}")

    def _record_failure(self):
        """Record failed operation."""
        self.circuit_breaker_failures += 1
        
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            if not self.circuit_breaker_open:
                self.circuit_breaker_open = True
                self.circuit_breaker_reset_time = datetime.now()
                logger.warning(f"Circuit breaker opened for agent {self.name}")

    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is currently open."""
        if not self.circuit_breaker_open:
            return False
            
        # Auto-reset after 5 minutes
        if (self.circuit_breaker_reset_time and 
            (datetime.now() - self.circuit_breaker_reset_time).total_seconds() > 300):
            self.circuit_breaker_open = False
            self.circuit_breaker_reset_time = None
            self.circuit_breaker_failures = 0
            logger.info(f"Circuit breaker auto-reset for agent {self.name}")
            return False
            
        return True

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if self.request_count > 0:
            success_rate = self.success_count / self.request_count
            avg_processing_time = self.total_processing_time / self.request_count
        else:
            success_rate = 1.0
            avg_processing_time = 0.0
            
        return {
            'request_count': self.request_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': success_rate,
            'average_processing_time': avg_processing_time,
            'load_factor': self.metadata.load_factor,
            'circuit_breaker_open': self.circuit_breaker_open,
            'uptime_seconds': (datetime.now() - self.metadata.created_at).total_seconds()
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            'metadata': asdict(self.metadata),
            'performance': self._get_performance_metrics(),
            'a2a_enabled': self.a2a_enabled,
            'capabilities': self._get_capabilities()
        } 