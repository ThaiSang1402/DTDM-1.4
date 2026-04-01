"""
Base AI Server implementation using FastAPI.

This module implements the core AI Server functionality with FastAPI,
including health checks, server identification, correlation tracking,
and error handling.
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import psutil
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from scalable_ai_api.interfaces import AIServerInterface
from scalable_ai_api.models import AIRequest, AIResponse, ServerStatus


class BaseAIServer(AIServerInterface):
    """Base AI Server implementation with FastAPI."""
    
    def __init__(self, server_id: str, host: str = "0.0.0.0", port: int = 8080):
        """Initialize the AI Server.
        
        Args:
            server_id: Unique identifier for this server instance
            host: Host address to bind to
            port: Port number to listen on
        """
        self.server_id = server_id
        self.host = host
        self.port = port
        self.status = ServerStatus.STARTING
        self.start_time = datetime.now()
        
        # Setup logging
        self.logger = logging.getLogger(f"ai_server_{server_id}")
        self.logger.setLevel(logging.INFO)
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title=f"AI Server {server_id}",
            description=f"Scalable AI API Server Instance - {server_id}",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        # Request metrics
        self.request_count = 0
        self.total_processing_time = 0.0
        
        self.logger.info(f"AI Server {server_id} initialized on {host}:{port}")
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.middleware("http")
        async def add_correlation_id(request: Request, call_next):
            """Add correlation ID to all requests."""
            # Get correlation ID from header or generate new one
            correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
            
            # Add to request state
            request.state.correlation_id = correlation_id
            
            # Process request
            response = await call_next(request)
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Server-ID"] = self.server_id
            
            return response
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            try:
                health_metrics = self.get_health_metrics()
                
                # Determine health status based on metrics
                cpu_usage = health_metrics.get("cpu_usage", 0)
                memory_usage = health_metrics.get("memory_usage", 0)
                
                # More lenient health check for development/testing
                is_healthy = (
                    self.status in [ServerStatus.HEALTHY, ServerStatus.STARTING] and
                    cpu_usage < 99.0 and  # Very high threshold for CPU
                    memory_usage < 99.0   # Very high threshold for memory
                )
                
                status_code = 200 if is_healthy else 503
                
                return JSONResponse(
                    status_code=status_code,
                    content={
                        "status": "healthy" if is_healthy else "unhealthy",
                        "server_id": self.server_id,
                        "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                        "metrics": health_metrics,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "server_id": self.server_id,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                )
        
        @self.app.get("/info")
        async def server_info():
            """Get server information."""
            return {
                "server_id": self.server_id,
                "host": self.host,
                "port": self.port,
                "status": self.status.value,
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "request_count": self.request_count,
                "average_processing_time": (
                    self.total_processing_time / self.request_count 
                    if self.request_count > 0 else 0.0
                )
            }
        
        @self.app.post("/api/ai")
        async def process_request(request: Request, ai_request: dict):
            """Process AI request."""
            start_time = time.time()
            correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
            
            try:
                # Validate request
                if not ai_request.get("prompt"):
                    raise HTTPException(
                        status_code=400,
                        detail="Prompt is required"
                    )
                
                # Create AIRequest object
                ai_req = AIRequest(
                    request_id=ai_request.get("request_id", str(uuid.uuid4())),
                    client_id=ai_request.get("client_id", ""),
                    prompt=ai_request.get("prompt", ""),
                    parameters=ai_request.get("parameters", {}),
                    correlation_id=correlation_id
                )
                
                # Process the request
                response = self.process_ai_request(ai_req)
                
                # Update metrics
                processing_time = time.time() - start_time
                self.request_count += 1
                self.total_processing_time += processing_time
                
                self.logger.info(
                    f"Processed request {ai_req.request_id} in {processing_time:.3f}s "
                    f"(correlation: {correlation_id})"
                )
                
                return {
                    "request_id": response.request_id,
                    "server_id": response.server_id,
                    "response_text": response.response_text,
                    "processing_time": response.processing_time,
                    "correlation_id": response.correlation_id,
                    "timestamp": response.timestamp.isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                processing_time = time.time() - start_time
                self.logger.error(
                    f"Error processing request: {e} "
                    f"(correlation: {correlation_id})"
                )
                
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Internal server error",
                        "message": str(e),
                        "server_id": self.server_id,
                        "correlation_id": correlation_id,
                        "processing_time": processing_time
                    }
                )
    
    def process_ai_request(self, request: AIRequest) -> AIResponse:
        """Process AI request and return response with server identification.
        
        Args:
            request: The AI request to process
            
        Returns:
            AIResponse with server identification and processing details
        """
        start_time = time.time()
        
        try:
            # Simulate AI processing (replace with actual AI logic)
            response_text = self._generate_ai_response(request.prompt, request.parameters)
            
            processing_time = time.time() - start_time
            
            # Create response with server identification
            response = AIResponse(
                request_id=request.request_id,
                server_id=self.server_id,
                response_text=response_text,
                processing_time=processing_time,
                correlation_id=request.correlation_id
            )
            
            self.logger.debug(
                f"Generated AI response for request {request.request_id} "
                f"in {processing_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"AI processing failed: {e}")
            
            return AIResponse(
                request_id=request.request_id,
                server_id=self.server_id,
                response_text="",
                processing_time=processing_time,
                correlation_id=request.correlation_id,
                error_message=str(e)
            )
    
    def _generate_ai_response(self, prompt: str, parameters: Dict[str, Any]) -> str:
        """Generate AI response (placeholder implementation).
        
        Args:
            prompt: The input prompt
            parameters: Additional parameters for AI processing
            
        Returns:
            Generated response text
        """
        # Simulate processing time based on prompt length
        import time
        processing_delay = min(len(prompt) * 0.001, 0.5)  # Max 0.5s delay
        time.sleep(processing_delay)
        
        # Generate response with server identification
        response = (
            f"AI Response from {self.server_id}: "
            f"Processed prompt '{prompt[:50]}{'...' if len(prompt) > 50 else ''}' "
            f"with parameters {parameters}"
        )
        
        return response
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information including ID and status.
        
        Returns:
            Dictionary containing server information
        """
        return {
            "server_id": self.server_id,
            "host": self.host,
            "port": self.port,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "request_count": self.request_count,
            "average_processing_time": (
                self.total_processing_time / self.request_count 
                if self.request_count > 0 else 0.0
            )
        }
    
    def get_health_metrics(self) -> Dict[str, float]:
        """Get current health metrics (CPU, memory, etc.).
        
        Returns:
            Dictionary containing health metrics
        """
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_usage": disk.percent,
                "process_memory_mb": process_memory.rss / (1024 * 1024),
                "request_count": float(self.request_count),
                "average_response_time": (
                    self.total_processing_time / self.request_count 
                    if self.request_count > 0 else 0.0
                )
            }
        except Exception as e:
            self.logger.error(f"Failed to collect health metrics: {e}")
            return {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "memory_available_mb": 0.0,
                "disk_usage": 0.0,
                "process_memory_mb": 0.0,
                "request_count": float(self.request_count),
                "average_response_time": 0.0
            }
    
    def shutdown(self) -> bool:
        """Gracefully shutdown the server.
        
        Returns:
            True if shutdown was successful
        """
        try:
            self.status = ServerStatus.STOPPING
            self.logger.info(f"AI Server {self.server_id} shutting down...")
            
            # Perform cleanup operations here
            # (close connections, save state, etc.)
            
            self.status = ServerStatus.UNHEALTHY
            self.logger.info(f"AI Server {self.server_id} shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False
    
    def start(self):
        """Start the FastAPI server."""
        try:
            self.status = ServerStatus.HEALTHY
            self.logger.info(f"Starting AI Server {self.server_id} on {self.host}:{self.port}")
            
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            self.status = ServerStatus.UNHEALTHY
            raise