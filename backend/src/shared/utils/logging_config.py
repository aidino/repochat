"""
Enhanced Logging Configuration for RepoChat v1.0

Provides centralized logging setup for all components with extensive debugging capabilities.
Supports both console and file logging with structured format for better debugging.
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that provides structured logging output
    with detailed context information for debugging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information."""
        
        # Base log data
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add process and thread info for debugging
        log_data['process_id'] = os.getpid()
        log_data['thread_id'] = record.thread if hasattr(record, 'thread') else None
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
            
        # For console output, use human-readable format
        if getattr(self, 'is_console', False):
            return (
                f"{log_data['timestamp']} | {log_data['level']:<8} | "
                f"{log_data['logger']:<20} | {log_data['module']}.{log_data['function']}:{log_data['line']} | "
                f"{log_data['message']}"
                f"{' | Exception: ' + log_data['exception'] if 'exception' in log_data else ''}"
            )
        
        # For file output, use JSON format for structured logging
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: str = "DEBUG",
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    log_file: Optional[str] = None,
    logger_name: str = "repochat",
    max_file_size: int = 50 * 1024 * 1024,  # 50MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up comprehensive logging configuration for RepoChat.
    
    Args:
        level: Base logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_level: Logging level for console output
        file_level: Logging level for file output
        log_file: Path to log file (auto-generated if None)
        logger_name: Name of the logger
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Generate log file path if not provided
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"repochat_{timestamp}.log"
    else:
        log_file = Path(log_file)
    
    # Console Handler with human-readable format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, console_level.upper()))
    console_formatter = StructuredFormatter()
    console_formatter.is_console = True
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler with JSON structured format and rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, file_level.upper()))
    file_formatter = StructuredFormatter()
    file_formatter.is_console = False
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Debug Handler - separate file for debug-only logs
    debug_file = log_dir / f"repochat_debug_{datetime.now().strftime('%Y%m%d')}.log"
    debug_handler = logging.handlers.RotatingFileHandler(
        debug_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(file_formatter)
    logger.addHandler(debug_handler)
    
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False
    
    # Log the setup completion with system info
    logger.info("Logging system initialized", extra={
        'extra_data': {
            'console_level': console_level,
            'file_level': file_level,
            'log_file': str(log_file),
            'debug_file': str(debug_file),
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform,
                'cwd': os.getcwd(),
                'pid': os.getpid()
            }
        }
    })
    
    return logger


def get_logger(name: str, extra_context: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Get a logger with the standard RepoChat configuration and optional context.
    
    Args:
        name: Name for the logger (typically module name)
        extra_context: Additional context to include in all log messages
        
    Returns:
        Configured logger instance with enhanced capabilities
    """
    logger = logging.getLogger(f"repochat.{name}")
    
    # Add context to logger if provided
    if extra_context:
        logger = LoggerAdapter(logger, extra_context)
    
    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that adds extra context to all log messages.
    """
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process the log message and add extra context."""
        
        # Merge extra context
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        if 'extra_data' not in kwargs['extra']:
            kwargs['extra']['extra_data'] = {}
            
        kwargs['extra']['extra_data'].update(self.extra)
        
        return msg, kwargs


def log_function_entry(logger: logging.Logger, func_name: str, **kwargs) -> None:
    """
    Log function entry with parameters for debugging.
    
    Args:
        logger: Logger instance
        func_name: Name of the function being entered
        **kwargs: Function parameters to log
    """
    logger.debug(f"ENTER {func_name}", extra={
        'extra_data': {
            'function': func_name,
            'parameters': kwargs,
            'event_type': 'function_entry'
        }
    })


def log_function_exit(logger: logging.Logger, func_name: str, result: Any = None, 
                     execution_time: Optional[float] = None) -> None:
    """
    Log function exit with result and timing for debugging.
    
    Args:
        logger: Logger instance
        func_name: Name of the function being exited
        result: Function result to log (will be truncated if too long)
        execution_time: Function execution time in seconds
    """
    extra_data = {
        'function': func_name,
        'event_type': 'function_exit'
    }
    
    if result is not None:
        # Truncate large results for logging
        result_str = str(result)
        if len(result_str) > 500:
            result_str = result_str[:500] + "... (truncated)"
        extra_data['result'] = result_str
    
    if execution_time is not None:
        extra_data['execution_time_ms'] = round(execution_time * 1000, 2)
    
    logger.debug(f"EXIT {func_name}", extra={'extra_data': extra_data})


def log_performance_metric(logger: logging.Logger, metric_name: str, 
                          value: float, unit: str = "ms", **context) -> None:
    """
    Log performance metrics for monitoring.
    
    Args:
        logger: Logger instance
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        **context: Additional context
    """
    logger.info(f"METRIC {metric_name}: {value}{unit}", extra={
        'extra_data': {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'context': context,
            'event_type': 'performance_metric'
        }
    })


# Initialize the main RepoChat logger with enhanced configuration
main_logger = setup_logging(
    level=os.getenv("LOG_LEVEL", "DEBUG"),
    console_level=os.getenv("CONSOLE_LOG_LEVEL", "INFO"),
    file_level=os.getenv("FILE_LOG_LEVEL", "DEBUG")
) 