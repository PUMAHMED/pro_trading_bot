"""
MEXC Pro Trading Bot - Constants
Sabit değerler ve enum'lar
"""

from enum import Enum

class SignalType(Enum):
    """Sinyal türleri"""
    LONG = "LONG"
    SHORT = "SHORT"

class SignalQuality(Enum):
    """Sinyal kalite seviyeleri"""
    EXCELLENT = "🔥 MÜKEMMEL"
    HIGH = "⭐ YÜKSEK"
    MEDIUM = "✅ ORTA"
    LOW = "⚠️ DÜŞÜK"

class SignalStatus(Enum):
    """Sinyal durumları"""
    ACTIVE = "active"
    TP1_HIT = "tp1_hit"
    TP2_HIT = "tp2_hit"
    TP3_HIT = "tp3_hit"
    SL_HIT = "sl_hit"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class MarketPhase(Enum):
    """Piyasa fazları"""
    ACCUMULATION = "accumulation"
    MARKUP = "markup"
    DISTRIBUTION = "distribution"
    MARKDOWN = "markdown"
    RANGING = "ranging"

class TrendDirection(Enum):
    """Trend yönleri"""
    STRONG_UPTREND = "strong_uptrend"
    UPTREND = "uptrend"
    SIDEWAYS = "sideways"
    DOWNTREND = "downtrend"
    STRONG_DOWNTREND = "strong_downtrend"

class ManipulationType(Enum):
    """Manipülasyon türleri"""
    PUMP = "pump"
    DUMP = "dump"
    WASH_TRADING = "wash_trading"
    SPOOFING = "spoofing"
    LIQUIDITY_HUNT = "liquidity_hunt"
    NONE = "none"

class ExchangeName(Enum):
    """Exchange isimleri"""
    MEXC = "MEXC"
    BINANCE = "Binance"

# Emoji ve simgeler
EMOJIS = {
    'rocket': '🚀',
    'fire': '🔥',
    'star': '⭐',
    'check': '✅',
    'warning': '⚠️',
    'cross': '❌',
    'chart_up': '📈',
    'chart_down': '📉',
    'money': '💰',
    'bell': '🔔',
    'target': '🎯',
    'shield': '🛡️',
    'clock': '⏰',
    'brain': '🧠',
    'crystal_ball': '🔮',
    'whale': '🐋',
    'magnifying_glass': '🔍',
    'gear': '⚙️',
    'document': '📄',
    'lightning': '⚡',
    'trophy': '🏆',
    'graph': '📊',
    'robot': '🤖',
    'info': 'ℹ️',
    'exclamation': '❗',
    'bullseye': '🎯',
    'up_arrow': '⬆️',
    'down_arrow': '⬇️',
    'hourglass': '⏳',
    'checkmark': '✓',
    'xmark': '✗'
}

# Chart style konfigürasyonu (reports/charts.py için GEREKLI)
CHART_STYLE = {
    'figure_size': (12, 8),
    'dpi': 100,
    'style': 'seaborn-v0_8-darkgrid',
    'title_fontsize': 14,
    'label_fontsize': 12,
    'tick_fontsize': 10,
    'legend_fontsize': 10,
    'grid_alpha': 0.3,
    'line_width': 2,
    'colors': {
        'primary': '#2E86AB',
        'secondary': '#A23B72',
        'success': '#06A77D',
        'danger': '#D84654',
        'warning': '#F18F01',
        'profit': '#06A77D',
        'loss': '#D84654',
        'neutral': '#6C757D'
    },
    'chart_types': {
        'line': {'linewidth': 2, 'alpha': 0.8},
        'bar': {'alpha': 0.7, 'edgecolor': 'black', 'linewidth': 0.5},
        'scatter': {'s': 50, 'alpha': 0.6},
        'area': {'alpha': 0.3}
    }
}

# Report configuration
REPORT_CONFIG = {
    'page_size': 'A4',
    'margins': {'top': 50, 'bottom': 50, 'left': 50, 'right': 50},
    'fonts': {'title': 18, 'heading': 14, 'subheading': 12, 'body': 10, 'small': 8},
    'colors': {'primary': '#2E86AB', 'text': '#000000', 'light_gray': '#CCCCCC', 'dark_gray': '#666666'}
}

# Kalite eşikleri
QUALITY_THRESHOLDS = {
    SignalQuality.EXCELLENT: 90.0,
    SignalQuality.HIGH: 75.0,
    SignalQuality.MEDIUM: 60.0,
    SignalQuality.LOW: 0.0
}

# Teknik indikatör ağırlıkları
INDICATOR_WEIGHTS = {
    'trend': 0.25,
    'momentum': 0.20,
    'volume': 0.20,
    'support_resistance': 0.15,
    'pattern': 0.10,
    'orderbook': 0.10
}

