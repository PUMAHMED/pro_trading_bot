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

# Kalite eşikleri için skorlar
QUALITY_THRESHOLDS = {
    SignalQuality.EXCELLENT: 90.0,
    SignalQuality.HIGH: 75.0,
    SignalQuality.MEDIUM: 60.0,
    SignalQuality.LOW: 0.0
}

# Teknik indikatör skorları için ağırlıklar
INDICATOR_WEIGHTS = {
    'trend': 0.25,
    'momentum': 0.20,
    'volume': 0.20,
    'support_resistance': 0.15,
    'pattern': 0.10,
    'orderbook': 0.10
}

# Volume analizi için kategoriler
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
    'signal': """
{emoji} {quality} SİNYAL - {exchange}

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

⚠️ Risk: {risk_level}
""",
    'update': """
🔄 SİNYAL GÜNCELLENDİ

💎 Coin: {symbol}
📊 Güncelleme: {update_type}

{details}
""",
    'tp_reached': """
🎉 HEDEF ULAŞILDI!

💎 Coin: {symbol}
🎯 {tp_level}: {price}
💰 Kar: {profit}%

⏱️ Süre: {duration}
""",
    'heartbeat': """
💓 Sistem Durumu

⏰ {timestamp}
✅ Tarama: Aktif
📊 İşlenen Coin: {coins_scanned}
📈 Bugünkü Sinyaller: {signals_today}
🎯 Başarı Oranı: {success_rate}%
"""
}

# Machine Learning Features
ML_FEATURES = [
    # Trend Indicators (Trend Göstergeleri)
    'sma_20',           # 20 günlük basit hareketli ortalama
    'sma_50',           # 50 günlük basit hareketli ortalama
    'sma_200',          # 200 günlük basit hareketli ortalama
    'ema_9',            # 9 günlük üstel hareketli ortalama
    'ema_21',           # 21 günlük üstel hareketli ortalama
    'ema_55',           # 55 günlük üstel hareketli ortalama
    'macd',             # MACD değeri
    'macd_signal',      # MACD sinyal çizgisi
    'macd_histogram',   # MACD histogram
    'adx',              # Average Directional Index
    'adx_pos',          # Pozitif yönlü gösterge
    'adx_neg',          # Negatif yönlü gösterge
    
    # Momentum Indicators (Momentum Göstergeleri)
    'rsi_14',           # 14 günlük RSI
    'rsi_7',            # 7 günlük RSI (hızlı)
    'rsi_21',           # 21 günlük RSI (yavaş)
    'stoch_k',          # Stochastic %K
    'stoch_d',          # Stochastic %D
    'cci',              # Commodity Channel Index
    'mfi',              # Money Flow Index
    'roc',              # Rate of Change
    'williams_r',       # Williams %R
    
    # Volatility Indicators (Volatilite Göstergeleri)
    'bb_upper',         # Bollinger Bands üst band
    'bb_middle',        # Bollinger Bands orta band
    'bb_lower',         # Bollinger Bands alt band
    'bb_width',         # Bollinger Bands genişliği
    'bb_position',      # Fiyatın Bollinger Bands içindeki pozisyonu
    'atr',              # Average True Range
    'atr_percent',      # ATR yüzde olarak
    'keltner_upper',    # Keltner Channel üst band
    'keltner_lower',    # Keltner Channel alt band
    'volatility_ratio', # Volatilite oranı
    
    # Volume Indicators (Hacim Göstergeleri)
    'volume_sma_20',    # 20 günlük hacim ortalaması
    'volume_ratio',     # Mevcut hacim / ortalama hacim
    'obv',              # On-Balance Volume
    'obv_ema',          # OBV üstel hareketli ortalaması
    'vwap',             # Volume Weighted Average Price
    'cmf',              # Chaikin Money Flow
    'accumulation',     # Akümülasyon/dağıtım göstergesi
    'volume_oscillator',# Hacim osilatörü
    
    # Price Action Features (Fiyat Hareketi Özellikleri)
    'price_change_1h',  # Son 1 saatlik fiyat değişimi
    'price_change_4h',  # Son 4 saatlik fiyat değişimi
    'price_change_24h', # Son 24 saatlik fiyat değişimi
    'price_change_7d',  # Son 7 günlük fiyat değişimi
    'high_low_ratio',   # Yüksek/düşük oranı
    'close_position',   # Kapanış fiyatının günlük aralıktaki pozisyonu
    'body_size',        # Mum gövde büyüklüğü
    'upper_wick',       # Üst fitil büyüklüğü
    'lower_wick',       # Alt fitil büyüklüğü
    'gap_size',         # Açılış gap büyüklüğü
    
    # Support/Resistance Features (Destek/Direnç Özellikleri)
    'distance_to_support',   # En yakın desteğe uzaklık
    'distance_to_resistance',# En yakın dirençe uzaklık
    'support_strength',      # Destek gücü
    'resistance_strength',   # Direnç gücü
    'pivot_point',          # Pivot noktası
    'fibonacci_382',        # Fibonacci 38.2% seviyesi
    'fibonacci_500',        # Fibonacci 50.0% seviyesi
    'fibonacci_618',        # Fibonacci 61.8% seviyesi
    
    # Market Structure Features (Piyasa Yapısı Özellikleri)
    'higher_highs',     # Yükselen tepeler sayısı
    'lower_lows',       # Alçalan dipler sayısı
    'trend_strength',   # Trend gücü skoru
    'consolidation',    # Konsolidasyon göstergesi
    'breakout_potential',# Kırılma potansiyeli
    'swing_high_low',   # Swing yüksek/düşük oranı
    
    # Order Book Features (Emir Defteri Özellikleri)
    'bid_ask_spread',   # Alış-satış farkı
    'bid_volume',       # Alış tarafı hacmi
    'ask_volume',       # Satış tarafı hacmi
    'order_imbalance',  # Emir dengesizliği
    'depth_ratio',      # Derinlik oranı
    'large_orders',     # Büyük emirlerin varlığı
    
    # Time-based Features (Zaman Bazlı Özellikler)
    'hour_of_day',      # Günün saati (0-23)
    'day_of_week',      # Haftanın günü (0-6)
    'is_weekend',       # Hafta sonu mu
    'trading_session',  # İşlem seansı (Asya/Avrupa/Amerika)
    
    # Cross-asset Features (Çapraz Varlık Özellikleri)
    'btc_correlation',  # Bitcoin ile korelasyon
    'market_correlation',# Genel piyasa ile korelasyon
    'sector_performance',# Sektör performansı
    
    # Derived Features (Türetilmiş Özellikler)
    'momentum_composite',    # Kompozit momentum skoru
    'trend_composite',       # Kompozit trend skoru
    'volume_composite',      # Kompozit hacim skoru
    'volatility_composite',  # Kompozit volatilite skoru
    'quality_score',         # Genel kalite skoru
]

