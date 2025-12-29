"""
MEXC Pro Trading Bot - Configuration Settings
Tüm bot ayarları ve parametreleri
"""

import os
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class BotConfig:
    """Ana bot konfigürasyonu"""
    TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN', '')
    ADMIN_ID: int = int(os.getenv('ADMIN_ID', 0))
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///trading_bot.db')
    
    # Cache
    REDIS_URL: str = os.getenv('REDIS_URL', '')
    CACHE_TTL: int = 300
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = 'bot.log'
    
    # Timezone - İstanbul saati
    TIMEZONE: str = 'Europe/Istanbul'

@dataclass
class ExchangeConfig:
    """Exchange API ayarları"""
    MEXC_API_KEY: str = os.getenv('MEXC_API_KEY', '')
    MEXC_API_SECRET: str = os.getenv('MEXC_API_SECRET', '')
    
    BINANCE_API_KEY: str = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET: str = os.getenv('BINANCE_API_SECRET', '')
    
    MEXC_RATE_LIMIT: int = 1000
    BINANCE_RATE_LIMIT: int = 1200

@dataclass
class TradingConfig:
    """Trading parametreleri"""
    # Hedefler - TP1 SPOT %4 SABİT
    MIN_PROFIT_TARGET: float = 4.0
    TP1_SPOT_FIXED: float = 4.0  # Spot TP1 her zaman %4
    TP2: float = 8.0
    TP3: float = 12.0
    
    # Kaldıraç
    MIN_LEVERAGE: int = 20
    MAX_LEVERAGE: int = 500
    DEFAULT_LEVERAGE: int = 50
    
    # Risk Yönetimi
    MAX_DAILY_SIGNALS: int = 300  # Günlük maksimum 300 işlem
    MAX_STOP_LOSS: float = 2.0
    MIN_RISK_REWARD: float = 2.0
    
    MAX_OPEN_POSITIONS: int = 10
    POSITION_SIZE_PERCENT: float = 10.0
    
    MIN_HOLDING_TIME: int = 30
    MAX_HOLDING_TIME: int = 4320
    SIGNAL_TIMEOUT: int = 300
    
    # Giriş fiyatı optimizasyonu için bekleme süresi (saniye)
    ENTRY_OPTIMIZATION_WAIT: int = 60  # 1 dakika oynaklık bekle
    ENTRY_PRICE_TOLERANCE: float = 0.5  # %0.5 tolerans

@dataclass
class ScannerConfig:
    """Tarayıcı ayarları"""
    MIN_VOLUME_USD: float = 500000
    MIN_PRICE: float = 0.00001
    MAX_PRICE: float = 100000
    
    SCAN_INTERVAL: int = 30
    PARALLEL_SCANS: int = 100
    
    MIN_VOLATILITY: float = 2.0
    MAX_VOLATILITY: float = 50.0
    
    # SADECE USDT coinleri
    QUOTE_CURRENCIES: List[str] = None
    
    def __post_init__(self):
        if self.QUOTE_CURRENCIES is None:
            self.QUOTE_CURRENCIES = ['USDT']  # Sadece USDT

@dataclass
class AnalysisConfig:
    """Analiz parametreleri"""
    TIMEFRAMES: List[str] = None
    PRIMARY_TIMEFRAME: str = '15m'
    
    RSI_PERIOD: int = 14
    RSI_OVERSOLD: float = 30
    RSI_OVERBOUGHT: float = 70
    
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    
    BB_PERIOD: int = 20
    BB_STD: float = 2.0
    
    EMA_FAST: int = 9
    EMA_SLOW: int = 21
    
    VOLUME_MA_PERIOD: int = 20
    VOLUME_SPIKE_MULTIPLIER: float = 2.5
    
    # Sinyal Kalitesi - 80'e çıkarıldı
    MIN_SIGNAL_SCORE: float = 70.0
    HIGH_QUALITY_THRESHOLD: float = 80.0  # 75'ten 80'e yükseltildi
    MEDIUM_QUALITY_THRESHOLD: float = 70.0
    
    def __post_init__(self):
        if self.TIMEFRAMES is None:
            self.TIMEFRAMES = ['5m', '15m', '1h', '4h']

