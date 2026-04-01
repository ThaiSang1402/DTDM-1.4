"""
FastAPI application for AI Server on Render.

This module creates a FastAPI application that wraps the AI Server
functionality for deployment on Render.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get server ID from environment
server_id = os.environ.get("SERVER_ID", "AI Server")

# Create FastAPI app
app = FastAPI(
    title=f"AI Server {server_id}",
    description=f"Scalable AI API Server Instance - {server_id}",
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

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": f"AI Server {server_id}",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server_id": server_id,
        "message": "AI Server is running"
    }

@app.get("/info")
async def server_info():
    """Get server information."""
    return {
        "server_id": server_id,
        "status": "healthy",
        "message": "AI Server information"
    }

@app.post("/api/ai")
async def process_ai_request(ai_request: dict):
    """Process AI request."""
    try:
        prompt = ai_request.get("prompt", "")
        if not prompt:
            return {"error": "Prompt is required"}
        
        # Simple AI response simulation
        response_text = f"AI Response from {server_id}: Processed prompt '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'"
        
        return {
            "request_id": ai_request.get("request_id", "default"),
            "server_id": server_id,
            "response_text": response_text,
            "processing_time": 0.1,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {
            "error": "Internal server error",
            "message": str(e),
            "server_id": server_id
        }