# Volume kategorileri
VOLUME_CATEGORIES = {
    'very_high': 3.0,
    'high': 2.0,
    'normal': 1.0,
    'low': 0.5,
    'very_low': 0.25
}

# RSI seviyeleri
RSI_LEVELS = {
    'extreme_oversold': 20,
    'oversold': 30,
    'neutral_low': 40,
    'neutral_high': 60,
    'overbought': 70,
    'extreme_overbought': 80
}

# Bollinger Bands pozisyonları
BB_POSITIONS = {
    'below_lower': -2.0,
    'at_lower': -1.0,
    'middle_lower': -0.5,
    'middle': 0.0,
    'middle_upper': 0.5,
    'at_upper': 1.0,
    'above_upper': 2.0
}

# Pattern güven skorları
PATTERN_CONFIDENCE = {
    'double_bottom': 0.85,
    'double_top': 0.85,
    'head_shoulders': 0.80,
    'inverse_head_shoulders': 0.80,
    'triangle_breakout': 0.75,
    'flag': 0.70,
    'wedge': 0.70,
    'channel_breakout': 0.65
}

# Kaldıraç risk seviyeleri
LEVERAGE_RISK_MAP = {
    (20, 50): 'low',
    (51, 100): 'medium',
    (101, 200): 'high',
    (201, 500): 'extreme'
}

# Zaman periyotları (saniye)
TIME_PERIODS = {
    '1m': 60,
    '5m': 300,
    '15m': 900,
    '30m': 1800,
    '1h': 3600,
    '2h': 7200,
    '4h': 14400,
    '6h': 21600,
    '12h': 43200,
    '1d': 86400
}

# Telegram komutları
BOT_COMMANDS = {
    'start': 'Botu başlat',
    'help': 'Yardım menüsü',
    'status': 'Bot durumu',
    'stats': 'İstatistikler',
    'analyze': 'Coin analiz et',
    'settings': 'Ayarlar',
    'report': 'Günlük rapor',
    'stop': 'Taramayı durdur',
    'resume': 'Taramayı başlat'
}

# Hata mesajları
ERROR_MESSAGES = {
    'api_error': '❌ API bağlantı hatası',
    'rate_limit': '⚠️ Rate limit aşıldı, bekleniyor...',
    'invalid_symbol': '❌ Geçersiz coin sembolü',
    'insufficient_data': '⚠️ Yetersiz veri',
    'analysis_failed': '❌ Analiz başarısız',
    'database_error': '❌ Veritabanı hatası',
    'network_error': '❌ Ağ bağlantı hatası'
}

# Başarı mesajları
SUCCESS_MESSAGES = {
    'scan_started': '✅ Tarama başlatıldı',
    'scan_stopped': '✅ Tarama durduruldu',
    'signal_sent': '✅ Sinyal gönderildi',
    'settings_updated': '✅ Ayarlar güncellendi',
    'report_generated': '✅ Rapor oluşturuldu'
}

# Notification templates
NOTIFICATION_TEMPLATES = {
    'signal': """{emoji} {quality} SİNYAL - {exchange}

💎 Coin: {symbol}
📊 Yön: {direction}
💰 Fiyat: {price}

🎯 Hedefler:
  TP1: {tp1} ({tp1_percent}%)
  TP2: {tp2} ({tp2_percent}%)
  TP3: {tp3} ({tp3_percent}%)

🛡️ Stop Loss: {sl} ({sl_percent}%)
⚡ Kaldıraç: {leverage}x

⏰ Tahmini Süre: {estimated_time}
📈 Sinyal Skoru: {score}/100
🧠 Güven: {confidence}%

📊 Analiz Özeti:
{analysis_summary}

⚠️ Risk: {risk_level}""",
    'update': """🔄 SİNYAL GÜNCELLENDİ

💎 Coin: {symbol}
📊 Güncelleme: {update_type}

{details}""",
    'tp_reached': """🎉 HEDEF ULAŞILDI!

💎 Coin: {symbol}
🎯 {tp_level}: {price}
💰 Kar: {profit}%

⏱️ Süre: {duration}""",
    'heartbeat': """💓 Sistem Durumu

⏰ {timestamp}
✅ Tarama: Aktif
📊 İşlenen Coin: {coins_scanned}
📈 Bugünkü Sinyaller: {signals_today}
🎯 Başarı Oranı: {success_rate}%"""
}

