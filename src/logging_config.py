"""
Logging configuration for Campaign Canvas application.

This module sets up comprehensive logging with support for:
- Console and file output
- Structured JSON logging
- Environment-specific log levels
- Performance tracking
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.config import config


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def setup_logging(
    name: str = config.APP_NAME,
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Configure and return a logger with console and optional file handlers.
    
    Args:
        name: Logger name (typically module name or app name)
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  Defaults based on environment
        log_file: Optional file path for file handler
    
    Returns:
        Configured logger instance
    """
    
    # Determine log level
    if log_level is None:
        if config.is_development() or config.ENABLE_DETAILED_LOGGING:
            log_level = "DEBUG"
        elif config.is_production():
            log_level = "WARNING"
        else:
            log_level = "INFO"
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    
    # Format based on environment
    if config.ENABLE_DETAILED_LOGGING:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotate log files to prevent them from growing too large
        file_handler = logging.handlers.RotatingFileHandler(
            str(log_file),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(getattr(logging, log_level))
        
        # Use JSON formatter for file output
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


# Get the main application logger
logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(name)
