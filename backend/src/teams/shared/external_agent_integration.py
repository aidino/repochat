"""
RepoChat v1.0 - External Agent Integration System
Support integration của external agents như CrewAI, AutoGen, custom agents.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Union, Protocol
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
import importlib
import inspect

from .a2a_agent_base import A2AAgentBase, A2AMessage, AgentStatus
from ...shared.utils.logging_config import get_logger

logger = get_logger(__name__)

class ExternalAgentType(Enum):
    """Supported external agent types."""
    CREWAI = "crewai"
    AUTOGEN = "autogen"
    LANGCHAIN = "langchain"
    CUSTOM = "custom"
    A2A_NATIVE = "a2a_native"

@dataclass
class AgentCapability:
    """Agent capability definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    version: str = "1.0.0"
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass 
class ExternalAgentManifest:
    """External agent manifest for registration."""
    agent_id: str
    name: str
    agent_type: ExternalAgentType
    version: str
    description: str
    capabilities: List[AgentCapability]
    endpoint: Optional[str] = None
    config_schema: Optional[Dict[str, Any]] = None
    dependencies: List[str] = None
    author: str = "Unknown"
    license: str = "MIT"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []

class ExternalAgentInterface(Protocol):
    """Protocol interface for external agents."""
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task and return result."""
        ...
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get agent capabilities."""
        ...
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        ...

class CrewAIAgentAdapter:
    """Adapter for CrewAI agents."""
    
    def __init__(self, crew_config: Dict[str, Any]):
        """Initialize CrewAI adapter."""
        self.config = crew_config
        self.crew = None
        self._initialize_crew()
        
    def _initialize_crew(self):
        """Initialize CrewAI crew."""
        try:
            # Try to import CrewAI
            from crewai import Crew, Agent, Task
            
            # Create agents from config
            agents = []
            for agent_config in self.config.get('agents', []):
                agent = Agent(
                    role=agent_config.get('role', 'Assistant'),
                    goal=agent_config.get('goal', 'Help with tasks'),
                    backstory=agent_config.get('backstory', 'Helpful assistant'),
                    verbose=agent_config.get('verbose', True)
                )
                agents.append(agent)
            
            # Create crew
            self.crew = Crew(
                agents=agents,
                verbose=self.config.get('verbose', True)
            )
            
            logger.info(f"CrewAI crew initialized with {len(agents)} agents")
            
        except ImportError:
            logger.warning("CrewAI not available. Using mock implementation.")
            self.crew = None
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using CrewAI crew."""
        if self.crew is None:
            return {
                'success': False,
                'error': 'CrewAI not available',
                'mock_result': f"Mock CrewAI execution for: {task.get('description', 'unknown task')}"
            }
        
        try:
            # Create CrewAI task
            from crewai import Task as CrewTask
            
            crew_task = CrewTask(
                description=task.get('description', 'Execute task'),
                expected_output=task.get('expected_output', 'Task completion result')
            )
            
            # Execute with crew
            result = self.crew.kickoff([crew_task])
            
            return {
                'success': True,
                'result': str(result),
                'agent_type': 'crewai',
                'execution_time': task.get('execution_time', 0.5)
            }
            
        except Exception as e:
            logger.error(f"CrewAI execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent_type': 'crewai'
            }
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get CrewAI capabilities."""
        return [
            AgentCapability(
                name="multi_agent_collaboration",
                description="Multi-agent collaborative task execution",
                input_schema={
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "expected_output": {"type": "string"}
                    }
                },
                output_schema={
                    "type": "object", 
                    "properties": {
                        "result": {"type": "string"},
                        "success": {"type": "boolean"}
                    }
                },
                tags=["collaboration", "multi-agent", "workflow"]
            )
        ]

class ExternalAgentRegistry:
    """Registry for managing external agents."""
    
    def __init__(self):
        """Initialize external agent registry."""
        self.registered_agents: Dict[str, ExternalAgentManifest] = {}
        self.agent_adapters: Dict[str, Any] = {}
        
    async def register_agent(self, manifest: ExternalAgentManifest, config: Dict[str, Any] = None) -> bool:
        """Register external agent."""
        try:
            # Validate manifest
            if manifest.agent_id in self.registered_agents:
                logger.warning(f"Agent {manifest.agent_id} already registered")
                return False
            
            # Create appropriate adapter
            adapter = None
            
            if manifest.agent_type == ExternalAgentType.CREWAI:
                adapter = CrewAIAgentAdapter(config or {})
            elif manifest.agent_type == ExternalAgentType.CUSTOM:
                # For Phase 3, we'll implement custom adapters
                pass
            
            # Store registration
            self.registered_agents[manifest.agent_id] = manifest
            if adapter:
                self.agent_adapters[manifest.agent_id] = adapter
            
            logger.info(f"External agent registered: {manifest.agent_id} ({manifest.agent_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Agent registration error: {e}")
            return False
    
    async def execute_agent_task(self, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using external agent."""
        try:
            if agent_id not in self.registered_agents:
                return {
                    'success': False,
                    'error': f'Agent {agent_id} not registered'
                }
            
            # Get adapter and execute
            adapter = self.agent_adapters.get(agent_id)
            if adapter:
                result = await adapter.execute_task(task)
                result['agent_id'] = agent_id
                result['execution_timestamp'] = datetime.now().isoformat()
                return result
            else:
                return {
                    'success': False,
                    'error': f'No adapter found for agent {agent_id}'
                }
                
        except Exception as e:
            logger.error(f"External agent execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent_id': agent_id
            }
    
    def list_agents(self, agent_type: ExternalAgentType = None) -> List[ExternalAgentManifest]:
        """List registered agents."""
        agents = list(self.registered_agents.values())
        
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        
        return agents

# Global registry instance
external_agent_registry = ExternalAgentRegistry()

async def register_crewai_agent(agent_id: str, config: Dict[str, Any]) -> bool:
    """Helper function to register CrewAI agent."""
    manifest = ExternalAgentManifest(
        agent_id=agent_id,
        name=f"CrewAI Agent - {agent_id}",
        agent_type=ExternalAgentType.CREWAI,
        version="1.0.0",
        description="CrewAI multi-agent system",
        capabilities=[
            AgentCapability(
                name="multi_agent_collaboration",
                description="Multi-agent collaborative task execution",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                tags=["crewai", "collaboration"]
            )
        ]
    )
    
    return await external_agent_registry.register_agent(manifest, config) 