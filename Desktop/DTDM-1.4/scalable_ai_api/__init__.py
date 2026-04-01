"""
Scalable AI API System

A production-ready AI API system with load balancing, auto-scaling,
and comprehensive monitoring capabilities.
"""

__version__ = "1.0.0"
__author__ = "Scalable AI API Team"

# Make key components easily importable
from scalable_ai_api.models import (
    AIRequest,
    AIResponse,
    ServerInstance,
    ServerStatus,
    HealthStatus,
    LoadBalancerMetrics
)

from scalable_ai_api.interfaces import (
    AIServerInterface,
    LoadBalancerInterface
)

__all__ = [
    "AIRequest",
    "AIResponse", 
    "ServerInstance",
    "ServerStatus",
    "HealthStatus",
    "LoadBalancerMetrics",
    "AIServerInterface",
    "LoadBalancerInterface"
]