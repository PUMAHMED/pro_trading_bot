“””
MEXC Pro Trading Bot - Constants
Sabit değerler ve enum’lar
“””

from enum import Enum, auto
from typing import Dict

class SignalType(Enum):
“”“Sinyal türleri”””
LONG = “LONG”
SHORT = “SHORT”

class SignalQuality(Enum):
“”“Sinyal kalite seviyeleri”””
EXCELLENT = “🔥 MÜKEMMEL”
HIGH = “⭐ YÜKSEK”
MEDIUM = “✅ ORTA”
LOW = “⚠️ DÜŞÜK”

class SignalStatus(Enum):
“”“Sinyal durumları”””
ACTIVE = “active”
TP1_HIT = “tp1_hit”
TP2_HIT = “tp2_hit”
TP3_HIT = “tp3_hit”
SL_HIT = “sl_hit”
EXPIRED = “expired”
CANCELLED = “cancelled”

class MarketPhase(Enum):
“”“Piyasa fazları”””
ACCUMULATION = “accumulation”
MARKUP = “markup”
DISTRIBUTION = “distribution”
MARKDOWN = “markdown”
RANGING = “ranging”

class TrendDirection(Enum):
“”“Trend yönleri”””
STRONG_UPTREND = “strong_uptrend”
UPTREND = “uptrend”
SIDEWAYS = “sideways”
DOWNTREND = “downtrend”
STRONG_DOWNTREND = “strong_downtrend”

class ManipulationType(Enum):
“”“Manipülasyon türleri”””
PUMP = “pump”
DUMP = “dump”
WASH_TRADING = “wash_trading”
SPOOFING = “spoofing”
LIQUIDITY_HUNT = “liquidity_hunt”
NONE = “none”

class ExchangeName(Enum):
“”“Exchange isimleri”””
MEXC = “MEXC”
BINANCE = “Binance”

# Emoji ve simgeler

EMOJIS = {
‘rocket’: ‘🚀’,
‘fire’: ‘🔥’,
‘star’: ‘⭐’,
‘check’: ‘✅’,
‘warning’: ‘⚠️’,
‘cross’: ‘❌’,
‘chart_up’: ‘📈’,
‘chart_down’: ‘📉’,
‘money’: ‘💰’,
‘bell’: ‘🔔’,
‘target’: ‘🎯’,
‘shield’: ‘🛡️’,
‘clock’: ‘⏰’,
‘brain’: ‘🧠’,
‘crystal_ball’: ‘🔮’,
‘whale’: ‘🐋’,
‘magnifying_glass’: ‘🔍’,
‘gear’: ‘⚙️’,
‘document’: ‘📄’,
‘lightning’: ‘⚡’,
‘trophy’: ‘🏆’,
‘graph’: ‘📊’,
‘robot’: ‘🤖’,
‘info’: ‘ℹ️’,
‘exclamation’: ‘❗’,
‘bullseye’: ‘🎯’,
‘up_arrow’: ‘⬆️’,
‘down_arrow’: ‘⬇️’,
‘hourglass’: ‘⏳’,
‘checkmark’: ‘✓’,
‘xmark’: ‘✗’
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
‘trend’: 0.25,
‘momentum’: 0.20,
‘volume’: 0.20,
‘support_resistance’: 0.15,
‘pattern’: 0.10,
‘orderbook’: 0.10
}

# Volume analizi için kategoriler

VOLUME_CATEGORIES = {
‘very_high’: 3.0,  # Normal’in 3x üstü
‘high’: 2.0,       # Normal’in 2x üstü
‘normal’: 1.0,     # Normal range
‘low’: 0.5,        # Normal’in altı
‘very_low’: 0.25   # Çok düşük
}

# RSI seviyeleri

RSI_LEVELS = {
‘extreme_oversold’: 20,
‘oversold’: 30,
‘neutral_low’: 40,
‘neutral_high’: 60,
‘overbought’: 70,
‘extreme_overbought’: 80
}

# Bollinger Bands pozisyonları

BB_POSITIONS = {
‘below_lower’: -2.0,
‘at_lower’: -1.0,
‘middle_lower’: -0.5,
‘middle’: 0.0,
‘middle_upper’: 0.5,
‘at_upper’: 1.0,
‘above_upper’: 2.0
}

# Pattern güven skorları

PATTERN_CONFIDENCE = {
‘double_bottom’: 0.85,
‘double_top’: 0.85,
‘head_shoulders’: 0.80,
‘inverse_head_shoulders’: 0.80,
‘triangle_breakout’: 0.75,
‘flag’: 0.70,
‘wedge’: 0.70,
‘channel_breakout’: 0.65
}

# Kaldıraç risk seviyeleri

LEVERAGE_RISK_MAP = {
(20, 50): ‘low’,
(51, 100): ‘medium’,
(101, 200): ‘high’,
(201, 500): ‘extreme’
}

# Zaman periyotları (saniye)

TIME_PERIODS = {
‘1m’: 60,
‘5m’: 300,
‘15m’: 900,
‘30m’: 1800,
‘1h’: 3600,
‘2h’: 7200,
‘4h’: 14400,
‘6h’: 21600,
‘12h’: 43200,
‘1d’: 86400
}

# Telegram komutları

BOT_COMMANDS = {
‘start’: ‘Botu başlat’,
‘help’: ‘Yardım menüsü’,
‘status’: ‘Bot durumu’,
‘stats’: ‘İstatistikler’,
‘analyze’: ‘Coin analiz et’,
‘settings’: ‘Ayarlar’,
‘report’: ‘Günlük rapor’,
‘stop’: ‘Taramayı durdur’,
‘resume’: ‘Taramayı başlat’
}

# Hata mesajları

