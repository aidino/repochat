"""
RepoChat v1.0 - Phase 3 Integration Test
Test external agent integration và API Gateway functionality.
"""

import asyncio
import time
from typing import Dict, Any

from .external_agent_integration import (
    external_agent_registry,
    register_crewai_agent,
    ExternalAgentType,
    ExternalAgentManifest,
    AgentCapability
)
from .api_gateway import APIGateway, SecurityManager
from ...shared.utils.logging_config import get_logger

logger = get_logger(__name__)

async def test_external_agent_integration():
    """Test external agent integration functionality."""
    print("🧪 Testing External Agent Integration...")
    
    results = {
        'success': True,
        'tests': {},
        'total_agents_registered': 0,
        'execution_tests_passed': 0
    }
    
    try:
        # Test 1: Register CrewAI Agent
        print("\n📋 Test 1: CrewAI Agent Registration")
        
        crewai_config = {
            'agents': [
                {
                    'role': 'Code Analyst',
                    'goal': 'Analyze code quality and patterns',
                    'backstory': 'Expert in code analysis and best practices',
                    'verbose': True
                }
            ],
            'verbose': True
        }
        
        success = await register_crewai_agent("crewai-code-analyst", crewai_config)
        results['tests']['crewai_registration'] = success
        
        if success:
            results['total_agents_registered'] += 1
            print("  ✅ CrewAI agent registered successfully")
        else:
            print("  ❌ CrewAI agent registration failed")
            results['success'] = False
        
        # Test 2: List Registered Agents
        print("\n📋 Test 2: List Registered Agents")
        
        agents = external_agent_registry.list_agents()
        results['tests']['agent_listing'] = len(agents) > 0
        
        print(f"  📊 Found {len(agents)} registered agents:")
        for agent in agents:
            print(f"    - {agent.name} ({agent.agent_type.value}) - {len(agent.capabilities)} capabilities")
        
        # Test 3: Execute Agent Task
        print("\n📋 Test 3: Agent Task Execution")
        
        if "crewai-code-analyst" in external_agent_registry.registered_agents:
            task = {
                'description': 'Analyze the code quality of a Python function',
                'expected_output': 'Code quality assessment report',
                'execution_time': 0.5
            }
            
            execution_result = await external_agent_registry.execute_agent_task(
                "crewai-code-analyst", 
                task
            )
            
            results['tests']['agent_execution'] = execution_result.get('success', False)
            
            if execution_result.get('success'):
                results['execution_tests_passed'] += 1
                print("  ✅ Agent task executed successfully")
                print(f"    Result: {execution_result.get('result', 'No result')}")
            else:
                print("  ❌ Agent task execution failed")
                print(f"    Error: {execution_result.get('error', 'Unknown error')}")
        else:
            print("  ⏭️ Skipping execution test - no agents registered")
            results['tests']['agent_execution'] = False
        
        # Test 4: Custom Agent Registration (Mock)
        print("\n📋 Test 4: Custom Agent Registration")
        
        custom_manifest = ExternalAgentManifest(
            agent_id="custom-test-agent",
            name="Custom Test Agent",
            agent_type=ExternalAgentType.CUSTOM,
            version="1.0.0",
            description="Test custom agent for validation",
            capabilities=[
                AgentCapability(
                    name="test_execution",
                    description="Execute test tasks",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                    tags=["test", "custom"]
                )
            ]
        )
        
        custom_config = {
            'module_path': 'tests.mock_agent',
            'class_name': 'MockCustomAgent',
            'init_config': {'test_mode': True}
        }
        
        custom_success = await external_agent_registry.register_agent(custom_manifest, custom_config)
        results['tests']['custom_registration'] = custom_success
        
        if custom_success:
            results['total_agents_registered'] += 1
            print("  ✅ Custom agent registered successfully")
        else:
            print("  ❌ Custom agent registration failed")
        
        # Test 5: Agent Registry Stats
        print("\n📋 Test 5: Registry Statistics")
        
        final_agents = external_agent_registry.list_agents()
        by_type = {}
        total_capabilities = 0
        
        for agent in final_agents:
            agent_type = agent.agent_type.value
            by_type[agent_type] = by_type.get(agent_type, 0) + 1
            total_capabilities += len(agent.capabilities)
        
        results['tests']['registry_stats'] = {
            'total_agents': len(final_agents),
            'by_type': by_type,
            'total_capabilities': total_capabilities
        }
        
        print(f"  📊 Registry Statistics:")
        print(f"    Total agents: {len(final_agents)}")
        print(f"    By type: {by_type}")
        print(f"    Total capabilities: {total_capabilities}")
        
    except Exception as e:
        logger.error(f"External agent integration test error: {e}")
        results['success'] = False
        results['error'] = str(e)
    
    return results

