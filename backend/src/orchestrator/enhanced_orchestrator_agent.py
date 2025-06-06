"""
Enhanced Orchestrator Agent - A2A Protocol & LangGraph Integration

This is the next-generation orchestrator that implements:
- Google Agent2Agent (A2A) Protocol for standardized communication
- LangGraph state machine for robust workflow management  
- Circuit breaker patterns for fault tolerance
- Dynamic agent discovery and coordination

Enhanced for RepoChat v2.0 multi-agent optimization.
"""

import asyncio
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import structlog
from enum import Enum

# A2A Protocol imports (when available)
try:
    from a2a.types import AgentCard, AgentSkill, AgentCapabilities
    from a2a.server.apps import A2AStarletteApplication
    from a2a.client import A2AClient
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False
    print("A2A SDK not available. Using fallback communication.")

# LangGraph imports (when available)  
try:
    from langgraph import StateGraph, START, END
    from langgraph.graph import MessagesState
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("LangGraph not available. Using fallback orchestration.")

# Circuit breaker và resilience
try:
    from tenacity import retry, stop_after_attempt, wait_exponential
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

# Current system imports
from ..shared.models.task_definition import TaskDefinition
from ..shared.models.project_data_context import ProjectDataContext
from ..shared.utils.logging_config import get_logger


class WorkflowStage(Enum):
    """Enhanced workflow stages for state machine"""
    INIT = "init"
    DATA_ACQUISITION = "data_acquisition" 
    CKG_OPERATIONS = "ckg_operations"
    CODE_ANALYSIS = "code_analysis"
    SYNTHESIS = "synthesis"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class RepoAnalysisState:
    """Enhanced state for LangGraph workflow"""
    # Core workflow data
    repository_url: str
    analysis_stage: WorkflowStage = WorkflowStage.INIT
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Analysis results
    project_context: Optional[ProjectDataContext] = None
    ckg_result: Optional[Dict[str, Any]] = None
    analysis_findings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Workflow metadata
    current_agent: Optional[str] = None
    error_count: int = 0
    retry_count: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    
    # A2A agent tracking
    available_agents: Dict[str, Any] = field(default_factory=dict)
    active_tasks: Dict[str, str] = field(default_factory=dict)


