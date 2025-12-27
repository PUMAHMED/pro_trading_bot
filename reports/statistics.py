"""
MEXC Pro Trading Bot - Statistics Calculator
İstatistik hesaplamaları
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from database.connection import get_session
from database.operations import SignalOperations
from utils.logger import get_logger

logger = get_logger(__name__)

class StatisticsCalculator:
    """İstatistik hesaplama sınıfı"""
    
    @staticmethod
    async def calculate_daily_stats() -> Dict[str, Any]:
        """Günlük istatistikleri hesapla"""
        async with get_session() as session:
            stats = await SignalOperations.get_signal_statistics(session, days=1)
            
            return {
                'total_signals': stats['total_signals'],
                'tp1_hit_count': stats['tp1_hit_count'],
                'success_rate': stats['success_rate'],
                'avg_profit': stats['avg_profit'],
                'max_profit': stats['max_profit'],
                'min_profit': stats['min_profit'],
                'avg_duration': stats['avg_duration_minutes']
            }
    
    @staticmethod
    async def calculate_weekly_stats() -> Dict[str, Any]:
        """Haftalık istatistikleri hesapla"""
        async with get_session() as session:
            stats = await SignalOperations.get_signal_statistics(session, days=7)
            return stats
    
    @staticmethod
    async def get_top_performers(limit: int = 10) -> List[Dict]:
        """En iyi performans gösteren coinleri getir"""
        # Placeholder - gerçek implementasyon database'den gelecek
        return []