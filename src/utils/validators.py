"""Validation utility functions"""

import re
from datetime import datetime
from typing import Optional


def validate_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format
    
    Args:
        symbol: Stock symbol to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not symbol:
        return False
    
    # NSE symbols are typically uppercase letters, may include numbers and hyphens
    # Examples: RELIANCE, TCS, M&M, NIFTY50
    pattern = r'^[A-Z0-9&\-]+$'
    
    # Length should be reasonable (2-20 characters)
    if len(symbol) < 2 or len(symbol) > 20:
        return False
    
    return bool(re.match(pattern, symbol.upper()))


def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format
    
    Args:
        date_str: Date string to validate
        format: Expected date format
    
    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except (ValueError, TypeError):
        return False


def validate_score(score: float, min_score: float = -5.0, max_score: float = 5.0) -> bool:
    """
    Validate score is within expected range
    
    Args:
        score: Score value to validate
        min_score: Minimum valid score
        max_score: Maximum valid score
    
    Returns:
        True if valid, False otherwise
    """
    try:
        return min_score <= float(score) <= max_score
    except (ValueError, TypeError):
        return False


def validate_percentage(value: float, allow_negative: bool = False) -> bool:
    """
    Validate percentage value
    
    Args:
        value: Percentage value to validate
        allow_negative: Whether to allow negative percentages
    
    Returns:
        True if valid, False otherwise
    """
    try:
        val = float(value)
        if allow_negative:
            return -100 <= val <= 100
        return 0 <= val <= 100
    except (ValueError, TypeError):
        return False


def sanitize_symbol(symbol: str) -> Optional[str]:
    """
    Sanitize and normalize stock symbol
    
    Args:
        symbol: Stock symbol to sanitize
    
    Returns:
        Sanitized symbol or None if invalid
    """
    if not symbol:
        return None
    
    # Convert to uppercase and strip whitespace
    clean_symbol = symbol.strip().upper()
    
    # Remove invalid characters
    clean_symbol = re.sub(r'[^A-Z0-9&\-]', '', clean_symbol)
    
    if validate_symbol(clean_symbol):
        return clean_symbol
    
    return None


def validate_market_cap(market_cap: float) -> bool:
    """
    Validate market cap value
    
    Args:
        market_cap: Market cap value in crores
    
    Returns:
        True if valid, False otherwise
    """
    try:
        return float(market_cap) >= 0
    except (ValueError, TypeError):
        return False


def validate_price(price: float) -> bool:
    """
    Validate stock price
    
    Args:
        price: Stock price to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        return float(price) > 0
    except (ValueError, TypeError):
        return False
