"""
Data models for the Scalable AI API System.

This module defines all the data structures used throughout the system
with proper validation and type hints.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import uuid


class ServerStatus(Enum):
    """Server status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"


class RequestPriority(Enum):
    """Request priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ScalingAction(Enum):
    """Auto scaling actions."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_CHANGE = "no_change"


@dataclass
class ServerInstance:
    """Represents a server instance in the system."""
    id: str
    ip_address: str
    port: int
    status: ServerStatus = ServerStatus.STARTING
    health_score: float = 1.0
    last_health_check: Optional[datetime] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_count: int = 0
    response_time: float = 0.0
    
    def __post_init__(self):
        """Validate server instance data."""
        if not self.id:
            raise ValueError("Server ID cannot be empty")
        if not self._is_valid_ip(self.ip_address):
            raise ValueError(f"Invalid IP address: {self.ip_address}")
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Port must be between 1-65535, got: {self.port}")
        if not (0.0 <= self.health_score <= 1.0):
            raise ValueError(f"Health score must be between 0.0-1.0, got: {self.health_score}")
    
    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """Validate IP address format."""
        # Allow localhost
        if ip.lower() == "localhost":
            return True
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except (ValueError, AttributeError):
            return False


@dataclass
class AIRequest:
    """Represents an AI request."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = ""
    prompt: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: RequestPriority = RequestPriority.NORMAL
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate AI request data."""
        if not self.request_id:
            raise ValueError("Request ID cannot be empty")
        if not self.prompt:
            raise ValueError("Prompt cannot be empty")


@dataclass
class AIResponse:
    """Represents an AI response."""
    request_id: str
    server_id: str
    response_text: str
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate AI response data."""
        if not self.request_id:
            raise ValueError("Request ID cannot be empty")
        if not self.server_id:
            raise ValueError("Server ID cannot be empty")
        if self.processing_time < 0:
            raise ValueError("Processing time cannot be negative")


@dataclass
class HealthStatus:
    """Represents health status of a component."""
    status: ServerStatus
    response_time: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadBalancerMetrics:
    """Metrics collected by the load balancer."""
    total_requests: int = 0
    requests_per_second: float = 0.0
    average_response_time: float = 0.0
    error_rate: float = 0.0
    active_connections: int = 0
    server_distribution: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate load balancer metrics."""
        if self.total_requests < 0:
            raise ValueError("Total requests cannot be negative")
        if not (0.0 <= self.error_rate <= 1.0):
            raise ValueError("Error rate must be between 0.0-1.0")
        if self.active_connections < 0:
            raise ValueError("Active connections cannot be negative")


@dataclass
class ScalingPolicy:
    """Auto scaling policy configuration."""
    min_instances: int = 2
    max_instances: int = 10
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 30.0
    cooldown_period: int = 300  # seconds
    metrics_window: int = 300   # seconds
    
    def __post_init__(self):
        """Validate scaling policy."""
        if self.min_instances < 1:
            raise ValueError("Minimum instances must be >= 1")
        if self.max_instances < self.min_instances:
            raise ValueError("Maximum instances must be >= minimum instances")
        if self.scale_up_threshold <= self.scale_down_threshold:
            raise ValueError("Scale up threshold must be > scale down threshold")


@dataclass
class ScalingDecision:
    """Represents an auto scaling decision."""
    action: ScalingAction
    target_instances: int
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    metrics_snapshot: Dict[str, float] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """System performance report."""
    throughput: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    error_rate: float
    server_utilization: Dict[str, float]
    bottlenecks: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SystemConfiguration:
    """System-wide configuration."""
    load_balancer_port: int = 8000
    health_check_interval: int = 30
    health_check_timeout: int = 5
    request_timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    scaling_policy: ScalingPolicy = field(default_factory=ScalingPolicy)
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Validate system configuration."""
        if not (1 <= self.load_balancer_port <= 65535):
            raise ValueError("Load balancer port must be between 1-65535")
        if self.health_check_interval <= 0:
            raise ValueError("Health check interval must be positive")
        if self.health_check_timeout <= 0:
            raise ValueError("Health check timeout must be positive")
        if self.request_timeout <= 0:
            raise ValueError("Request timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
        if self.retry_backoff_factor <= 0:
            raise ValueError("Retry backoff factor must be positive")