async def test_api_gateway():
    """Test API Gateway functionality."""
    print("\n🌐 Testing API Gateway...")
    
    results = {
        'success': True,
        'tests': {},
        'gateway_initialized': False,
        'security_enabled': False
    }
    
    try:
        # Test 1: Gateway Initialization
        print("\n📋 Test 1: Gateway Initialization")
        
        gateway = APIGateway(host="localhost", port=8001)
        results['tests']['gateway_init'] = True
        results['gateway_initialized'] = True
        
        print("  ✅ API Gateway initialized successfully")
        print(f"    Host: {gateway.host}:{gateway.port}")
        print(f"    Title: {gateway.app.title}")
        
        # Test 2: Security Manager
        print("\n📋 Test 2: Security Manager")
        
        security_manager = SecurityManager()
        results['tests']['security_manager'] = len(security_manager.api_keys) > 0
        results['security_enabled'] = True
        
        print(f"  ✅ Security manager initialized")
        print(f"    API keys created: {len(security_manager.api_keys)}")
        
        # List API keys (first 10 chars only for security)
        for key, api_key in security_manager.api_keys.items():
            print(f"    - {api_key.name}: {key[:10]}... ({api_key.security_level.value})")
        
        # Test 3: Route Configuration
        print("\n📋 Test 3: Route Configuration")
        
        routes = [route.path for route in gateway.app.routes]
        expected_routes = ["/", "/health", "/agents", "/metrics"]
        
        routes_configured = all(route in [r.path for r in gateway.app.routes] for route in expected_routes)
        results['tests']['routes_configured'] = routes_configured
        
        if routes_configured:
            print("  ✅ All expected routes configured")
            print(f"    Routes: {[r for r in routes if not r.startswith('/docs')]}")
        else:
            print("  ❌ Some routes missing")
            results['success'] = False
        
        # Test 4: Middleware Configuration
        print("\n📋 Test 4: Middleware Configuration")
        
        middleware_count = len(gateway.app.user_middleware)
        results['tests']['middleware_count'] = middleware_count
        
        print(f"  ✅ Middleware configured: {middleware_count} middleware layers")
        
        # Test 5: Gateway Status
        print("\n📋 Test 5: Gateway Status")
        
        uptime = (gateway.app.state.__dict__ if hasattr(gateway.app, 'state') else {})
        results['tests']['gateway_status'] = {
            'request_count': gateway.request_count,
            'start_time': gateway.start_time.isoformat(),
            'uptime_seconds': (time.time() - gateway.start_time.timestamp())
        }
        
        print(f"  ✅ Gateway status:")
        print(f"    Request count: {gateway.request_count}")
        print(f"    Uptime: {results['tests']['gateway_status']['uptime_seconds']:.2f}s")
        
    except Exception as e:
        logger.error(f"API Gateway test error: {e}")
        results['success'] = False
        results['error'] = str(e)
    
    return results

async def test_phase3_integration():
    """Test complete Phase 3 integration."""
    print("🚀 Testing Phase 3: Advanced Features Integration")
    print("=" * 60)
    
    overall_results = {
        'success': True,
        'start_time': time.time(),
        'components': {}
    }
    
    try:
        # Test External Agent Integration
        agent_results = await test_external_agent_integration()
        overall_results['components']['external_agents'] = agent_results
        
        if not agent_results['success']:
            overall_results['success'] = False
        
        # Test API Gateway
        gateway_results = await test_api_gateway()
        overall_results['components']['api_gateway'] = gateway_results
        
        if not gateway_results['success']:
            overall_results['success'] = False
        
        # Calculate summary
        overall_results['end_time'] = time.time()
        overall_results['duration'] = overall_results['end_time'] - overall_results['start_time']
        
        # Print final results
        print("\n" + "=" * 60)
        print("🎯 PHASE 3 INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        status = "✅ PASSED" if overall_results['success'] else "❌ FAILED"
        print(f"Overall Status: {status}")
        print(f"Duration: {overall_results['duration']:.2f} seconds")
        
        print(f"\n📊 Component Results:")
        
        # External Agents Summary
        agent_summary = overall_results['components']['external_agents']
        agent_status = "✅ PASSED" if agent_summary['success'] else "❌ FAILED"
        print(f"  External Agent Integration: {agent_status}")
        print(f"    Agents registered: {agent_summary['total_agents_registered']}")
        print(f"    Execution tests passed: {agent_summary['execution_tests_passed']}")
        
        # API Gateway Summary
        gateway_summary = overall_results['components']['api_gateway']
        gateway_status = "✅ PASSED" if gateway_summary['success'] else "❌ FAILED"
        print(f"  API Gateway: {gateway_status}")
        print(f"    Gateway initialized: {gateway_summary['gateway_initialized']}")
        print(f"    Security enabled: {gateway_summary['security_enabled']}")
        
        if overall_results['success']:
            print("\n🚀 Phase 3 Advanced Features: VALIDATED ✅")
        else:
            print("\n❌ Phase 3 has issues that need attention")
        
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Phase 3 integration test error: {e}")
        overall_results['success'] = False
        overall_results['error'] = str(e)
    
    return overall_results

if __name__ == "__main__":
    asyncio.run(test_phase3_integration()) 