# ML Feature Kategorileri (Model eğitiminde gruplandırma için)
ML_FEATURE_CATEGORIES = {
    'trend': [
        'sma_20', 'sma_50', 'sma_200', 'ema_9', 'ema_21', 'ema_55',
        'macd', 'macd_signal', 'macd_histogram', 'adx', 'adx_pos', 'adx_neg'
    ],
    'momentum': [
        'rsi_14', 'rsi_7', 'rsi_21', 'stoch_k', 'stoch_d',
        'cci', 'mfi', 'roc', 'williams_r'
    ],
    'volatility': [
        'bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_position',
        'atr', 'atr_percent', 'keltner_upper', 'keltner_lower', 'volatility_ratio'
    ],
    'volume': [
        'volume_sma_20', 'volume_ratio', 'obv', 'obv_ema',
        'vwap', 'cmf', 'accumulation', 'volume_oscillator'
    ],
    'price_action': [
        'price_change_1h', 'price_change_4h', 'price_change_24h', 'price_change_7d',
        'high_low_ratio', 'close_position', 'body_size', 'upper_wick', 'lower_wick', 'gap_size'
    ],
    'support_resistance': [
        'distance_to_support', 'distance_to_resistance', 'support_strength',
        'resistance_strength', 'pivot_point', 'fibonacci_382', 'fibonacci_500', 'fibonacci_618'
    ],
    'market_structure': [
        'higher_highs', 'lower_lows', 'trend_strength',
        'consolidation', 'breakout_potential', 'swing_high_low'
    ],
    'orderbook': [
        'bid_ask_spread', 'bid_volume', 'ask_volume',
        'order_imbalance', 'depth_ratio', 'large_orders'
    ],
    'temporal': [
        'hour_of_day', 'day_of_week', 'is_weekend', 'trading_session'
    ],
    'cross_asset': [
        'btc_correlation', 'market_correlation', 'sector_performance'
    ],
    'composite': [
        'momentum_composite', 'trend_composite', 'volume_composite',
        'volatility_composite', 'quality_score'
    ]
}

# ML Model Konfigürasyonu
ML_CONFIG = {
    'train_test_split': 0.8,           # Eğitim/test ayrımı
    'validation_split': 0.2,           # Validation ayrımı
    'min_samples_for_training': 1000,  # Minimum eğitim örneği
    'feature_importance_threshold': 0.01, # Özellik önem eşiği
    'correlation_threshold': 0.95,     # Yüksek korelasyon eşiği
    'update_frequency_hours': 24,      # Model güncelleme sıklığı (saat)
    'prediction_confidence_threshold': 0.7, # Tahmin güven eşiği
    'ensemble_models': ['random_forest', 'gradient_boost', 'neural_network'],
    'cross_validation_folds': 5,       # Cross-validation fold sayısı
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
    
    # Yüksek volatilite = düşük kaldıraç
    if volatility > 15:
        max_lev = 50
    elif volatility > 10:
        max_lev = 100
    elif volatility > 5:
        max_lev = 200
    else:
        max_lev = trading_config.MAX_LEVERAGE
    
    # Yüksek skor = yüksek kaldıraç
    if score >= 90:
        leverage = max_lev
    elif score >= 80:
        leverage = int(max_lev * 0.8)
    elif score >= 70:
        leverage = int(max_lev * 0.6)
    else:
        leverage = int(max_lev * 0.4)
    
    # Limitleri kontrol et
    leverage = max(trading_config.MIN_LEVERAGE, leverage)
    leverage = min(trading_config.MAX_LEVERAGE, leverage)
    
    return leverage
