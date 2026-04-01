"""
FastAPI application for AI Server on Render.

This module creates a FastAPI application that wraps the AI Server
functionality for deployment on Render.
"""

import os
from .base_server import BaseAIServer

# Get server ID from environment
server_id = os.environ.get("SERVER_ID", "AI Server")

# Create AI Server instance
ai_server = BaseAIServer(
    server_id=server_id,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080))
)

# Export the FastAPI app
app = ai_server.app