@dataclass
class ManipulationConfig:
    """Manipülasyon filtreleme"""
    MAX_PRICE_CHANGE_1M: float = 15.0
    MAX_PRICE_CHANGE_5M: float = 25.0
    
    PUMP_VOLUME_MULTIPLIER: float = 5.0
    
    MIN_CONSOLIDATION_PERIOD: int = 120
    MAX_CONSOLIDATION_VOLATILITY: float = 3.0
    
    MIN_ORDER_BOOK_DEPTH: float = 50000
    MAX_SPREAD_PERCENT: float = 0.5
    
    WHALE_ORDER_THRESHOLD: float = 100000
    MAX_WHALE_DOMINANCE: float = 30.0

@dataclass
class MLConfig:
    """Machine Learning ayarları"""
    MODEL_PATH: str = 'models/'
    TRAIN_DATA_DAYS: int = 90
    MIN_TRAIN_SAMPLES: int = 1000
    
    FEATURE_ENGINEERING: bool = True
    USE_SENTIMENT: bool = True
    USE_ORDER_FLOW: bool = True
    
    RETRAIN_INTERVAL: int = 86400
    VALIDATION_SPLIT: float = 0.2
    
    CONFIDENCE_THRESHOLD: float = 0.75

@dataclass
class NotificationConfig:
    """Bildirim ayarları"""
    SEND_ALL_SIGNALS: bool = True
    SEND_HIGH_QUALITY_ONLY: bool = False
    
    # TP/SL bildirimleri aktif
    NOTIFY_TP_REACHED: bool = True
    NOTIFY_SL_APPROACHING: bool = True
    NOTIFY_ANALYSIS_BROKEN: bool = True  # Analiz bozulması bildirimi
    NOTIFY_TARGET_UPDATED: bool = True  # Hedef güncelleme bildirimi
    
    NOTIFY_ERRORS: bool = True
    NOTIFY_API_ISSUES: bool = True
    HEARTBEAT_INTERVAL: int = 3600
    
    MAX_NOTIFICATIONS_PER_MINUTE: int = 10

@dataclass
class ReportConfig:
    """Rapor ayarları"""
    DAILY_REPORT_TIME: str = '23:55'
    REPORT_PATH: str = 'reports/'
    INCLUDE_CHARTS: bool = True
    
    INCLUDE_ALL_SIGNALS: bool = True
    INCLUDE_STATISTICS: bool = True
    INCLUDE_MARKET_OVERVIEW: bool = True
    INCLUDE_TOP_PERFORMERS: bool = True
    INCLUDE_RECOMMENDATIONS: bool = True

@dataclass
class PerformanceConfig:
    """Performans optimizasyonu"""
    MAX_CONCURRENT_TASKS: int = 100
    TASK_TIMEOUT: int = 30
    
    USE_CACHE: bool = True
    CACHE_KLINE_DATA: bool = True
    CACHE_ORDERBOOK: bool = False
    
    BATCH_INSERT_SIZE: int = 100
    CONNECTION_POOL_SIZE: int = 10
    
    MAX_MEMORY_MB: int = 512
    CLEANUP_INTERVAL: int = 3600

# Global config instances
bot_config = BotConfig()
exchange_config = ExchangeConfig()
trading_config = TradingConfig()
scanner_config = ScannerConfig()
analysis_config = AnalysisConfig()
manipulation_config = ManipulationConfig()
ml_config = MLConfig()
notification_config = NotificationConfig()
report_config = ReportConfig()
performance_config = PerformanceConfig()

def validate_config() -> bool:
    """Konfigürasyonları doğrula"""
    errors = []
    
    if not bot_config.TELEGRAM_TOKEN:
        errors.append("TELEGRAM_TOKEN bulunamadı")
    
    if not bot_config.ADMIN_ID:
        errors.append("ADMIN_ID bulunamadı")
    
    if not exchange_config.MEXC_API_KEY or not exchange_config.MEXC_API_SECRET:
        errors.append("MEXC API credentials bulunamadı")
    
    if not exchange_config.BINANCE_API_KEY or not exchange_config.BINANCE_API_SECRET:
        errors.append("Binance API credentials bulunamadı")
    
    if errors:
        print("❌ Konfigürasyon hataları:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Konfigürasyon doğrulandı")
    return True