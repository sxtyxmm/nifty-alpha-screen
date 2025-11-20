"""Retry utility with exponential backoff"""

import time
import functools
from typing import Callable, Any, Type, Tuple
import logging

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] = None
):
    """
    Decorator to retry a function with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries
        exponential: Use exponential backoff if True, constant delay if False
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function called on each retry
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            delay = base_delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {str(e)}"
                        )
                        raise
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt)
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed: {str(e)}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    time.sleep(delay)
                    
                    # Calculate next delay
                    if exponential:
                        delay = min(delay * 2, max_delay)
                    else:
                        delay = base_delay
            
            # This should never be reached, but just in case
            raise RuntimeError(f"{func.__name__} exceeded maximum retry attempts")
        
        return wrapper
    return decorator


def simple_retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Simple retry decorator with constant delay
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Delay between retries in seconds
    
    Returns:
        Decorated function
    """
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=delay,
        exponential=False
    )
