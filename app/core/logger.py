import logging
import sys
from typing import Any

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger("opendoge")

# Set level based on environment (can be configured via settings later)
logger.setLevel(logging.INFO)

def log_error(error: Any) -> None:
    """Log error messages with stack trace"""
    logger.error(f"Error: {str(error)}", exc_info=True)

def log_warning(message: str) -> None:
    """Log warning messages"""
    logger.warning(message)

def log_info(message: str) -> None:
    """Log info messages"""
    logger.info(message)

def log_debug(message: str) -> None:
    """Log debug messages"""
    logger.debug(message) 