ERROR_MESSAGES = {
‘api_error’: ‘❌ API bağlantı hatası’,
‘rate_limit’: ‘⚠️ Rate limit aşıldı, bekleniyor…’,
‘invalid_symbol’: ‘❌ Geçersiz coin sembolü’,
‘insufficient_data’: ‘⚠️ Yetersiz veri’,
‘analysis_failed’: ‘❌ Analiz başarısız’,
‘database_error’: ‘❌ Veritabanı hatası’,
‘network_error’: ‘❌ Ağ bağlantı hatası’
}

# Başarı mesajları

SUCCESS_MESSAGES = {
‘scan_started’: ‘✅ Tarama başlatıldı’,
‘scan_stopped’: ‘✅ Tarama durduruldu’,
‘signal_sent’: ‘✅ Sinyal gönderildi’,
‘settings_updated’: ‘✅ Ayarlar güncellendi’,
‘report_generated’: ‘✅ Rapor oluşturuldu’
}

# API endpoint’leri

API_ENDPOINTS = {
‘mexc’: {
‘base’: ‘https://api.mexc.com’,
‘futures_base’: ‘https://contract.mexc.com’
},
‘binance’: {
‘base’: ‘https://api.binance.com’,
‘futures_base’: ‘https://fapi.binance.com’
}
}

# Webhook URL’leri (opsiyonel)

WEBHOOK_URLS = {
‘tradingview’: ‘’,
‘custom’: ‘’
}

# Chart stilleri

CHART_STYLE = {
‘colors’: {
‘up’: ‘#26a69a’,
‘down’: ‘#ef5350’,
‘volume_up’: ‘#26a69a80’,
‘volume_down’: ‘#ef535080’,
‘ma_fast’: ‘#2196F3’,
‘ma_slow’: ‘#FF9800’,
‘rsi’: ‘#9C27B0’,
‘macd’: ‘#00BCD4’,
‘signal’: ‘#FF5722’
},
‘figure_size’: (12, 8),
‘dpi’: 100
}

# PDF rapor stilleri

PDF_STYLE = {
‘title_font_size’: 24,
‘heading_font_size’: 16,
‘text_font_size’: 11,
‘colors’: {
‘primary’: ‘#1976D2’,
‘success’: ‘#4CAF50’,
‘warning’: ‘#FF9800’,
‘danger’: ‘#F44336’,
‘text’: ‘#212121’,
‘background’: ‘#FAFAFA’
}
}

# Database tablo isimleri

DB_TABLES = {
‘signals’: ‘signals’,
‘scans’: ‘scans’,
‘analysis’: ‘analysis_results’,
‘performance’: ‘performance_metrics’,
‘coins’: ‘coin_list’,
‘ml_predictions’: ‘ml_predictions’,
‘whale_activity’: ‘whale_activity’,
‘market_data’: ‘market_data’
}

# Cache key prefix’leri

CACHE_KEYS = {
‘kline’: ‘kline:’,
‘ticker’: ‘ticker:’,
‘orderbook’: ‘orderbook:’,
‘analysis’: ‘analysis:’,
‘coin_list’: ‘coins:’,
‘volume_profile’: ‘volume_profile:’
}

# Webhook event tipleri

WEBHOOK_EVENTS = {
‘signal_created’: ‘signal.created’,
‘signal_updated’: ‘signal.updated’,
‘tp_hit’: ‘target.hit’,
‘sl_hit’: ‘stoploss.hit’,
‘analysis_broken’: ‘analysis.broken’
}

# Machine Learning feature’ları

ML_FEATURES = [
‘rsi’, ‘macd’, ‘macd_signal’, ‘macd_hist’,
‘bb_upper’, ‘bb_middle’, ‘bb_lower’, ‘bb_width’,
‘ema_fast’, ‘ema_slow’, ‘ema_diff’,
‘volume_ratio’, ‘volume_trend’,
‘price_change_1h’, ‘price_change_4h’, ‘price_change_24h’,
‘high_low_ratio’, ‘close_open_ratio’,
‘support_distance’, ‘resistance_distance’,
‘trend_strength’, ‘momentum_score’,
‘volatility’, ‘atr’,
‘orderbook_imbalance’, ‘spread_percent’,
‘whale_orders_ratio’, ‘large_trades_count’
]

# Notification templates

NOTIFICATION_TEMPLATES = {
‘signal’: “””
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
“””,
‘update’: “””
🔄 SİNYAL GÜNCELLENDİ

💎 Coin: {symbol}
📊 Güncelleme: {update_type}

{details}
“””,
‘tp_reached’: “””
🎉 HEDEF ULAŞILDI!

💎 Coin: {symbol}
🎯 {tp_level}: {price}
💰 Kar: {profit}%

⏱️ Süre: {duration}
“””,
‘heartbeat’: “””
💓 Sistem Durumu

⏰ {timestamp}
✅ Tarama: Aktif
📊 İşlenen Coin: {coins_scanned}
📈 Bugünkü Sinyaller: {signals_today}
🎯 Başarı Oranı: {success_rate}%
“””
}

def get_quality_from_score(score: float) -> SignalQuality:
“”“Skordan kalite seviyesi belirle”””
if score >= QUALITY_THRESHOLDS[SignalQuality.EXCELLENT]:
return SignalQuality.EXCELLENT
elif score >= QUALITY_THRESHOLDS[SignalQuality.HIGH]:
return SignalQuality.HIGH
elif score >= QUALITY_THRESHOLDS[SignalQuality.MEDIUM]:
return SignalQuality.MEDIUM
else:
return SignalQuality.LOW

def get_leverage_recommendation(score: float, volatility: float) -> int:
“”“Skordan kaldıraç önerisi”””
from config.settings import trading_config

```
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
```