# ML Features
ML_FEATURES = [
    'sma_20', 'sma_50', 'sma_200', 'ema_9', 'ema_21', 'ema_55',
    'macd', 'macd_signal', 'macd_histogram', 'adx', 'adx_pos', 'adx_neg',
    'rsi_14', 'rsi_7', 'rsi_21', 'stoch_k', 'stoch_d', 'cci', 'mfi', 'roc', 'williams_r',
    'bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_position',
    'atr', 'atr_percent', 'keltner_upper', 'keltner_lower', 'volatility_ratio',
    'volume_sma_20', 'volume_ratio', 'obv', 'obv_ema', 'vwap', 'cmf', 'accumulation', 'volume_oscillator',
    'price_change_1h', 'price_change_4h', 'price_change_24h', 'price_change_7d',
    'high_low_ratio', 'close_position', 'body_size', 'upper_wick', 'lower_wick', 'gap_size',
    'distance_to_support', 'distance_to_resistance', 'support_strength', 'resistance_strength',
    'pivot_point', 'fibonacci_382', 'fibonacci_500', 'fibonacci_618',
    'higher_highs', 'lower_lows', 'trend_strength', 'consolidation', 'breakout_potential', 'swing_high_low',
    'bid_ask_spread', 'bid_volume', 'ask_volume', 'order_imbalance', 'depth_ratio', 'large_orders',
    'hour_of_day', 'day_of_week', 'is_weekend', 'trading_session',
    'btc_correlation', 'market_correlation', 'sector_performance',
    'momentum_composite', 'trend_composite', 'volume_composite', 'volatility_composite', 'quality_score'
]

# ML Feature Kategorileri
ML_FEATURE_CATEGORIES = {
    'trend': ['sma_20', 'sma_50', 'sma_200', 'ema_9', 'ema_21', 'ema_55', 'macd', 'macd_signal', 'macd_histogram', 'adx', 'adx_pos', 'adx_neg'],
    'momentum': ['rsi_14', 'rsi_7', 'rsi_21', 'stoch_k', 'stoch_d', 'cci', 'mfi', 'roc', 'williams_r'],
    'volatility': ['bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_position', 'atr', 'atr_percent', 'keltner_upper', 'keltner_lower', 'volatility_ratio'],
    'volume': ['volume_sma_20', 'volume_ratio', 'obv', 'obv_ema', 'vwap', 'cmf', 'accumulation', 'volume_oscillator'],
    'price_action': ['price_change_1h', 'price_change_4h', 'price_change_24h', 'price_change_7d', 'high_low_ratio', 'close_position', 'body_size', 'upper_wick', 'lower_wick', 'gap_size'],
    'support_resistance': ['distance_to_support', 'distance_to_resistance', 'support_strength', 'resistance_strength', 'pivot_point', 'fibonacci_382', 'fibonacci_500', 'fibonacci_618'],
    'market_structure': ['higher_highs', 'lower_lows', 'trend_strength', 'consolidation', 'breakout_potential', 'swing_high_low'],
    'orderbook': ['bid_ask_spread', 'bid_volume', 'ask_volume', 'order_imbalance', 'depth_ratio', 'large_orders'],
    'temporal': ['hour_of_day', 'day_of_week', 'is_weekend', 'trading_session'],
    'cross_asset': ['btc_correlation', 'market_correlation', 'sector_performance'],
    'composite': ['momentum_composite', 'trend_composite', 'volume_composite', 'volatility_composite', 'quality_score']
}

# ML Model Konfigürasyonu
ML_CONFIG = {
    'train_test_split': 0.8,
    'validation_split': 0.2,
    'min_samples_for_training': 1000,
    'feature_importance_threshold': 0.01,
    'correlation_threshold': 0.95,
    'update_frequency_hours': 24,
    'prediction_confidence_threshold': 0.7,
    'ensemble_models': ['random_forest', 'gradient_boost', 'neural_network'],
    'cross_validation_folds': 5
}

def get_quality_from_score(score: float) -> SignalQuality:
    """Skordan kalite seviyesi belirle"""
    if score >= QUALITY_THRESHOLDS[SignalQuality.EXCELLENT]:
        return SignalQuality.EXCELLENT
    elif score >= QUALITY_THRESHOLDS[SignalQuality.HIGH]:
        return SignalQuality.HIGH
    elif score >= QUALITY_THRESHOLDS[SignalQuality.MEDIUM]:
        return SignalQuality.MEDIUM
    else:
        return SignalQuality.LOW

def get_leverage_recommendation(score: float, volatility: float) -> int:
    """Skordan kaldıraç önerisi"""
    from config.settings import trading_config
    
    if volatility > 15:
        max_lev = 50
    elif volatility > 10:
        max_lev = 100
    elif volatility > 5:
        max_lev = 200
    else:
        max_lev = trading_config.MAX_LEVERAGE
    
    if score >= 90:
        leverage = max_lev
    elif score >= 80:
        leverage = int(max_lev * 0.8)
    elif score >= 70:
        leverage = int(max_lev * 0.6)
    else:
        leverage = int(max_lev * 0.4)
    
    leverage = max(trading_config.MIN_LEVERAGE, leverage)
    leverage = min(trading_config.MAX_LEVERAGE, leverage)
    
    return leverage