"""
MEXC Pro Trading Bot - Helper Functions
Yardımcı fonksiyonlar
"""

import numpy as np
from typing import List, Tuple
from datetime import datetime, timedelta

def format_price(price: float, decimals: int = 8) -> str:
    """Fiyatı formatla"""
    if price >= 1:
        return f"${price:,.{min(2, decimals)}f}"
    else:
        return f"${price:.{decimals}f}"

def format_percent(value: float, decimals: int = 2) -> str:
    """Yüzdeyi formatla"""
    return f"{value:+.{decimals}f}%"

def calculate_percent_change(old_value: float, new_value: float) -> float:
    """Yüzde değişim hesapla"""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100

def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    """Average True Range hesapla"""
    if len(highs) < period + 1:
        return 0.0
    
    true_ranges = []
    for i in range(1, len(highs)):
        high_low = highs[i] - lows[i]
        high_close = abs(highs[i] - closes[i-1])
        low_close = abs(lows[i] - closes[i-1])
        true_ranges.append(max(high_low, high_close, low_close))
    
    if len(true_ranges) < period:
        return 0.0
    
    return np.mean(true_ranges[-period:])

def calculate_volatility(prices: List[float], period: int = 20) -> float:
    """Volatilite hesapla (standart sapma)"""
    if len(prices) < period:
        return 0.0
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
    
    if len(returns) < period:
        return 0.0
    
    volatility = np.std(returns[-period:]) * np.sqrt(365) * 100
    return volatility

def timeframe_to_seconds(timeframe: str) -> int:
    """Timeframe'i saniyeye çevir"""
    from config.constants import TIME_PERIODS
    return TIME_PERIODS.get(timeframe, 3600)

def seconds_to_timeframe_string(seconds: int) -> str:
    """Saniyeyi zaman string'ine çevir"""
    if seconds < 60:
        return f"{seconds} saniye"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} dakika"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} saat"
    else:
        days = seconds // 86400
        return f"{days} gün"

def calculate_support_resistance(prices: List[float], window: int = 20) -> Tuple[List[float], List[float]]:
    """Support ve resistance seviyelerini hesapla"""
    if len(prices) < window:
        return [], []
    
    supports = []
    resistances = []
    
    for i in range(window, len(prices) - window):
        # Local minima (support)
        if prices[i] == min(prices[i-window:i+window+1]):
            supports.append(prices[i])
        
        # Local maxima (resistance)
        if prices[i] == max(prices[i-window:i+window+1]):
            resistances.append(prices[i])
    
    # Benzer seviyeleri birleştir
    supports = merge_similar_levels(supports)
    resistances = merge_similar_levels(resistances)
    
    return supports, resistances

def merge_similar_levels(levels: List[float], threshold: float = 0.02) -> List[float]:
    """Birbirine yakın seviyeleri birleştir"""
    if not levels:
        return []
    
    sorted_levels = sorted(levels)
    merged = [sorted_levels[0]]
    
    for level in sorted_levels[1:]:
        if abs(level - merged[-1]) / merged[-1] > threshold:
            merged.append(level)
        else:
            # Ortalamayı al
            merged[-1] = (merged[-1] + level) / 2
    
    return merged

def calculate_ema(prices: List[float], period: int) -> List[float]:
    """Exponential Moving Average hesapla"""
    if len(prices) < period:
        return []
    
    ema = []
    multiplier = 2 / (period + 1)
    
    # İlk EMA = SMA
    sma = sum(prices[:period]) / period
    ema.append(sma)
    
    # EMA hesapla
    for price in prices[period:]:
        ema_value = (price - ema[-1]) * multiplier + ema[-1]
        ema.append(ema_value)
    
    return ema

def calculate_sma(prices: List[float], period: int) -> List[float]:
    """Simple Moving Average hesapla"""
    if len(prices) < period:
        return []
    
    sma = []
    for i in range(period - 1, len(prices)):
        avg = sum(prices[i-period+1:i+1]) / period
        sma.append(avg)
    
    return sma

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Relative Strength Index hesapla"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
    """MACD hesapla"""
    if len(prices) < slow:
        return 0.0, 0.0, 0.0
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    if not ema_fast or not ema_slow:
        return 0.0, 0.0, 0.0
    
    # MACD line
    macd_line = ema_fast[-1] - ema_slow[-1]
    
    # Signal line (9 period EMA of MACD)
    macd_values = [ema_fast[i] - ema_slow[i] for i in range(len(ema_slow))]
    signal_line_values = calculate_ema(macd_values, signal)
    signal_line = signal_line_values[-1] if signal_line_values else 0.0
    
    # Histogram
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
    """Bollinger Bands hesapla"""
    if len(prices) < period:
        return 0.0, 0.0, 0.0
    
    sma = calculate_sma(prices, period)
    if not sma:
        return 0.0, 0.0, 0.0
    
    middle = sma[-1]
    
    # Standard deviation
    variance = sum((p - middle) ** 2 for p in prices[-period:]) / period
    std = variance ** 0.5
    
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    return upper, middle, lower

def detect_trend(prices: List[float], period: int = 20) -> Tuple[str, float]:
    """Trend tespit et"""
    if len(prices) < period:
        return "sideways", 0.0
    
    recent_prices = prices[-period:]
    
    # Linear regression ile trend hesapla
    x = np.arange(len(recent_prices))
    coefficients = np.polyfit(x, recent_prices, 1)
    slope = coefficients[0]
    
    # Trend strength
    avg_price = np.mean(recent_prices)
    strength = abs(slope) / avg_price * 100 * period
    
    # Trend direction
    if strength > 5:
        if slope > 0:
            trend = "strong_uptrend"
        else:
            trend = "strong_downtrend"
    elif strength > 2:
        if slope > 0:
            trend = "uptrend"
        else:
            trend = "downtrend"
    else:
        trend = "sideways"
    
    return trend, strength

def estimate_duration(volatility: float, target_percent: float) -> int:
    """Hedefe ulaşma süresini tahmin et (dakika)"""
    # Basit heuristik: yüksek volatilite = daha hızlı
    if volatility > 20:
        base_duration = 60  # 1 saat
    elif volatility > 10:
        base_duration = 120  # 2 saat
    elif volatility > 5:
        base_duration = 240  # 4 saat
    else:
        base_duration = 480  # 8 saat
    
    # Hedef yüzdeye göre ayarla
    duration_multiplier = target_percent / 4.0
    estimated = int(base_duration * duration_multiplier)
    
    # Min/max limitleri
    from config.settings import trading_config
    estimated = max(trading_config.MIN_HOLDING_TIME, estimated)
    estimated = min(trading_config.MAX_HOLDING_TIME, estimated)
    
    return estimated

def format_duration(minutes: int) -> str:
    """Süreyi okunabilir formata çevir"""
    if minutes < 60:
        return f"{minutes} dakika"
    elif minutes < 1440:
        hours = minutes / 60
        if hours < 2:
            return f"{hours:.1f} saat"
        return f"{int(hours)} saat"
    else:
        days = minutes / 1440
        return f"{days:.1f} gün"

def get_risk_level(leverage: int, score: float) -> str:
    """Risk seviyesini belirle"""
    if leverage > 200 or score < 70:
        return "YÜKSEK"
    elif leverage > 100 or score < 80:
        return "ORTA"
    else:
        return "DÜŞÜK"