#!/usr/bin/env python3
"""
Main entry point for Scalable AI API System on Render.

This module provides the main entry point for running different components
of the system on Render cloud platform.
"""

import argparse
import logging
import os
import sys
from typing import Optional

from scalable_ai_api.ai_server.server_runner import run_server
from scalable_ai_api.load_balancer.render_app import create_load_balancer_app


def setup_logging(level: str = "INFO"):
    """Setup logging configuration for Render."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def run_load_balancer(host: str = "0.0.0.0", port: int = 8000):
    """Run the load balancer component."""
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Load Balancer on {host}:{port}")
    
    try:
        app = create_load_balancer_app()
        
        # Use uvicorn to run the FastAPI app
        import uvicorn
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start Load Balancer: {e}")
        sys.exit(1)


def run_ai_server_component(
    server_id: str,
    host: str = "0.0.0.0", 
    port: int = 8080
):
    """Run an AI server component."""
    logger = logging.getLogger(__name__)
    logger.info(f"Starting AI Server {server_id} on {host}:{port}")
    
    try:
        run_server(
            server_id=server_id,
            host=host,
            port=port,
            log_level="INFO"
        )
    except Exception as e:
        logger.error(f"Failed to start AI Server {server_id}: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scalable AI API System")
    parser.add_argument(
        "--component",
        choices=["load_balancer", "ai_server"],
        required=True,
        help="Component to run"
    )
    parser.add_argument(
        "--server-id",
        help="Server ID for AI server component"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to listen on (defaults from environment PORT or component default)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Get port from environment (Render sets PORT) or use provided/default
    port = args.port or int(os.environ.get("PORT", 8000))
    
    if args.component == "load_balancer":
        run_load_balancer(host=args.host, port=port)
    elif args.component == "ai_server":
        if not args.server_id:
            # Try to get from environment
            server_id = os.environ.get("SERVER_ID")
            if not server_id:
                print("Error: --server-id is required for ai_server component")
                sys.exit(1)
        else:
            server_id = args.server_id
        
        run_ai_server_component(
            server_id=server_id,
            host=args.host,
            port=port
        )


if __name__ == "__main__":
    main()