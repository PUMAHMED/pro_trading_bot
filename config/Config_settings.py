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
    CACHE_TTL: int = 300  # 5 dakika
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = 'bot.log'

@dataclass
class ExchangeConfig:
    """Exchange API ayarları"""
    # MEXC
    MEXC_API_KEY: str = os.getenv('MEXC_API_KEY', '')
    MEXC_API_SECRET: str = os.getenv('MEXC_API_SECRET', '')
    
    # Binance
    BINANCE_API_KEY: str = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET: str = os.getenv('BINANCE_API_SECRET', '')
    
    # Rate Limits
    MEXC_RATE_LIMIT: int = 1000  # requests/minute
    BINANCE_RATE_LIMIT: int = 1200

@dataclass
class TradingConfig:
    """Trading parametreleri"""
    # Hedefler
    MIN_PROFIT_TARGET: float = 4.0  # %4 minimum kar
    TP1: float = 4.0
    TP2: float = 8.0
    TP3: float = 12.0
    
    # Kaldıraç
    MIN_LEVERAGE: int = 20
    MAX_LEVERAGE: int = 500
    DEFAULT_LEVERAGE: int = 50
    
    # Risk Yönetimi
    MAX_DAILY_SIGNALS: int = 100
    MAX_STOP_LOSS: float = 2.0  # %2 max SL
    MIN_RISK_REWARD: float = 2.0  # 1:2 minimum
    
    # Position Management
    MAX_OPEN_POSITIONS: int = 10
    POSITION_SIZE_PERCENT: float = 10.0  # Portfolio'nun %10'u
    
    # Zaman
    MIN_HOLDING_TIME: int = 30  # 30 dakika minimum
    MAX_HOLDING_TIME: int = 4320  # 3 gün (dakika)
    SIGNAL_TIMEOUT: int = 300  # 5 dakika sinyal geçerlilik

@dataclass
class ScannerConfig:
    """Tarayıcı ayarları"""
    # Coin filtreleme
    MIN_VOLUME_USD: float = 500000  # $500K minimum günlük volume
    MIN_PRICE: float = 0.00001  # Minimum fiyat
    MAX_PRICE: float = 100000  # Maximum fiyat
    
    # Tarama
    SCAN_INTERVAL: int = 30  # 30 saniye
    PARALLEL_SCANS: int = 100  # Paralel coin sayısı
    
    # Volatilite
    MIN_VOLATILITY: float = 2.0  # %2 minimum günlük volatilite
    MAX_VOLATILITY: float = 50.0  # %50 maximum (pump-dump ihtimali)
    
    # Quote currencies
    QUOTE_CURRENCIES: List[str] = None
    
    def __post_init__(self):
        if self.QUOTE_CURRENCIES is None:
            self.QUOTE_CURRENCIES = ['USDT', 'USDC', 'BUSD']

@dataclass
class AnalysisConfig:
    """Analiz parametreleri"""
    # Timeframes
    TIMEFRAMES: List[str] = None
    PRIMARY_TIMEFRAME: str = '15m'
    
    # Teknik İndikatörler
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
    
    # Volume
    VOLUME_MA_PERIOD: int = 20
    VOLUME_SPIKE_MULTIPLIER: float = 2.5
    
    # Sinyal Kalitesi
    MIN_SIGNAL_SCORE: float = 70.0  # 0-100 arası
    HIGH_QUALITY_THRESHOLD: float = 85.0
    MEDIUM_QUALITY_THRESHOLD: float = 70.0
    
    def __post_init__(self):
        if self.TIMEFRAMES is None:
            self.TIMEFRAMES = ['5m', '15m', '1h', '4h']

@dataclass
class ManipulationConfig:
    """Manipülasyon filtreleme"""
    # Pump/Dump Detection
    MAX_PRICE_CHANGE_1M: float = 15.0  # 1 dakikada max %15
    MAX_PRICE_CHANGE_5M: float = 25.0  # 5 dakikada max %25
    
    PUMP_VOLUME_MULTIPLIER: float = 5.0  # Normal volume'un 5 katı
    
    # Konsolidasyon
    MIN_CONSOLIDATION_PERIOD: int = 120  # 2 saat minimum konsolidasyon
    MAX_CONSOLIDATION_VOLATILITY: float = 3.0  # %3 içinde hareket
    
    # Likidite
    MIN_ORDER_BOOK_DEPTH: float = 50000  # $50K min depth
    MAX_SPREAD_PERCENT: float = 0.5  # %0.5 max spread
    
    # Whale Detection
    WHALE_ORDER_THRESHOLD: float = 100000  # $100K+ orders
    MAX_WHALE_DOMINANCE: float = 30.0  # Order book'un %30'undan fazla whale olamaz

@dataclass
class MLConfig:
    """Machine Learning ayarları"""
    # Model
    MODEL_PATH: str = 'models/'
    TRAIN_DATA_DAYS: int = 90
    MIN_TRAIN_SAMPLES: int = 1000
    
    # Features
    FEATURE_ENGINEERING: bool = True
    USE_SENTIMENT: bool = True
    USE_ORDER_FLOW: bool = True
    
    # Training
    RETRAIN_INTERVAL: int = 86400  # 24 saat
    VALIDATION_SPLIT: float = 0.2
    
    # Prediction
    CONFIDENCE_THRESHOLD: float = 0.75

@dataclass
class NotificationConfig:
    """Bildirim ayarları"""
    # Sinyal bildirimleri
    SEND_ALL_SIGNALS: bool = True
    SEND_HIGH_QUALITY_ONLY: bool = False
    
    # Güncelleme bildirimleri
    NOTIFY_TP_REACHED: bool = True
    NOTIFY_SL_APPROACHING: bool = True
    NOTIFY_ANALYSIS_BROKEN: bool = True
    NOTIFY_TARGET_UPDATED: bool = True
    
    # Sistem bildirimleri
    NOTIFY_ERRORS: bool = True
    NOTIFY_API_ISSUES: bool = True
    HEARTBEAT_INTERVAL: int = 3600  # 1 saatte bir durum bildirimi
    
    # Rate limiting
    MAX_NOTIFICATIONS_PER_MINUTE: int = 10

@dataclass
class ReportConfig:
    """Rapor ayarları"""
    # PDF
    DAILY_REPORT_TIME: str = '23:55'  # Günlük rapor saati
    REPORT_PATH: str = 'reports/'
    INCLUDE_CHARTS: bool = True
    
    # İçerik
    INCLUDE_ALL_SIGNALS: bool = True
    INCLUDE_STATISTICS: bool = True
    INCLUDE_MARKET_OVERVIEW: bool = True
    INCLUDE_TOP_PERFORMERS: bool = True
    INCLUDE_RECOMMENDATIONS: bool = True

@dataclass
class PerformanceConfig:
    """Performans optimizasyonu"""
    # Async
    MAX_CONCURRENT_TASKS: int = 100
    TASK_TIMEOUT: int = 30
    
    # Cache
    USE_CACHE: bool = True
    CACHE_KLINE_DATA: bool = True
    CACHE_ORDERBOOK: bool = False  # Order book gerçek zamanlı olmalı
    
    # Database
    BATCH_INSERT_SIZE: int = 100
    CONNECTION_POOL_SIZE: int = 10
    
    # Memory
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