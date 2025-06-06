"""
RepoChat v1.0 - Performance Monitoring Dashboard
Real-time monitoring cho migration process từ legacy sang enhanced orchestrator.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

from .migration_manager import MigrationManager, MigrationPhase
from ..shared.utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: datetime
    value: float
    tags: Dict[str, str]

@dataclass
class SystemHealth:
    """Overall system health status."""
    status: str  # "healthy", "degraded", "critical"
    migration_phase: str
    enhanced_traffic_percentage: float
    success_rate_legacy: float
    success_rate_enhanced: float
    performance_ratio: float
    circuit_breaker_open: bool
    recommendations: List[str]

class MetricsCollector:
    """Collects và stores performance metrics."""
    
    def __init__(self, retention_hours: int = 24):
        """
        Initialize metrics collector.
        
        Args:
            retention_hours: How long to keep metrics data
        """
        self.retention_hours = retention_hours
        self.retention_seconds = retention_hours * 3600
        
        # Time series data storage
        self.metrics = defaultdict(lambda: deque(maxlen=10000))
        
        # Real-time statistics
        self.current_stats = {}
        
        # Alert thresholds
        self.alert_thresholds = {
            'success_rate_min': 0.95,
            'performance_ratio_max': 2.0,
            'error_rate_max': 0.05,
            'response_time_max': 30.0
        }

    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """
        Record a metric data point.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Additional tags for the metric
        """
        if tags is None:
            tags = {}
            
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags
        )
        
        self.metrics[metric_name].append(point)
        self._cleanup_old_metrics()
        
        logger.debug(f"Recorded metric {metric_name}: {value} with tags {tags}")

    def get_metric_series(self, metric_name: str, since: datetime = None) -> List[MetricPoint]:
        """
        Get time series data for a metric.
        
        Args:
            metric_name: Name of the metric
            since: Only return points after this timestamp
            
        Returns:
            List of metric points
        """
        if since is None:
            since = datetime.now() - timedelta(hours=1)
            
        points = self.metrics.get(metric_name, [])
        return [p for p in points if p.timestamp >= since]

    def get_current_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        stats = {}
        
        for metric_name in self.metrics:
            recent_points = self.get_metric_series(metric_name, hour_ago)
            
            if recent_points:
                values = [p.value for p in recent_points]
                stats[metric_name] = {
                    'current': values[-1],
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
            else:
                stats[metric_name] = {
                    'current': 0,
                    'average': 0,
                    'min': 0,
                    'max': 0,
                    'count': 0
                }
        
        return stats

    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff = datetime.now() - timedelta(seconds=self.retention_seconds)
        
        for metric_name in self.metrics:
            while (self.metrics[metric_name] and 
                   self.metrics[metric_name][0].timestamp < cutoff):
                self.metrics[metric_name].popleft()

class MonitoringDashboard:
    """
    Real-time monitoring dashboard cho migration process.
    
    Features:
    - Real-time metrics visualization
    - Health status monitoring
    - Alert generation
    - Migration phase control
    - Performance comparison
    """
    
    def __init__(self, migration_manager: MigrationManager):
        """
        Initialize monitoring dashboard.
        
        Args:
            migration_manager: Migration manager instance to monitor
        """
        self.migration_manager = migration_manager
        self.metrics_collector = MetricsCollector()
        
        # WebSocket connections for real-time updates
        self.websocket_connections: List[WebSocket] = []
        
        # FastAPI app for dashboard
        self.app = FastAPI(title="RepoChat Migration Dashboard")
        self._setup_routes()
        
        # Monitoring task
        self.monitoring_task = None
        self.monitoring_active = False

    def _setup_routes(self):
        """Setup FastAPI routes for dashboard."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home():
            return self._get_dashboard_html()
            
        @self.app.get("/health")
        async def get_health():
            return asdict(await self.get_system_health())
            
        @self.app.get("/metrics")
        async def get_metrics():
            return self.get_current_metrics()
            
        @self.app.get("/migration/status")
        async def get_migration_status():
            return {
                "phase": self.migration_manager.current_phase.value,
                "traffic_percentage": self.migration_manager.enhanced_traffic_percentage,
                "migration_enabled": self.migration_manager.migration_enabled,
                "circuit_breaker_open": self.migration_manager.circuit_breaker_open
            }
            
        @self.app.post("/migration/advance")
        async def advance_migration():
            success = await self.migration_manager.advance_migration_phase()
            return {"success": success, "phase": self.migration_manager.current_phase.value}
            
        @self.app.post("/migration/rollback")
        async def rollback_migration():
            success = await self.migration_manager.rollback_migration()
            return {"success": success, "phase": self.migration_manager.current_phase.value}
            
        @self.app.post("/migration/enable")
        async def enable_migration():
            self.migration_manager.enable_migration()
            return {"status": "enabled"}
            
        @self.app.post("/migration/disable")
        async def disable_migration():
            self.migration_manager.disable_migration()
            return {"status": "disabled"}
            
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self._handle_websocket(websocket)

    async def _handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection for real-time updates."""
        await websocket.accept()
        self.websocket_connections.append(websocket)
        
        try:
            while True:
                # Send current metrics every second
                metrics = self.get_current_metrics()
                await websocket.send_json(metrics)
                await asyncio.sleep(1)
                
        except WebSocketDisconnect:
            self.websocket_connections.remove(websocket)

    async def start_monitoring(self):
        """Start monitoring process."""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Monitoring dashboard started")

    async def stop_monitoring(self):
        """Stop monitoring process."""
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Monitoring dashboard stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect current metrics from migration manager
                metrics = self.migration_manager.get_current_metrics()
                
                # Record key metrics
                self._record_metrics_from_manager(metrics)
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                # Broadcast to WebSocket connections
                await self._broadcast_metrics(metrics)
                
                await asyncio.sleep(5)  # Collect metrics every 5 seconds
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)

    def _record_metrics_from_manager(self, metrics: Dict[str, Any]):
        """Record metrics from migration manager to time series storage."""
        # Legacy orchestrator metrics
        legacy = metrics.get('legacy', {})
        if legacy.get('requests', 0) > 0:
            self.metrics_collector.record_metric(
                'success_rate', 
                legacy.get('success_rate', 0),
                {'orchestrator': 'legacy'}
            )
            self.metrics_collector.record_metric(
                'response_time',
                legacy.get('average_time', 0),
                {'orchestrator': 'legacy'}
            )
            self.metrics_collector.record_metric(
                'request_count',
                legacy.get('requests', 0),
                {'orchestrator': 'legacy'}
            )
        
        # Enhanced orchestrator metrics
        enhanced = metrics.get('enhanced', {})
        if enhanced.get('requests', 0) > 0:
            self.metrics_collector.record_metric(
                'success_rate',
                enhanced.get('success_rate', 0),
                {'orchestrator': 'enhanced'}
            )
            self.metrics_collector.record_metric(
                'response_time',
                enhanced.get('average_time', 0),
                {'orchestrator': 'enhanced'}
            )
            self.metrics_collector.record_metric(
                'request_count',
                enhanced.get('requests', 0),
                {'orchestrator': 'enhanced'}
            )
            self.metrics_collector.record_metric(
                'performance_ratio',
                enhanced.get('performance_ratio', 1.0),
                {'orchestrator': 'enhanced'}
            )
        
        # Migration metrics
        self.metrics_collector.record_metric(
            'traffic_percentage',
            metrics.get('enhanced_traffic_percentage', 0),
            {'type': 'migration'}
        )

    async def _check_alerts(self, metrics: Dict[str, Any]):
        """Check for alert conditions and log warnings."""
        alerts = []
        
        # Check enhanced orchestrator success rate
        enhanced = metrics.get('enhanced', {})
        if enhanced.get('requests', 0) > 10:  # Need minimum sample size
            success_rate = enhanced.get('success_rate', 1.0)
            if success_rate < self.metrics_collector.alert_thresholds['success_rate_min']:
                alerts.append(f"Enhanced success rate low: {success_rate:.2%}")
                
            performance_ratio = enhanced.get('performance_ratio', 1.0)
            if performance_ratio > self.metrics_collector.alert_thresholds['performance_ratio_max']:
                alerts.append(f"Enhanced performance degraded: {performance_ratio:.2f}x slower")
        
        # Check circuit breaker status
        if metrics.get('circuit_breaker_open', False):
            alerts.append("Circuit breaker OPEN - Enhanced orchestrator disabled")
            
        # Log alerts
        for alert in alerts:
            logger.warning(f"ALERT: {alert}")

    async def _broadcast_metrics(self, metrics: Dict[str, Any]):
        """Broadcast metrics to all WebSocket connections."""
        if not self.websocket_connections:
            return
            
        # Add health status
        health = await self.get_system_health()
        broadcast_data = {
            'metrics': metrics,
            'health': asdict(health),
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all connections
        disconnected = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send_json(broadcast_data)
            except:
                disconnected.append(websocket)
                
        # Remove disconnected clients
        for websocket in disconnected:
            self.websocket_connections.remove(websocket)

    async def get_system_health(self) -> SystemHealth:
        """
        Determine overall system health status.
        
        Returns:
            SystemHealth object with current status and recommendations
        """
        metrics = self.migration_manager.get_current_metrics()
        recommendations = []
        
        # Determine health status
        legacy = metrics.get('legacy', {})
        enhanced = metrics.get('enhanced', {})
        
        legacy_success = legacy.get('success_rate', 1.0)
        enhanced_success = enhanced.get('success_rate', 1.0)
        performance_ratio = enhanced.get('performance_ratio', 1.0)
        circuit_breaker_open = metrics.get('circuit_breaker_open', False)
        
        # Health logic
        if circuit_breaker_open:
            status = "critical"
            recommendations.append("Circuit breaker open - investigate enhanced orchestrator issues")
        elif enhanced_success < 0.9 and enhanced.get('requests', 0) > 10:
            status = "degraded"
            recommendations.append("Enhanced orchestrator success rate below 90%")
        elif performance_ratio > 3.0:
            status = "degraded"
            recommendations.append("Enhanced orchestrator 3x+ slower than legacy")
        elif legacy_success < 0.95:
            status = "degraded"
            recommendations.append("Legacy orchestrator success rate below 95%")
        else:
            status = "healthy"
            
        # Migration recommendations
        if (status == "healthy" and 
            enhanced.get('requests', 0) > 20 and 
            enhanced_success >= 0.95 and 
            performance_ratio <= 1.5):
            recommendations.append("Consider advancing to next migration phase")
            
        return SystemHealth(
            status=status,
            migration_phase=metrics.get('phase', 'unknown'),
            enhanced_traffic_percentage=metrics.get('enhanced_traffic_percentage', 0),
            success_rate_legacy=legacy_success,
            success_rate_enhanced=enhanced_success,
            performance_ratio=performance_ratio,
            circuit_breaker_open=circuit_breaker_open,
            recommendations=recommendations
        )

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics including time series data."""
        manager_metrics = self.migration_manager.get_current_metrics()
        collector_stats = self.metrics_collector.get_current_stats()
        
        return {
            'migration': manager_metrics,
            'time_series': collector_stats,
            'timestamp': datetime.now().isoformat()
        }

    def _get_dashboard_html(self) -> str:
        """Return simple HTML dashboard."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>RepoChat Migration Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .healthy { background-color: #d4edda; }
                .degraded { background-color: #fff3cd; }
                .critical { background-color: #f8d7da; }
                .metric { display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ccc; }
                #status { font-size: 24px; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>RepoChat Migration Dashboard</h1>
            
            <div class="card">
                <h2>System Health</h2>
                <div id="status">Loading...</div>
                <div id="recommendations"></div>
            </div>
            
            <div class="card">
                <h2>Migration Status</h2>
                <div id="migration-info">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Performance Metrics</h2>
                <div id="metrics">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Controls</h2>
                <button onclick="advancePhase()">Advance Phase</button>
                <button onclick="rollbackPhase()">Rollback Phase</button>
                <button onclick="enableMigration()">Enable Migration</button>
                <button onclick="disableMigration()">Disable Migration</button>
            </div>
            
            <script>
                const ws = new WebSocket('ws://localhost:8080/ws');
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                };
                
                function updateDashboard(data) {
                    // Update health status
                    const health = data.health;
                    document.getElementById('status').textContent = 'Status: ' + health.status.toUpperCase();
                    document.getElementById('status').className = health.status;
                    
                    // Update recommendations
                    const recommendations = health.recommendations.map(r => '<li>' + r + '</li>').join('');
                    document.getElementById('recommendations').innerHTML = '<ul>' + recommendations + '</ul>';
                    
                    // Update migration info
                    const migration = data.metrics.migration;
                    document.getElementById('migration-info').innerHTML = 
                        '<p>Phase: ' + migration.phase + '</p>' +
                        '<p>Enhanced Traffic: ' + migration.enhanced_traffic_percentage + '%</p>' +
                        '<p>Circuit Breaker: ' + (migration.circuit_breaker_open ? 'OPEN' : 'CLOSED') + '</p>';
                    
                    // Update metrics
                    let metricsHtml = '';
                    if (migration.legacy.requests > 0) {
                        metricsHtml += '<div class="metric"><h4>Legacy</h4>' +
                            '<p>Success: ' + (migration.legacy.success_rate * 100).toFixed(1) + '%</p>' +
                            '<p>Avg Time: ' + migration.legacy.average_time.toFixed(2) + 's</p>' +
                            '<p>Requests: ' + migration.legacy.requests + '</p></div>';
                    }
                    if (migration.enhanced.requests > 0) {
                        metricsHtml += '<div class="metric"><h4>Enhanced</h4>' +
                            '<p>Success: ' + (migration.enhanced.success_rate * 100).toFixed(1) + '%</p>' +
                            '<p>Avg Time: ' + migration.enhanced.average_time.toFixed(2) + 's</p>' +
                            '<p>Requests: ' + migration.enhanced.requests + '</p>' +
                            '<p>Ratio: ' + migration.enhanced.performance_ratio.toFixed(2) + 'x</p></div>';
                    }
                    document.getElementById('metrics').innerHTML = metricsHtml;
                }
                
                function advancePhase() {
                    fetch('/migration/advance', {method: 'POST'}).then(r => r.json()).then(console.log);
                }
                
                function rollbackPhase() {
                    fetch('/migration/rollback', {method: 'POST'}).then(r => r.json()).then(console.log);
                }
                
                function enableMigration() {
                    fetch('/migration/enable', {method: 'POST'}).then(r => r.json()).then(console.log);
                }
                
                function disableMigration() {
                    fetch('/migration/disable', {method: 'POST'}).then(r => r.json()).then(console.log);
                }
            </script>
        </body>
        </html>
        """

    async def run_dashboard(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Run the monitoring dashboard server.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        await self.start_monitoring()
        
        config = uvicorn.Config(self.app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        
        try:
            await server.serve()
        finally:
            await self.stop_monitoring() 