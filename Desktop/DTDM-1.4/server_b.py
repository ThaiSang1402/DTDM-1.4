#!/usr/bin/env python3
"""
Server B Instance - Scalable AI API System

This script creates and runs the Server B instance as specified in Task 2.4.
Server B runs on port 8081 and clearly identifies itself in all responses.

Requirements addressed:
- 2.1: Deploy exactly 2 AI server instances initially (Server A and Server B)
- 2.2: When Server B processes a request, return response clearly identifying "Server B"
"""

import logging
import sys
import signal
from scalable_ai_api.ai_server.base_server import BaseAIServer


def setup_logging():
    """Setup logging for Server B."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('server_b.log')
        ]
    )


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger = logging.getLogger(__name__)
    logger.info("Received shutdown signal, stopping Server B...")
    sys.exit(0)


def main():
    """Main function to run Server B instance."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Server B configuration
    SERVER_ID = "Server B"
    HOST = "0.0.0.0"
    PORT = 8081
    
    logger.info(f"Initializing {SERVER_ID} on {HOST}:{PORT}")
    
    try:
        # Create and start Server B instance
        server_b = BaseAIServer(
            server_id=SERVER_ID,
            host=HOST,
            port=PORT
        )
        
        logger.info(f"{SERVER_ID} initialized successfully")
        logger.info(f"Server will identify itself as '{SERVER_ID}' in all responses")
        logger.info(f"Health check available at: http://{HOST}:{PORT}/health")
        logger.info(f"Server info available at: http://{HOST}:{PORT}/info")
        logger.info(f"AI API endpoint available at: http://{HOST}:{PORT}/api/ai")
        
        # Start the server (this will block until shutdown)
        server_b.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down Server B...")
    except Exception as e:
        logger.error(f"Failed to start {SERVER_ID}: {e}")
        sys.exit(1)
    finally:
        logger.info(f"{SERVER_ID} shutdown complete")


if __name__ == "__main__":
    main()