class AgentCommunicationManager:
    """Manages A2A protocol communication with circuit breaker patterns"""
    
    def __init__(self):
        self.logger = structlog.get_logger("agent.communication")
        self.circuit_breakers: Dict[str, bool] = {}
        self.failure_counts: Dict[str, int] = {}
        self.a2a_clients: Dict[str, Any] = {}  # A2AClient instances
        
    async def discover_agents(self) -> Dict[str, Any]:
        """Discover available A2A agents"""
        if not A2A_AVAILABLE:
            self.logger.warning("A2A not available, using mock agent discovery")
            return self._mock_agent_discovery()
            
        discovered_agents = {}
        # In real implementation, this would scan network/registry
        # For now, return known local agents
        known_endpoints = [
            "http://localhost:9001",  # Data Acquisition Agent
            "http://localhost:9002",  # CKG Operations Agent  
            "http://localhost:9003",  # Code Analysis Agent
            "http://localhost:9004",  # LLM Services Agent
        ]
        
        for endpoint in known_endpoints:
            try:
                if A2A_AVAILABLE:
                    client = A2AClient(endpoint)
                    agent_card = await client.get_agent_card()
                    discovered_agents[agent_card.name] = agent_card
                    self.a2a_clients[agent_card.name] = client
            except Exception as e:
                self.logger.warning(f"Failed to discover agent at {endpoint}: {e}")
                
        return discovered_agents
    
    def _mock_agent_discovery(self) -> Dict[str, Dict[str, Any]]:
        """Mock agent discovery when A2A not available"""
        return {
            "DataAcquisitionAgent": {
                "name": "Data Acquisition Agent",
                "skills": ["clone_repository", "detect_languages", "prepare_data"],
                "endpoint": "internal://data_acquisition"
            },
            "CKGOperationsAgent": {
                "name": "CKG Operations Agent", 
                "skills": ["parse_code", "build_ckg", "analyze_relationships"],
                "endpoint": "internal://ckg_operations"
            },
            "CodeAnalysisAgent": {
                "name": "Code Analysis Agent",
                "skills": ["analyze_architecture", "detect_patterns", "find_issues"],
                "endpoint": "internal://code_analysis"
            }
        }
    
    async def call_agent_with_retry(self, agent_name: str, skill_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call agent with retry logic"""
        if TENACITY_AVAILABLE:
            return await self._call_with_tenacity(agent_name, skill_id, task_data)
        else:
            return await self._call_agent_internal(agent_name, skill_id, task_data)
    
    if TENACITY_AVAILABLE:
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10)
        )
        async def _call_with_tenacity(self, agent_name: str, skill_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
            """Call agent with exponential backoff"""
            return await self._call_agent_internal(agent_name, skill_id, task_data)
    
    async def _call_agent_internal(self, agent_name: str, skill_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal agent call implementation"""
        if self.circuit_breakers.get(agent_name, False):
            raise Exception(f"Circuit breaker open for agent {agent_name}")
            
        try:
            if A2A_AVAILABLE and agent_name in self.a2a_clients:
                # Use A2A protocol
                client = self.a2a_clients[agent_name]
                result = await client.send_task({
                    "skill": skill_id,
                    "data": task_data
                })
                self._reset_circuit_breaker(agent_name)
                return result
            else:
                # Fallback to current system
                result = await self._fallback_agent_call(agent_name, skill_id, task_data)
                return result
                
        except Exception as e:
            self._handle_agent_failure(agent_name, e)
            raise
    
    async def _fallback_agent_call(self, agent_name: str, skill_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to current system when A2A not available"""
        self.logger.info(f"Using fallback communication for {agent_name}.{skill_id}")
        
        # Mock successful responses for demo
        await asyncio.sleep(0.1)  # Simulate processing time
        
        if agent_name == "DataAcquisitionAgent":
            return {
                "success": True,
                "project_context": {
                    "repository_url": task_data.get("repository_url"),
                    "detected_languages": ["Python", "JavaScript"],
                    "cloned_path": "/tmp/mock_repo"
                }
            }
        elif agent_name == "CKGOperationsAgent":
            return {
                "success": True, 
                "nodes_created": 150,
                "relationships_created": 89,
                "files_processed": 45
            }
        elif agent_name == "CodeAnalysisAgent":
            return {
                "success": True,
                "findings": [
                    {"type": "architecture", "severity": "info", "message": "Well-structured modular design"},
                    {"type": "pattern", "severity": "warning", "message": "Potential circular dependency in module X"}
                ]
            }
        
        return {"success": True, "message": f"Mock response from {agent_name}"}
    
    def _handle_agent_failure(self, agent_name: str, error: Exception):
        """Handle agent communication failure"""
        self.failure_counts[agent_name] = self.failure_counts.get(agent_name, 0) + 1
        
        if self.failure_counts[agent_name] >= 3:
            self.circuit_breakers[agent_name] = True
            self.logger.error(f"Circuit breaker opened for agent {agent_name} after {self.failure_counts[agent_name]} failures")
        
        self.logger.error(f"Agent {agent_name} communication failed: {error}")
    
    def _reset_circuit_breaker(self, agent_name: str):
        """Reset circuit breaker after successful call"""
        self.circuit_breakers[agent_name] = False
        self.failure_counts[agent_name] = 0


class EnhancedOrchestratorAgent:
    """
    Enhanced Orchestrator Agent với A2A Protocol và LangGraph integration
    
    Features:
    - A2A standardized communication
    - LangGraph state machine workflows
    - Circuit breaker fault tolerance  
    - Dynamic agent discovery
    - Comprehensive monitoring
    """
    
    def __init__(self):
        self.logger = structlog.get_logger("orchestrator.enhanced")
        self.communication_manager = AgentCommunicationManager()
        self.workflow_graph = None
        self.checkpointer = MemorySaver() if LANGGRAPH_AVAILABLE else None
        
        # Initialize workflow
        if LANGGRAPH_AVAILABLE:
            self.workflow_graph = self._create_optimized_workflow()
        
        self.logger.info("Enhanced Orchestrator Agent initialized", extra={
            "a2a_available": A2A_AVAILABLE,
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "tenacity_available": TENACITY_AVAILABLE
        })
    
    def _create_optimized_workflow(self):
        """Create LangGraph workflow with optimized state machine"""
        if not LANGGRAPH_AVAILABLE:
            return None
            
        workflow = StateGraph(dict)  # Using dict instead of MessagesState for simplicity
        
        # Add workflow nodes
        workflow.add_node("init", self._init_workflow_node)
        workflow.add_node("discover_agents", self._discover_agents_node) 
        workflow.add_node("data_acquisition", self._data_acquisition_node)
        workflow.add_node("ckg_operations", self._ckg_operations_node)
        workflow.add_node("code_analysis", self._code_analysis_node)
        workflow.add_node("synthesis", self._synthesis_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Define workflow edges
        workflow.set_entry_point("init")
        workflow.add_edge("init", "discover_agents")
        workflow.add_edge("discover_agents", "data_acquisition")
        
        # Conditional edges with error handling
        workflow.add_conditional_edges(
            "data_acquisition",
            self._should_continue_after_data_acquisition,
            {
                "continue": "ckg_operations",
                "retry": "data_acquisition",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "ckg_operations", 
            self._should_continue_after_ckg,
            {
                "continue": "code_analysis",
                "retry": "ckg_operations", 
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("code_analysis", "synthesis")
        workflow.add_edge("synthesis", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _init_workflow_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize workflow state"""
        self.logger.info("Initializing enhanced workflow", extra={"execution_id": state.get("execution_id")})
        
        state.update({
            "analysis_stage": WorkflowStage.INIT.value,
            "start_time": datetime.now(),
            "error_count": 0,
            "retry_count": 0
        })
        return state
    
    async def _discover_agents_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Discover available agents through A2A protocol"""
        self.logger.info("Discovering available agents")
        
        try:
            available_agents = await self.communication_manager.discover_agents()
            state["available_agents"] = available_agents
            state["analysis_stage"] = "agent_discovery_completed"
            
            self.logger.info("Agent discovery completed", extra={
                "agents_found": len(available_agents),
                "agent_names": list(available_agents.keys())
            })
            
        except Exception as e:
            self.logger.error(f"Agent discovery failed: {e}")
            state["error_count"] += 1
            state["last_error"] = str(e)
            
        return state
    
    async def _data_acquisition_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data acquisition through A2A agent"""
        self.logger.info("Starting data acquisition")
        
        try:
            result = await self.communication_manager.call_agent_with_retry(
                agent_name="DataAcquisitionAgent",
                skill_id="clone_repository", 
                task_data={
                    "repository_url": state["repository_url"],
                    "execution_id": state["execution_id"]
                }
            )
            
            if result.get("success"):
                state["project_context"] = result.get("project_context", {})
                state["analysis_stage"] = "data_acquisition_completed"
                self.logger.info("Data acquisition completed successfully")
            else:
                raise Exception(f"Data acquisition failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Data acquisition error: {e}")
            state["error_count"] += 1
            state["last_error"] = str(e)
            
        return state
    
    async def _ckg_operations_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CKG operations through A2A agent"""
        self.logger.info("Starting CKG operations")
        
        try:
            result = await self.communication_manager.call_agent_with_retry(
                agent_name="CKGOperationsAgent",
                skill_id="build_ckg",
                task_data={
                    "project_context": state.get("project_context", {}),
                    "execution_id": state["execution_id"]
                }
            )
            
            if result.get("success"):
                state["ckg_result"] = result
                state["analysis_stage"] = "ckg_operations_completed"
                self.logger.info("CKG operations completed successfully")
            else:
                raise Exception(f"CKG operations failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"CKG operations error: {e}")
            state["error_count"] += 1
            state["last_error"] = str(e)
            
        return state
    
    async def _code_analysis_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code analysis through A2A agent"""
        self.logger.info("Starting code analysis")
        
        try:
            result = await self.communication_manager.call_agent_with_retry(
                agent_name="CodeAnalysisAgent", 
                skill_id="analyze_architecture",
                task_data={
                    "project_context": state.get("project_context", {}),
                    "ckg_result": state.get("ckg_result", {}),
                    "execution_id": state["execution_id"]
                }
            )
            
            if result.get("success"):
                state["analysis_findings"] = result.get("findings", [])
                state["analysis_stage"] = "code_analysis_completed"
                self.logger.info("Code analysis completed successfully")
            else:
                raise Exception(f"Code analysis failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Code analysis error: {e}")
            state["error_count"] += 1
            state["last_error"] = str(e)
            
        return state
    
    async def _synthesis_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize final results"""
        self.logger.info("Starting synthesis")
        
        try:
            # Synthesize all results
            synthesis_result = {
                "execution_id": state["execution_id"],
                "repository_url": state["repository_url"],
                "analysis_duration": (datetime.now() - state["start_time"]).total_seconds(),
                "project_context": state.get("project_context", {}),
                "ckg_metrics": state.get("ckg_result", {}),
                "findings": state.get("analysis_findings", []),
                "agent_communications": len(state.get("available_agents", {}))
            }
            
            state["synthesis_result"] = synthesis_result
            state["analysis_stage"] = WorkflowStage.COMPLETED.value
            
            self.logger.info("Synthesis completed", extra={
                "total_findings": len(synthesis_result["findings"]),
                "duration_seconds": synthesis_result["analysis_duration"]
            })
            
        except Exception as e:
            self.logger.error(f"Synthesis error: {e}")
            state["error_count"] += 1
            state["last_error"] = str(e)
            
        return state
    
    async def _error_handler_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow errors"""
        self.logger.error("Entering error handler", extra={
            "error_count": state.get("error_count", 0),
            "last_error": state.get("last_error", "Unknown")
        })
        
        state["analysis_stage"] = WorkflowStage.ERROR.value
        state["final_status"] = "failed"
        
        return state
    
    def _should_continue_after_data_acquisition(self, state: Dict[str, Any]) -> str:
        """Conditional logic for data acquisition"""
        if state.get("error_count", 0) > 0:
            if state.get("retry_count", 0) < 2:
                state["retry_count"] = state.get("retry_count", 0) + 1
                return "retry"
            else:
                return "error"
        return "continue"
    
    def _should_continue_after_ckg(self, state: Dict[str, Any]) -> str:
        """Conditional logic for CKG operations"""
        if state.get("error_count", 0) > 0:
            if state.get("retry_count", 0) < 2:
                state["retry_count"] = state.get("retry_count", 0) + 1
                return "retry"
            else:
                return "error"
        return "continue"
    
    async def execute_enhanced_workflow(self, repository_url: str) -> Dict[str, Any]:
        """Execute enhanced workflow using LangGraph state machine"""
        execution_id = str(uuid.uuid4())
        
        initial_state = {
            "repository_url": repository_url,
            "execution_id": execution_id,
            "analysis_stage": WorkflowStage.INIT.value
        }
        
        self.logger.info("Starting enhanced workflow execution", extra={
            "execution_id": execution_id,
            "repository_url": repository_url
        })
        
        try:
            if self.workflow_graph:
                # Use LangGraph workflow
                result = await self.workflow_graph.ainvoke(initial_state)
            else:
                # Fallback sequential execution
                result = await self._fallback_sequential_execution(initial_state)
            
            self.logger.info("Enhanced workflow completed", extra={
                "execution_id": execution_id,
                "final_stage": result.get("analysis_stage"),
                "success": result.get("analysis_stage") == WorkflowStage.COMPLETED.value
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced workflow failed: {e}", extra={"execution_id": execution_id})
            return {
                "execution_id": execution_id,
                "analysis_stage": WorkflowStage.ERROR.value,
                "error": str(e)
            }
    
    async def _fallback_sequential_execution(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback sequential execution when LangGraph not available"""
        state = initial_state.copy()
        
        # Execute nodes sequentially
        state = await self._init_workflow_node(state)
        state = await self._discover_agents_node(state)
        state = await self._data_acquisition_node(state)
        state = await self._ckg_operations_node(state)
        state = await self._code_analysis_node(state)
        state = await self._synthesis_node(state)
        
        return state
    
    def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get current workflow status"""
        # In real implementation, this would query checkpointer
        return {
            "execution_id": execution_id,
            "status": "running",
            "current_stage": "unknown",
            "progress": "0%"
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down Enhanced Orchestrator Agent")
        # Close A2A connections, cleanup resources
        for client in self.communication_manager.a2a_clients.values():
            if hasattr(client, 'close'):
                await client.close()


# Standalone test function
async def test_enhanced_orchestrator():
    """Test function for Enhanced Orchestrator Agent"""
    print("🚀 Testing Enhanced Orchestrator Agent...")
    
    orchestrator = EnhancedOrchestratorAgent()
    
    # Test workflow execution
    test_repo_url = "https://github.com/test/sample-repo"
    result = await orchestrator.execute_enhanced_workflow(test_repo_url)
    
    print(f"✅ Workflow Result:")
    print(f"   Execution ID: {result.get('execution_id')}")
    print(f"   Stage: {result.get('analysis_stage')}")
    print(f"   Success: {result.get('analysis_stage') == WorkflowStage.COMPLETED.value}")
    
    if result.get("synthesis_result"):
        synthesis = result["synthesis_result"]
        print(f"   Duration: {synthesis.get('analysis_duration', 0):.2f}s")
        print(f"   Findings: {len(synthesis.get('findings', []))}")
        print(f"   Agents Used: {synthesis.get('agent_communications', 0)}")
    
    await orchestrator.shutdown()
    return result


if __name__ == "__main__":
    # Run test if executed directly
    import asyncio
    asyncio.run(test_enhanced_orchestrator()) 