"""
Server runner for AI Server instances.

This module provides utilities to run AI Server instances with different configurations.
"""

import argparse
import logging
import sys
from typing import Optional

from scalable_ai_api.ai_server.base_server import BaseAIServer


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('ai_server.log')
        ]
    )


def run_server(
    server_id: str,
    host: str = "0.0.0.0",
    port: int = 8080,
    log_level: str = "INFO"
):
    """Run an AI Server instance.
    
    Args:
        server_id: Unique identifier for the server
        host: Host address to bind to
        port: Port number to listen on
        log_level: Logging level
    """
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting AI Server {server_id} on {host}:{port}")
    
    try:
        server = BaseAIServer(server_id=server_id, host=host, port=port)
        server.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)


def main():
    """Main entry point for server runner."""
    parser = argparse.ArgumentParser(description="Run AI Server instance")
    parser.add_argument(
        "--server-id",
        required=True,
        help="Unique server identifier (e.g., 'Server A', 'Server B')"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port number to listen on (default: 8080)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    run_server(
        server_id=args.server_id,
        host=args.host,
        port=args.port,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()