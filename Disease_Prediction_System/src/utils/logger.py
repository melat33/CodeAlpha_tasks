"""
Centralized logging configuration for the entire project.
"""

import logging
import sys
from datetime import datetime
import os
from pathlib import Path

def setup_logging(name, log_level=logging.INFO, log_file=None):
    """
    Set up logging with consistent formatting
    
    Args:
        name: Logger name
        log_level: Logging level
        log_file: Optional log file path
    
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file: {e}")
    
    return logger

def setup_logger(name):
    """Simple logger setup for backward compatibility"""
    return setup_logging(name)