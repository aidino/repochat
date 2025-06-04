"""
Logging Configuration for RepoChat v1.0

Provides centralized logging setup for all components.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    logger_name: str = "repochat"
) -> logging.Logger:
    """
    Set up logging configuration for RepoChat.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        logger_name: Name of the logger
        
    Returns:
        Configured logger instance
    """
    
    # Default format if none provided
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(module)s.%(funcName)s:%(lineno)d - %(message)s"
        )
    
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the standard RepoChat configuration.
    
    Args:
        name: Name for the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"repochat.{name}")


# Create the main RepoChat logger
main_logger = setup_logging() 