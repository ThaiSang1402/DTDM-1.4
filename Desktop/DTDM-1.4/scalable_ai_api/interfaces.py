"""
Core interfaces for the Scalable AI API System.

This module defines the abstract interfaces that all components must implement
to ensure consistent behavior across the system.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from scalable_ai_api.models import (
    ServerInstance, AIRequest, AIResponse, HealthStatus, 
    LoadBalancerMetrics, ScalingDecision, PerformanceReport
)


class LoadBalancerInterface(ABC):
    """Interface for Load Balancer implementations."""
    
    @abstractmethod
    def route_request(self, request: AIRequest) -> AIResponse:
        """Route request to next available server using Round Robin algorithm."""
        pass
    
    @abstractmethod
    def add_server(self, server: ServerInstance) -> bool:
        """Add server to the server pool."""
        pass
    
    @abstractmethod
    def remove_server(self, server_id: str) -> bool:
        """Remove server from the server pool."""
        pass
    
    @abstractmethod
    def get_health_status(self) -> HealthStatus:
        """Get current health status of the load balancer."""
        pass
    
    @abstractmethod
    def get_current_server_pool(self) -> List[ServerInstance]:
        """Get list of current servers in the pool."""
        pass


class AIServerInterface(ABC):
    """Interface for AI Server implementations."""
    
    @abstractmethod
    def process_ai_request(self, request: AIRequest) -> AIResponse:
        """Process AI request and return response with server identification."""
        pass
    
    @abstractmethod
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information including ID and status."""
        pass
    
    @abstractmethod
    def get_health_metrics(self) -> Dict[str, float]:
        """Get current health metrics (CPU, memory, etc.)."""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Gracefully shutdown the server."""
        pass


class MonitoringSystemInterface(ABC):
    """Interface for Monitoring System implementations."""
    
    @abstractmethod
    def collect_metrics(self, source: str) -> Dict[str, Any]:
        """Collect metrics from specified source."""
        pass
    
    @abstractmethod
    def analyze_performance(self) -> PerformanceReport:
        """Analyze system performance and generate report."""
        pass
    
    @abstractmethod
    def trigger_alert(self, condition: str, message: str) -> bool:
        """Trigger alert for specified condition."""
        pass
    
    @abstractmethod
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive system report."""
        pass


class AutoScalingControllerInterface(ABC):
    """Interface for Auto Scaling Controller implementations."""
    
    @abstractmethod
    def evaluate_scaling_need(self) -> ScalingDecision:
        """Evaluate if scaling is needed based on current metrics."""
        pass
    
    @abstractmethod
    def scale_up(self, target_count: int) -> bool:
        """Scale up to target server count."""
        pass
    
    @abstractmethod
    def scale_down(self, target_count: int) -> bool:
        """Scale down to target server count."""
        pass
    
    @abstractmethod
    def set_scaling_policy(self, policy: Dict[str, Any]) -> bool:
        """Set scaling policy parameters."""
        pass


class HealthCheckerInterface(ABC):
    """Interface for Health Checker implementations."""
    
    @abstractmethod
    def perform_health_check(self, server: ServerInstance) -> HealthStatus:
        """Perform health check on specified server."""
        pass
    
    @abstractmethod
    def start_monitoring(self, servers: List[ServerInstance]) -> bool:
        """Start continuous health monitoring for servers."""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> bool:
        """Stop health monitoring."""
        pass