"""
MEXC Pro Trading Bot - Performance Monitor
Performans izleme
"""

from datetime import datetime
from typing import Dict, Any
from collections import deque
from utils.logger import get_logger

logger = get_logger(__name__)

class PerformanceMonitor:
    """Performans monitörü"""
    
    def __init__(self):
        self.scan_durations = deque(maxlen=100)
        self.scan_counts = deque(maxlen=100)
        self.signal_counts = deque(maxlen=100)
        
        self.total_scans = 0
        self.total_signals = 0
        self.total_errors = 0
        
        self.start_time = datetime.now()
        self.last_scan_time = None
        
    def record_scan(self, duration: float, coins_scanned: int, signals_generated: int):
        """Tarama metriklerini kaydet"""
        self.scan_durations.append(duration)
        self.scan_counts.append(coins_scanned)
        self.signal_counts.append(signals_generated)
        
        self.total_scans += 1
        self.total_signals += signals_generated
        self.last_scan_time = datetime.now()
        
        logger.debug(
            f"📊 Scan: {duration:.2f}s, "
            f"Coins: {coins_scanned}, "
            f"Signals: {signals_generated}"
        )
    
    def record_error(self):
        """Hata kaydet"""
        self.total_errors += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri al"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        avg_scan_duration = (
            sum(self.scan_durations) / len(self.scan_durations)
            if self.scan_durations else 0
        )
        
        avg_coins_per_scan = (
            sum(self.scan_counts) / len(self.scan_counts)
            if self.scan_counts else 0
        )
        
        avg_signals_per_scan = (
            sum(self.signal_counts) / len(self.signal_counts)
            if self.signal_counts else 0
        )
        
        return {
            'uptime_seconds': int(uptime),
            'uptime_formatted': self._format_uptime(uptime),
            'total_scans': self.total_scans,
            'total_signals': self.total_signals,
            'total_errors': self.total_errors,
            'avg_scan_duration': round(avg_scan_duration, 2),
            'avg_coins_per_scan': int(avg_coins_per_scan),
            'avg_signals_per_scan': round(avg_signals_per_scan, 2),
            'last_scan': self.last_scan_time.isoformat() if self.last_scan_time else None,
            'scans_per_hour': int(self.total_scans / (uptime / 3600)) if uptime > 0 else 0,
            'signals_per_hour': round(self.total_signals / (uptime / 3600), 2) if uptime > 0 else 0
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Uptime'ı formatla"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}g")
        if hours > 0:
            parts.append(f"{hours}s")
        if minutes > 0:
            parts.append(f"{minutes}d")
        
        return " ".join(parts) if parts else "< 1d"
    
    def get_health_status(self) -> str:
        """Sistem sağlık durumu"""
        if self.total_errors == 0:
            return "🟢 EXCELLENT"
        
        error_rate = self.total_errors / max(self.total_scans, 1)
        
        if error_rate < 0.01:
            return "🟢 GOOD"
        elif error_rate < 0.05:
            return "🟡 WARNING"
        else:
            return "🔴 CRITICAL"
