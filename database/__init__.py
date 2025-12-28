"""
Database package initialization
"""

from database.connection import (
    init_database,
    close_database,
    get_session
)

from database.models import (
    Signal,
    AnalysisSnapshot,
    CoinInfo,
    ScanResult,
    WhaleActivity,
    PerformanceMetric,
    MLPrediction,
    SystemLog,
    UserPreference
)

from database.operations import (
    SignalOperations,
    CoinOperations,
    AnalysisOperations,
    PerformanceOperations,
    WhaleOperations,
    SystemOperations
)

__all__ = [
    'init_database',
    'close_database',
    'get_session',
    'Signal',
    'AnalysisSnapshot',
    'CoinInfo',
    'ScanResult',
    'WhaleActivity',
    'PerformanceMetric',
    'MLPrediction',
    'SystemLog',
    'UserPreference',
    'SignalOperations',
    'CoinOperations',
    'AnalysisOperations',
    'PerformanceOperations',
    'WhaleOperations',
    'SystemOperations'
]