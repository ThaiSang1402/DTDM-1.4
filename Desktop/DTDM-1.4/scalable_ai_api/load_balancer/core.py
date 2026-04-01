"""
Load Balancer core implementation with Round Robin algorithm.

This module implements the core Load Balancer functionality including:
- Round Robin request distribution
- Server health tracking and dynamic pool management
- Request forwarding with connection pooling
- Health-aware routing
"""

import logging
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scalable_ai_api.interfaces import LoadBalancerInterface
from scalable_ai_api.models import (
    ServerInstance, AIRequest, AIResponse, HealthStatus, 
    LoadBalancerMetrics, ServerStatus
)


class LoadBalancerCore(LoadBalancerInterface):
    """Core Load Balancer implementation with Round Robin algorithm."""
    
    def __init__(self, request_timeout: int = 30, max_retries: int = 3):
        """Initialize the Load Balancer.
        
        Args:
            request_timeout: Timeout for requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.server_pool: List[ServerInstance] = []
        self.last_server_index = -1
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        
        # Thread safety
        self._pool_lock = threading.RLock()
        
        # Metrics tracking
        self.metrics = LoadBalancerMetrics()
        self._metrics_lock = threading.Lock()
        
        # Setup logging
        self.logger = logging.getLogger("load_balancer")
        self.logger.setLevel(logging.INFO)
        
        # Setup HTTP session with connection pooling
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=2.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,
            pool_maxsize=20
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.logger.info("Load Balancer initialized with Round Robin algorithm")
    
    def route_request(self, request: AIRequest) -> AIResponse:
        """Route request to next available server using Round Robin algorithm.
        
        Args:
            request: The AI request to route
            
        Returns:
            AIResponse from the selected server
            
        Raises:
            Exception: If no healthy servers are available
        """
        start_time = time.time()
        
        with self._pool_lock:
            healthy_servers = [s for s in self.server_pool if s.status == ServerStatus.HEALTHY]
            
            if not healthy_servers:
                self._update_metrics_error()
                processing_time = time.time() - start_time
                self.logger.error("No healthy servers available for request routing")
                
                return AIResponse(
                    request_id=request.request_id,
                    server_id="load_balancer",
                    response_text="",
                    processing_time=processing_time,
                    correlation_id=request.correlation_id,
                    error_message="No healthy servers available"
                )
            
            # Round Robin selection
            server = self._select_next_server(healthy_servers)
            
        try:
            # Forward request to selected server
            response = self._forward_request(server, request)
            
            # Update metrics for successful request
            processing_time = time.time() - start_time
            self._update_metrics_success(server.id, processing_time)
            
            self.logger.info(
                f"Routed request {request.request_id} to {server.id} "
                f"in {processing_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(
                f"Failed to route request {request.request_id} to {server.id}: {e}"
            )
            
            # Mark server as potentially unhealthy if request fails
            self._handle_server_error(server)
            
            # Update error metrics
            self._update_metrics_error()
            
            # Return error response
            return AIResponse(
                request_id=request.request_id,
                server_id="load_balancer",
                response_text="",
                processing_time=processing_time,
                correlation_id=request.correlation_id,
                error_message=f"Request routing failed: {str(e)}"
            )
    
    def _select_next_server(self, healthy_servers: List[ServerInstance]) -> ServerInstance:
        """Select next server using Round Robin algorithm.
        
        Args:
            healthy_servers: List of healthy servers to choose from
            
        Returns:
            Selected server instance
        """
        if not healthy_servers:
            raise Exception("No healthy servers available for selection")
        
        # Find the next server in round robin order
        # We need to map from the healthy servers list to the original pool indices
        server_indices = []
        for server in healthy_servers:
            try:
                original_index = self.server_pool.index(server)
                server_indices.append((original_index, server))
            except ValueError:
                # Server not in pool anymore, skip
                continue
        
        if not server_indices:
            raise Exception("No valid servers found in pool")
        
        # Sort by original index to maintain consistent ordering
        server_indices.sort(key=lambda x: x[0])
        
        # Find next server after last_server_index
        selected_server = None
        for original_index, server in server_indices:
            if original_index > self.last_server_index:
                selected_server = server
                self.last_server_index = original_index
                break
        
        # If no server found after last_server_index, wrap around to first
        if selected_server is None:
            selected_server = server_indices[0][1]
            self.last_server_index = server_indices[0][0]
        
        return selected_server
    
    def _forward_request(self, server: ServerInstance, request: AIRequest) -> AIResponse:
        """Forward request to the specified server.
        
        Args:
            server: Target server instance
            request: Request to forward
            
        Returns:
            Response from the server
        """
        url = f"http://{server.ip_address}:{server.port}/api/ai"
        
        headers = {
            "Content-Type": "application/json",
            "X-Correlation-ID": request.correlation_id or "",
            "X-Request-ID": request.request_id
        }
        
        payload = {
            "request_id": request.request_id,
            "client_id": request.client_id,
            "prompt": request.prompt,
            "parameters": request.parameters
        }
        
        try:
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.request_timeout
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Update server metrics
            server.request_count += 1
            server.response_time = response_data.get("processing_time", 0.0)
            
            return AIResponse(
                request_id=response_data.get("request_id", request.request_id),
                server_id=response_data.get("server_id", server.id),
                response_text=response_data.get("response_text", ""),
                processing_time=response_data.get("processing_time", 0.0),
                correlation_id=response_data.get("correlation_id", request.correlation_id)
            )
            
        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout after {self.request_timeout}s")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Connection failed to {server.ip_address}:{server.port}")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Request forwarding failed: {str(e)}")
    
    def _handle_server_error(self, server: ServerInstance):
        """Handle server error by potentially marking it as unhealthy.
        
        Args:
            server: Server that encountered an error
        """
        # For now, we don't immediately mark servers as unhealthy on single errors
        # This will be handled by the health checker component
        self.logger.warning(f"Server {server.id} encountered an error")
    
    def add_server(self, server: ServerInstance) -> bool:
        """Add server to the server pool.
        
        Args:
            server: Server instance to add
            
        Returns:
            True if server was added successfully
        """
        try:
            with self._pool_lock:
                # Check if server already exists
                existing_server = next(
                    (s for s in self.server_pool if s.id == server.id), 
                    None
                )
                
                if existing_server:
                    self.logger.warning(f"Server {server.id} already exists in pool")
                    return False
                
                # Add server to pool
                self.server_pool.append(server)
                
                # Initialize server distribution metrics
                with self._metrics_lock:
                    self.metrics.server_distribution[server.id] = 0
                
                self.logger.info(
                    f"Added server {server.id} ({server.ip_address}:{server.port}) to pool. "
                    f"Pool size: {len(self.server_pool)}"
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to add server {server.id}: {e}")
            return False
    
    def remove_server(self, server_id: str) -> bool:
        """Remove server from the server pool.
        
        Args:
            server_id: ID of server to remove
            
        Returns:
            True if server was removed successfully
        """
        try:
            with self._pool_lock:
                # Find and remove server
                server_to_remove = None
                for i, server in enumerate(self.server_pool):
                    if server.id == server_id:
                        server_to_remove = self.server_pool.pop(i)
                        break
                
                if server_to_remove is None:
                    self.logger.warning(f"Server {server_id} not found in pool")
                    return False
                
                # Adjust last_server_index if necessary
                if i <= self.last_server_index:
                    self.last_server_index -= 1
                
                # Reset if pool is empty or index is invalid
                if not self.server_pool or self.last_server_index >= len(self.server_pool):
                    self.last_server_index = -1
                
                # Remove from metrics
                with self._metrics_lock:
                    self.metrics.server_distribution.pop(server_id, None)
                
                self.logger.info(
                    f"Removed server {server_id} from pool. "
                    f"Pool size: {len(self.server_pool)}"
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to remove server {server_id}: {e}")
            return False
    
    def get_health_status(self) -> HealthStatus:
        """Get current health status of the load balancer.
        
        Returns:
            HealthStatus indicating load balancer health
        """
        try:
            with self._pool_lock:
                healthy_count = sum(
                    1 for s in self.server_pool 
                    if s.status == ServerStatus.HEALTHY
                )
                total_count = len(self.server_pool)
            
            if total_count == 0:
                status = ServerStatus.UNHEALTHY
                message = "No servers in pool"
            elif healthy_count == 0:
                status = ServerStatus.UNHEALTHY
                message = f"No healthy servers (0/{total_count})"
            elif healthy_count < total_count:
                status = ServerStatus.HEALTHY
                message = f"Partially healthy ({healthy_count}/{total_count} servers)"
            else:
                status = ServerStatus.HEALTHY
                message = f"All servers healthy ({healthy_count}/{total_count})"
            
            return HealthStatus(
                status=status,
                response_time=0.0,  # Load balancer doesn't have response time
                message=message,
                details={
                    "total_servers": total_count,
                    "healthy_servers": healthy_count,
                    "total_requests": self.metrics.total_requests,
                    "error_rate": self.metrics.error_rate
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get health status: {e}")
            return HealthStatus(
                status=ServerStatus.UNHEALTHY,
                response_time=-1.0,
                message=f"Health check failed: {str(e)}"
            )
    
    def get_current_server_pool(self) -> List[ServerInstance]:
        """Get list of current servers in the pool.
        
        Returns:
            Copy of current server pool
        """
        with self._pool_lock:
            return self.server_pool.copy()
    
    def get_metrics(self) -> LoadBalancerMetrics:
        """Get current load balancer metrics.
        
        Returns:
            Current metrics snapshot
        """
        with self._metrics_lock:
            return LoadBalancerMetrics(
                total_requests=self.metrics.total_requests,
                requests_per_second=self.metrics.requests_per_second,
                average_response_time=self.metrics.average_response_time,
                error_rate=self.metrics.error_rate,
                active_connections=self.metrics.active_connections,
                server_distribution=self.metrics.server_distribution.copy(),
                timestamp=datetime.now()
            )
    
    def _update_metrics_success(self, server_id: str, processing_time: float):
        """Update metrics for successful request.
        
        Args:
            server_id: ID of server that processed the request
            processing_time: Time taken to process the request
        """
        with self._metrics_lock:
            self.metrics.total_requests += 1
            
            # Update server distribution
            if server_id not in self.metrics.server_distribution:
                self.metrics.server_distribution[server_id] = 0
            self.metrics.server_distribution[server_id] += 1
            
            # Update average response time
            total_time = (self.metrics.average_response_time * 
                         (self.metrics.total_requests - 1) + processing_time)
            self.metrics.average_response_time = total_time / self.metrics.total_requests
            
            # Update error rate (successful request decreases error rate)
            error_count = self.metrics.error_rate * self.metrics.total_requests
            self.metrics.error_rate = error_count / self.metrics.total_requests
    
    def _update_metrics_error(self):
        """Update metrics for failed request."""
        with self._metrics_lock:
            self.metrics.total_requests += 1
            
            # Update error rate
            error_count = self.metrics.error_rate * (self.metrics.total_requests - 1) + 1
            self.metrics.error_rate = error_count / self.metrics.total_requests
    
    def shutdown(self):
        """Shutdown the load balancer and cleanup resources."""
        try:
            self.logger.info("Shutting down Load Balancer...")
            
            # Close HTTP session
            if hasattr(self, 'session'):
                self.session.close()
            
            self.logger.info("Load Balancer shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")