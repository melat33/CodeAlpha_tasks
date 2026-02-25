"""
Performance and logging decorators.
"""

import time
import functools
import logging

logger = logging.getLogger(__name__)

def timer(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.debug(f"{func.__name__} took {run_time:.4f} seconds")
        return value
    return wrapper_timer

def log_execution(func):
    """Decorator to log function execution"""
    @functools.wraps(func)
    def wrapper_log(*args, **kwargs):
        logger.debug(f"Starting {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Completed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper_log