"""
Utils package initialization
"""

from utils.logger import setup_logger, get_logger
from utils.helpers import (
    format_price,
    format_percent,
    calculate_percent_change,
    calculate_atr,
    calculate_volatility,
    timeframe_to_seconds,
    seconds_to_timeframe_string,
    calculate_support_resistance,
    merge_similar_levels,
    calculate_ema,
    calculate_sma,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    detect_trend,
    estimate_duration,
    format_duration,
    get_risk_level
)
from utils.cache import cache_manager, CacheManager
from utils.performance import PerformanceMonitor

__all__ = [
    'setup_logger',
    'get_logger',
    'format_price',
    'format_percent',
    'calculate_percent_change',
    'calculate_atr',
    'calculate_volatility',
    'timeframe_to_seconds',
    'seconds_to_timeframe_string',
    'calculate_support_resistance',
    'merge_similar_levels',
    'calculate_ema',
    'calculate_sma',
    'calculate_rsi',
    'calculate_macd',
    'calculate_bollinger_bands',
    'detect_trend',
    'estimate_duration',
    'format_duration',
    'get_risk_level',
    'cache_manager',
    'CacheManager',
    'PerformanceMonitor'
]