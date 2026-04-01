"""
FastAPI application for Load Balancer on Render.

This module creates a FastAPI application that wraps the Load Balancer
core functionality for deployment on Render.
"""

import logging
import os
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core import LoadBalancerCore
from ..models import ServerInstance, AIRequest, ServerStatus


# Global load balancer instance
load_balancer: Optional[LoadBalancerCore] = None


def create_load_balancer_app() -> FastAPI:
    """Create and configure the FastAPI application for Load Balancer."""
    app = FastAPI(
        title="Scalable AI API Load Balancer",
        description="Load Balancer for Scalable AI API System",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup logging
    logger = logging.getLogger("load_balancer_app")
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize load balancer on startup."""
        global load_balancer
        
        logger.info("Initializing Load Balancer...")
        
        # Create load balancer instance
        request_timeout = int(os.environ.get("REQUEST_TIMEOUT", "30"))
        max_retries = int(os.environ.get("MAX_RETRIES", "3"))
        
        load_balancer = LoadBalancerCore(
            request_timeout=request_timeout,
            max_retries=max_retries
        )
        
        # Add AI servers from environment
        server_a_url = os.environ.get("SERVER_A_URL", "http://localhost:8080")
        server_b_url = os.environ.get("SERVER_B_URL", "http://localhost:8081")
        
        # Parse URLs to get host and port
        import urllib.parse
        
        # Add Server A
        parsed_a = urllib.parse.urlparse(server_a_url)
        server_a = ServerInstance(
            id="Server A",
            ip_address=parsed_a.hostname or "localhost",
            port=parsed_a.port or (443 if parsed_a.scheme == "https" else 80),
            status=ServerStatus.HEALTHY
        )
        load_balancer.add_server(server_a)
        
        # Add Server B
        parsed_b = urllib.parse.urlparse(server_b_url)
        server_b = ServerInstance(
            id="Server B", 
            ip_address=parsed_b.hostname or "localhost",
            port=parsed_b.port or (443 if parsed_b.scheme == "https" else 80),
            status=ServerStatus.HEALTHY
        )
        load_balancer.add_server(server_b)
        
        logger.info(f"Load Balancer initialized with {len(load_balancer.get_current_server_pool())} servers")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        global load_balancer
        if load_balancer:
            load_balancer.shutdown()
            logger.info("Load Balancer shutdown complete")
    
    @app.middleware("http")
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
        response.headers["X-Load-Balancer"] = "Scalable-AI-API-LB"
        
        return response
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "service": "Scalable AI API Load Balancer",
            "status": "running",
            "version": "1.0.0"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        if not load_balancer:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": "Load balancer not initialized"
                }
            )
        
        try:
            health_status = load_balancer.get_health_status()
            status_code = 200 if health_status.status == ServerStatus.HEALTHY else 503
            
            return JSONResponse(
                status_code=status_code,
                content={
                    "status": health_status.status.value,
                    "message": health_status.message,
                    "details": health_status.details,
                    "timestamp": health_status.timestamp.isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": f"Health check failed: {str(e)}"
                }
            )
    
    @app.get("/status")
    async def status():
        """Get load balancer status and metrics."""
        if not load_balancer:
            raise HTTPException(status_code=503, detail="Load balancer not initialized")
        
        try:
            metrics = load_balancer.get_metrics()
            server_pool = load_balancer.get_current_server_pool()
            
            return {
                "load_balancer": {
                    "status": "running",
                    "server_count": len(server_pool),
                    "healthy_servers": len([s for s in server_pool if s.status == ServerStatus.HEALTHY])
                },
                "metrics": {
                    "total_requests": metrics.total_requests,
                    "requests_per_second": metrics.requests_per_second,
                    "average_response_time": metrics.average_response_time,
                    "error_rate": metrics.error_rate,
                    "server_distribution": metrics.server_distribution
                },
                "servers": [
                    {
                        "id": server.id,
                        "address": f"{server.ip_address}:{server.port}",
                        "status": server.status.value,
                        "request_count": server.request_count,
                        "response_time": server.response_time
                    }
                    for server in server_pool
                ]
            }
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
    
    @app.post("/api/ai")
    async def process_ai_request(request: Request, ai_request_data: Dict[str, Any]):
        """Process AI request through load balancer."""
        if not load_balancer:
            raise HTTPException(status_code=503, detail="Load balancer not initialized")
        
        correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
        
        try:
            # Validate request
            if not ai_request_data.get("prompt"):
                raise HTTPException(status_code=400, detail="Prompt is required")
            
            # Create AIRequest object
            ai_request = AIRequest(
                request_id=ai_request_data.get("request_id", str(uuid.uuid4())),
                client_id=ai_request_data.get("client_id", ""),
                prompt=ai_request_data.get("prompt", ""),
                parameters=ai_request_data.get("parameters", {}),
                correlation_id=correlation_id
            )
            
            # Route request through load balancer
            response = load_balancer.route_request(ai_request)
            
            # Check for errors
            if response.error_message:
                logger.error(f"Request routing failed: {response.error_message}")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "Service unavailable",
                        "message": response.error_message,
                        "correlation_id": correlation_id
                    }
                )
            
            # Return successful response
            return {
                "request_id": response.request_id,
                "server_id": response.server_id,
                "response_text": response.response_text,
                "processing_time": response.processing_time,
                "correlation_id": response.correlation_id,
                "timestamp": response.timestamp.isoformat(),
                "routed_by": "load_balancer"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing AI request: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Internal server error",
                    "message": str(e),
                    "correlation_id": correlation_id
                }
            )
    
    return app


# Create the ASGI app instance for Render
app = create_load_balancer_app()