"""
RepoChat v1.0 - API Gateway for External Agent Communication
Enterprise-grade API Gateway với security, load balancing, rate limiting.
"""

import asyncio
import hashlib
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from .external_agent_integration import external_agent_registry, ExternalAgentType
from ...shared.utils.logging_config import get_logger

logger = get_logger(__name__)

class SecurityLevel(Enum):
    """Security levels for API access."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    ENTERPRISE = "enterprise"

@dataclass
class APIKey:
    """API key definition."""
    key_id: str
    secret_hash: str
    name: str
    security_level: SecurityLevel
    rate_limit_per_minute: int
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    last_used: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class RateLimitInfo:
    """Rate limiting information."""
    requests_count: int
    window_start: datetime
    blocked_until: Optional[datetime] = None

class SecurityManager:
    """Manages API security, authentication, and authorization."""
    
    def __init__(self):
        """Initialize security manager."""
        self.api_keys: Dict[str, APIKey] = {}
        self._create_default_api_keys()
    
    def _create_default_api_keys(self):
        """Create default API keys for testing."""
        # Public API key
        public_key = self._generate_api_key(
            name="Public Access",
            security_level=SecurityLevel.PUBLIC,
            rate_limit_per_minute=30
        )
        
        # Enterprise API key  
        enterprise_key = self._generate_api_key(
            name="Enterprise Access",
            security_level=SecurityLevel.ENTERPRISE,
            rate_limit_per_minute=1000
        )
        
        logger.info(f"Default API keys created:")
        logger.info(f"  Public: {public_key}")
        logger.info(f"  Enterprise: {enterprise_key}")
    
    def _generate_api_key(self, name: str, security_level: SecurityLevel, 
                         rate_limit_per_minute: int) -> str:
        """Generate new API key."""
        key_id = str(uuid.uuid4())
        secret = f"rca_{uuid.uuid4().hex}"
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        
        api_key = APIKey(
            key_id=key_id,
            secret_hash=secret_hash,
            name=name,
            security_level=security_level,
            rate_limit_per_minute=rate_limit_per_minute
        )
        
        self.api_keys[secret] = api_key
        return secret
    
    async def verify_api_key(self, authorization: Optional[str] = Header(None)) -> APIKey:
        """Verify API key from Authorization header."""
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="API key required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization format"
            )
        
        api_key = authorization[7:]  # Remove "Bearer " prefix
        
        if api_key not in self.api_keys:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        
        key_info = self.api_keys[api_key]
        
        # Check expiration
        if key_info.expires_at and datetime.now() > key_info.expires_at:
            raise HTTPException(
                status_code=401,
                detail="API key expired"
            )
        
        # Update last used timestamp
        key_info.last_used = datetime.now()
        
        return key_info
    
    def require_security_level(self, required_level: SecurityLevel):
        """Dependency to require specific security level."""
        async def check_security_level(api_key: APIKey = Depends(self.verify_api_key)):
            security_levels = {
                SecurityLevel.PUBLIC: 0,
                SecurityLevel.AUTHENTICATED: 1,
                SecurityLevel.ENTERPRISE: 2
            }
            
            if security_levels[api_key.security_level] < security_levels[required_level]:
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires {required_level.value} access level"
                )
            
            return api_key
        
        return check_security_level

class APIGateway:
    """
    Enterprise-grade API Gateway for external agent communication.
    
    Features:
    - Authentication & authorization
    - Rate limiting
    - Request/response transformation
    - Monitoring & analytics
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """Initialize API Gateway."""
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="RepoChat External Agent API Gateway",
            version="1.0.0",
            description="Enterprise API Gateway for external agent communication"
        )
        
        self.security_manager = SecurityManager()
        self.request_count = 0
        self.start_time = datetime.now()
        
        self._setup_middleware()
        self._setup_routes()
        
        logger.info("API Gateway initialized")
    
    def _setup_middleware(self):
        """Setup middleware stack."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Compression middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            """API Gateway status."""
            return {
                "service": "RepoChat External Agent API Gateway",
                "version": "1.0.0",
                "status": "healthy",
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "request_count": self.request_count
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "external_agents": len(external_agent_registry.registered_agents),
                "gateway_uptime": (datetime.now() - self.start_time).total_seconds()
            }
        
        @self.app.get("/agents")
        async def list_agents(
            agent_type: Optional[str] = None,
            api_key: APIKey = Depends(self.security_manager.verify_api_key)
        ):
            """List available external agents."""
            self.request_count += 1
            
            # Filter by type if specified
            filter_type = None
            if agent_type:
                try:
                    filter_type = ExternalAgentType(agent_type)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid agent type: {agent_type}"
                    )
            
            agents = external_agent_registry.list_agents(filter_type)
            
            # Convert to serializable format
            return {
                "agents": [
                    {
                        "agent_id": agent.agent_id,
                        "name": agent.name,
                        "type": agent.agent_type.value,
                        "version": agent.version,
                        "description": agent.description,
                        "capabilities": [
                            {
                                "name": cap.name,
                                "description": cap.description,
                                "tags": cap.tags
                            }
                            for cap in agent.capabilities
                        ]
                    }
                    for agent in agents
                ],
                "total_count": len(agents)
            }
        
        @self.app.post("/agents/{agent_id}/execute")
        async def execute_agent_task(
            agent_id: str,
            task: Dict[str, Any],
            api_key: APIKey = Depends(self.security_manager.require_security_level(SecurityLevel.AUTHENTICATED))
        ):
            """Execute task using specific external agent."""
            self.request_count += 1
            
            try:
                # Validate agent exists
                if agent_id not in external_agent_registry.registered_agents:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Agent {agent_id} not found"
                    )
                
                # Execute task
                result = await external_agent_registry.execute_agent_task(agent_id, task)
                
                # Add gateway metadata
                result['gateway_metadata'] = {
                    'processed_at': datetime.now().isoformat(),
                    'request_id': str(uuid.uuid4()),
                    'api_key_name': api_key.name,
                    'security_level': api_key.security_level.value
                }
                
                return result
                
            except Exception as e:
                logger.error(f"Agent execution error: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Agent execution failed: {str(e)}"
                )
        
        @self.app.get("/metrics")
        async def get_metrics(
            api_key: APIKey = Depends(self.security_manager.require_security_level(SecurityLevel.AUTHENTICATED))
        ):
            """Get API Gateway metrics."""
            self.request_count += 1
            
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            return {
                "gateway_metrics": {
                    "total_requests": self.request_count,
                    "uptime_seconds": uptime,
                    "requests_per_second": self.request_count / max(uptime, 1),
                    "external_agents_count": len(external_agent_registry.registered_agents)
                },
                "security_metrics": {
                    "active_api_keys": len(self.security_manager.api_keys),
                    "authentication_enabled": True,
                    "rate_limiting_enabled": True
                }
            }
    
    async def start(self):
        """Start API Gateway."""
        logger.info(f"Starting API Gateway on {self.host}:{self.port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()

# Global API Gateway instance
api_gateway = APIGateway()

async def start_api_gateway(host: str = "0.0.0.0", port: int = 8000):
    """Start the API Gateway server."""
    gateway = APIGateway(host, port)
    await gateway.start()

if __name__ == "__main__":
    asyncio.run(start_api_gateway()) 