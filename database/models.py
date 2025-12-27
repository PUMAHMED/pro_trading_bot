"""
MEXC Pro Trading Bot - Database Models
SQLAlchemy ORM modelleri
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    Text, JSON, ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from config.constants import SignalType, SignalStatus, SignalQuality, ExchangeName

Base = declarative_base()

class Signal(Base):
    """Trading sinyalleri"""
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True)
    
    # Temel bilgiler
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(SQLEnum(ExchangeName), nullable=False)
    signal_type = Column(SQLEnum(SignalType), nullable=False)
    
    # Fiyat bilgileri
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    
    # Hedefler
    tp1 = Column(Float, nullable=False)
    tp2 = Column(Float)
    tp3 = Column(Float)
    stop_loss = Column(Float, nullable=False)
    
    # Kaldıraç
    leverage = Column(Integer, nullable=False)
    
    # Kalite ve skor
    quality = Column(SQLEnum(SignalQuality), nullable=False)
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Durum
    status = Column(SQLEnum(SignalStatus), default=SignalStatus.ACTIVE)
    
    # Zaman bilgileri
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Tahminler
    estimated_duration_minutes = Column(Integer)
    estimated_profit_percent = Column(Float)
    
    # Analiz detayları
    analysis_summary = Column(Text)
    technical_score = Column(Float)
    volume_score = Column(Float)
    momentum_score = Column(Float)
    pattern_score = Column(Float)
    
    # Risk yönetimi
    risk_level = Column(String(20))
    max_position_size = Column(Float)
    
    # Performans tracking
    tp1_hit = Column(Boolean, default=False)
    tp1_hit_at = Column(DateTime)
    tp2_hit = Column(Boolean, default=False)
    tp2_hit_at = Column(DateTime)
    tp3_hit = Column(Boolean, default=False)
    tp3_hit_at = Column(DateTime)
    sl_hit = Column(Boolean, default=False)
    sl_hit_at = Column(DateTime)
    
    actual_profit_percent = Column(Float)
    actual_duration_minutes = Column(Integer)
    
    # İlişkiler
    analysis_snapshots = relationship("AnalysisSnapshot", back_populates="signal")
    
    __table_args__ = (
        Index('idx_signal_status_created', 'status', 'created_at'),
        Index('idx_signal_exchange_symbol', 'exchange', 'symbol'),
    )

class AnalysisSnapshot(Base):
    """Analiz anlık görüntüleri"""
    __tablename__ = 'analysis_snapshots'
    
    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey('signals.id'))
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Teknik indikatörler
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    bb_position = Column(Float)
    
    ema_fast = Column(Float)
    ema_slow = Column(Float)
    
    # Volume
    volume = Column(Float)
    volume_ma = Column(Float)
    volume_ratio = Column(Float)
    
    # Price action
    support_levels = Column(JSON)
    resistance_levels = Column(JSON)
    
    # Trend
    trend_direction = Column(String(50))
    trend_strength = Column(Float)
    
    # Market structure
    higher_highs = Column(Boolean)
    higher_lows = Column(Boolean)
    lower_highs = Column(Boolean)
    lower_lows = Column(Boolean)
    
    # Volatility
    atr = Column(Float)
    volatility_percent = Column(Float)
    
    # İlişki
    signal = relationship("Signal", back_populates="analysis_snapshots")

class CoinInfo(Base):
    """Coin bilgileri"""
    __tablename__ = 'coin_info'
    
    id = Column(Integer, primary_key=True)
    
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(SQLEnum(ExchangeName), nullable=False)
    
    # Durum
    is_active = Column(Boolean, default=True)
    is_futures_available = Column(Boolean, default=False)
    
    # Market data
    current_price = Column(Float)
    volume_24h = Column(Float)
    price_change_24h = Column(Float)
    
    market_cap = Column(Float)
    circulating_supply = Column(Float)
    
    # Trading info
    min_order_size = Column(Float)
    max_leverage = Column(Integer)
    tick_size = Column(Float)
    
    # Statistikler
    total_scans = Column(Integer, default=0)
    total_signals = Column(Integer, default=0)
    successful_signals = Column(Integer, default=0)
    
    # Average performance
    avg_profit_percent = Column(Float)
    avg_duration_minutes = Column(Float)
    
    # Zaman bilgileri
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_scanned = Column(DateTime)
    last_signal = Column(DateTime)
    
    __table_args__ = (
        Index('idx_coin_active_exchange', 'is_active', 'exchange'),
        Index('idx_coin_symbol_exchange', 'symbol', 'exchange', unique=True),
    )

class ScanResult(Base):
    """Tarama sonuçları"""
    __tablename__ = 'scan_results'
    
    id = Column(Integer, primary_key=True)
    
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(SQLEnum(ExchangeName), nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Tarama sonucu
    passed_filters = Column(Boolean, default=False)
    signal_generated = Column(Boolean, default=False)
    
    # Skorlar
    overall_score = Column(Float)
    technical_score = Column(Float)
    volume_score = Column(Float)
    momentum_score = Column(Float)
    manipulation_check_score = Column(Float)
    
    # Neden elendiği
    rejection_reasons = Column(JSON)
    
    # Temel metrikler
    price = Column(Float)
    volume_24h = Column(Float)
    price_change_1h = Column(Float)
    price_change_24h = Column(Float)
    volatility = Column(Float)
    
    __table_args__ = (
        Index('idx_scan_timestamp_symbol', 'timestamp', 'symbol'),
    )

class WhaleActivity(Base):
    """Balina aktiviteleri"""
    __tablename__ = 'whale_activity'
    
    id = Column(Integer, primary_key=True)
    
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(SQLEnum(ExchangeName), nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Order detayları
    side = Column(String(10))  # buy/sell
    price = Column(Float)
    amount = Column(Float)
    total_usd = Column(Float)
    
    # Order book pozisyonu
    distance_from_price_percent = Column(Float)
    
    # Impact
    orderbook_dominance_percent = Column(Float)
    
    __table_args__ = (
        Index('idx_whale_symbol_timestamp', 'symbol', 'timestamp'),
    )

class PerformanceMetric(Base):
    """Performans metrikleri"""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True)
    
    date = Column(DateTime, nullable=False, unique=True, index=True)
    
    # Sinyal metrikleri
    total_signals = Column(Integer, default=0)
    excellent_signals = Column(Integer, default=0)
    high_signals = Column(Integer, default=0)
    medium_signals = Column(Integer, default=0)
    low_signals = Column(Integer, default=0)
    
    # Sonuçlar
    tp1_hit_count = Column(Integer, default=0)
    tp2_hit_count = Column(Integer, default=0)
    tp3_hit_count = Column(Integer, default=0)
    sl_hit_count = Column(Integer, default=0)
    
    # Kar/zarar
    total_profit_percent = Column(Float, default=0.0)
    avg_profit_percent = Column(Float)
    max_profit_percent = Column(Float)
    min_profit_percent = Column(Float)
    
    # Win rate
    win_rate = Column(Float)
    success_rate_tp1 = Column(Float)
    success_rate_tp2 = Column(Float)
    success_rate_tp3 = Column(Float)
    
    # Timing
    avg_duration_minutes = Column(Float)
    fastest_win_minutes = Column(Integer)
    slowest_win_minutes = Column(Integer)
    
    # En iyi performans
    best_coin = Column(String(20))
    best_coin_profit = Column(Float)
    worst_coin = Column(String(20))
    worst_coin_profit = Column(Float)
    
    # Exchange breakdown
    mexc_signals = Column(Integer, default=0)
    binance_signals = Column(Integer, default=0)
    
    # System metrics
    total_scans = Column(Integer, default=0)
    avg_scan_duration_ms = Column(Float)
    api_errors = Column(Integer, default=0)

class MLPrediction(Base):
    """Machine Learning tahminleri"""
    __tablename__ = 'ml_predictions'
    
    id = Column(Integer, primary_key=True)
    
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(SQLEnum(ExchangeName), nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Tahmin
    predicted_direction = Column(SQLEnum(SignalType))
    predicted_move_percent = Column(Float)
    confidence = Column(Float)
    
    # Features kullanılan
    features_used = Column(JSON)
    feature_importance = Column(JSON)
    
    # Model bilgisi
    model_version = Column(String(50))
    model_accuracy = Column(Float)
    
    # Gerçek sonuç (sonradan güncellenir)
    actual_direction = Column(SQLEnum(SignalType))
    actual_move_percent = Column(Float)
    prediction_correct = Column(Boolean)
    
    validated_at = Column(DateTime)

class SystemLog(Base):
    """Sistem logları"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(20))  # INFO, WARNING, ERROR
    category = Column(String(50))  # SCAN, ANALYSIS, SIGNAL, API, etc.
    
    message = Column(Text)
    details = Column(JSON)
    
    # Error tracking
    error_type = Column(String(100))
    stack_trace = Column(Text)
    
    __table_args__ = (
        Index('idx_log_timestamp_level', 'timestamp', 'level'),
    )

class UserPreference(Base):
    """Kullanıcı tercihleri"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    
    # Bildirim tercihleri
    notify_all_signals = Column(Boolean, default=True)
    notify_high_quality_only = Column(Boolean, default=False)
    min_signal_score = Column(Float, default=70.0)
    
    notify_tp_reached = Column(Boolean, default=True)
    notify_sl_approaching = Column(Boolean, default=True)
    notify_analysis_updates = Column(Boolean, default=True)
    
    # Coin filtreleri
    excluded_coins = Column(JSON)
    preferred_exchanges = Column(JSON)
    
    # Risk tercihleri
    max_leverage = Column(Integer, default=100)
    risk_tolerance = Column(String(20), default='medium')
    
    # Özel ayarlar
    custom_settings = Column(JSON)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)