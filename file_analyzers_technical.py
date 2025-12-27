"""
MEXC Pro Trading Bot - Technical Analyzer
Teknik analiz motoru
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from config.settings import analysis_config
from config.constants import RSI_LEVELS, BB_POSITIONS
from utils.helpers import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_ema, calculate_sma, detect_trend
)
from utils.logger import get_logger

logger = get_logger(__name__)

class TechnicalAnalyzer:
    """Teknik analiz sınıfı"""
    
    def __init__(self):
        self.config = analysis_config
    
    async def analyze(self, ohlcv_data: List[List], symbol: str) -> Dict[str, Any]:
        """Kapsamlı teknik analiz yap"""
        try:
            if len(ohlcv_data) < 50:
                logger.warning(f"⚠️ {symbol}: Yetersiz veri")
                return self._empty_analysis()
            
            # OHLCV verilerini ayır
            closes = [candle[4] for candle in ohlcv_data]
            highs = [candle[2] for candle in ohlcv_data]
            lows = [candle[3] for candle in ohlcv_data]
            volumes = [candle[5] for candle in ohlcv_data]
            
            current_price = closes[-1]
            
            # Tüm indikatörleri hesapla
            rsi = calculate_rsi(closes, self.config.RSI_PERIOD)
            macd, macd_signal, macd_hist = calculate_macd(
                closes,
                self.config.MACD_FAST,
                self.config.MACD_SLOW,
                self.config.MACD_SIGNAL
            )
            
            bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(
                closes,
                self.config.BB_PERIOD,
                self.config.BB_STD
            )
            
            ema_fast = calculate_ema(closes, self.config.EMA_FAST)
            ema_slow = calculate_ema(closes, self.config.EMA_SLOW)
            
            # Trend analizi
            trend, trend_strength = detect_trend(closes, period=20)
            
            # Support/Resistance
            support_levels, resistance_levels = self._calculate_sr_levels(closes)
            
            # Sinyal skorları hesapla
            rsi_score = self._score_rsi(rsi)
            macd_score = self._score_macd(macd, macd_signal, macd_hist)
            bb_score = self._score_bollinger(current_price, bb_upper, bb_middle, bb_lower)
            ema_score = self._score_ema(ema_fast, ema_slow, current_price)
            trend_score = self._score_trend(trend, trend_strength)
            sr_score = self._score_support_resistance(
                current_price,
                support_levels,
                resistance_levels
            )
            
            # Genel teknik skor
            technical_score = self._calculate_overall_score({
                'rsi': rsi_score,
                'macd': macd_score,
                'bb': bb_score,
                'ema': ema_score,
                'trend': trend_score,
                'sr': sr_score
            })
            
            # Sinyal yönü belirleme
            signal_direction = self._determine_direction({
                'rsi': rsi,
                'macd': macd,
                'macd_signal': macd_signal,
                'ema_fast': ema_fast[-1] if ema_fast else 0,
                'ema_slow': ema_slow[-1] if ema_slow else 0,
                'trend': trend,
                'price': current_price,
                'bb_middle': bb_middle
            })
            
            return {
                'symbol': symbol,
                'technical_score': round(technical_score, 2),
                'signal_direction': signal_direction,
                
                # İndikatörler
                'rsi': round(rsi, 2),
                'rsi_score': round(rsi_score, 2),
                'rsi_level': self._get_rsi_level(rsi),
                
                'macd': round(macd, 4),
                'macd_signal': round(macd_signal, 4),
                'macd_histogram': round(macd_hist, 4),
                'macd_score': round(macd_score, 2),
                'macd_crossover': 'bullish' if macd > macd_signal else 'bearish',
                
                'bb_upper': round(bb_upper, 8),
                'bb_middle': round(bb_middle, 8),
                'bb_lower': round(bb_lower, 8),
                'bb_position': self._get_bb_position(current_price, bb_upper, bb_middle, bb_lower),
                'bb_score': round(bb_score, 2),
                
                'ema_fast': round(ema_fast[-1], 8) if ema_fast else 0,
                'ema_slow': round(ema_slow[-1], 8) if ema_slow else 0,
                'ema_score': round(ema_score, 2),
                'ema_trend': 'bullish' if (ema_fast and ema_slow and ema_fast[-1] > ema_slow[-1]) else 'bearish',
                
                'trend': trend,
                'trend_strength': round(trend_strength, 2),
                'trend_score': round(trend_score, 2),
                
                'support_levels': [round(s, 8) for s in support_levels[:3]],
                'resistance_levels': [round(r, 8) for r in resistance_levels[:3]],
                'sr_score': round(sr_score, 2),
                
                'current_price': round(current_price, 8)
            }
            
        except Exception as e:
            logger.error(f"❌ Teknik analiz hatası {symbol}: {e}", exc_info=True)
            return self._empty_analysis()
    
    def _score_rsi(self, rsi: float) -> float:
        """RSI skorla"""
        if rsi <= RSI_LEVELS['extreme_oversold']:
            return 100  # Çok güçlü al sinyali
        elif rsi <= RSI_LEVELS['oversold']:
            return 80
        elif rsi <= RSI_LEVELS['neutral_low']:
            return 60
        elif rsi >= RSI_LEVELS['extreme_overbought']:
            return 0  # Çok güçlü sat sinyali
        elif rsi >= RSI_LEVELS['overbought']:
            return 20
        elif rsi >= RSI_LEVELS['neutral_high']:
            return 40
        else:
            return 50  # Nötr
    
    def _score_macd(self, macd: float, signal: float, hist: float) -> float:
        """MACD skorla"""
        score = 50
        
        # Crossover
        if macd > signal and hist > 0:
            score += 30  # Bullish crossover
        elif macd < signal and hist < 0:
            score -= 30  # Bearish crossover
        
        # Histogram büyüklüğü
        hist_strength = min(abs(hist) * 100, 20)
        if hist > 0:
            score += hist_strength
        else:
            score -= hist_strength
        
        return max(0, min(100, score))
    
    def _score_bollinger(self, price: float, upper: float, middle: float, lower: float) -> float:
        """Bollinger Bands skorla"""
        bb_width = upper - lower
        if bb_width == 0:
            return 50
        
        position = (price - lower) / bb_width
        
        if position <= 0.1:
            return 90  # Alt bandın altında - güçlü al
        elif position <= 0.3:
            return 70
        elif position >= 0.9:
            return 10  # Üst bandın üstünde - güçlü sat
        elif position >= 0.7:
            return 30
        else:
            return 50  # Ortada - nötr
    
    def _score_ema(self, ema_fast: List[float], ema_slow: List[float], price: float) -> float:
        """EMA skorla"""
        if not ema_fast or not ema_slow:
            return 50
        
        fast = ema_fast[-1]
        slow = ema_slow[-1]
        
        score = 50
        
        # EMA pozisyonu
        if fast > slow:
            score += 25  # Bullish
        else:
            score -= 25  # Bearish
        
        # Fiyatın EMA'lara göre pozisyonu
        if price > fast and price > slow:
            score += 25  # Güçlü bullish
        elif price < fast and price < slow:
            score -= 25  # Güçlü bearish
        
        return max(0, min(100, score))
    
    def _score_trend(self, trend: str, strength: float) -> float:
        """Trend skorla"""
        base_scores = {
            'strong_uptrend': 90,
            'uptrend': 70,
            'sideways': 50,
            'downtrend': 30,
            'strong_downtrend': 10
        }
        
        base = base_scores.get(trend, 50)
        
        # Trend gücüne göre ayarla
        adjustment = min(strength, 10)
        if 'uptrend' in trend:
            return min(100, base + adjustment)
        elif 'downtrend' in trend:
            return max(0, base - adjustment)
        else:
            return base
    
    def _score_support_resistance(
        self,
        price: float,
        supports: List[float],
        resistances: List[float]
    ) -> float:
        """Support/Resistance skorla"""
        score = 50
        
        # Support yakınlığı
        if supports:
            nearest_support = min(supports, key=lambda x: abs(x - price))
            support_distance = abs(price - nearest_support) / price * 100
            
            if support_distance < 1:  # %1 içinde
                score += 30  # Güçlü support
            elif support_distance < 2:
                score += 20
            elif support_distance < 3:
                score += 10
        
        # Resistance yakınlığı
        if resistances:
            nearest_resistance = min(resistances, key=lambda x: abs(x - price))
            resistance_distance = abs(price - nearest_resistance) / price * 100
            
            if resistance_distance < 1:
                score -= 30  # Güçlü resistance
            elif resistance_distance < 2:
                score -= 20
            elif resistance_distance < 3:
                score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Genel skoru hesapla"""
        from config.constants import INDICATOR_WEIGHTS
        
        # Trend ve momentum ağırlıklı
        weights = INDICATOR_WEIGHTS
        
        overall = (
            scores['rsi'] * weights['momentum'] +
            scores['macd'] * weights['momentum'] +
            scores['bb'] * weights['trend'] +
            scores['ema'] * weights['trend'] +
            scores['trend'] * weights['trend'] +
            scores['sr'] * weights['support_resistance']
        )
        
        return overall
    
    def _determine_direction(self, indicators: Dict[str, Any]) -> str:
        """Sinyal yönünü belirle"""
        bullish_votes = 0
        bearish_votes = 0
        
        # RSI
        if indicators['rsi'] < 40:
            bullish_votes += 1
        elif indicators['rsi'] > 60:
            bearish_votes += 1
        
        # MACD
        if indicators['macd'] > indicators['macd_signal']:
            bullish_votes += 1
        else:
            bearish_votes += 1
        
        # EMA
        if indicators['ema_fast'] > indicators['ema_slow']:
            bullish_votes += 1
        else:
            bearish_votes += 1
        
        # Trend
        if 'uptrend' in indicators['trend']:
            bullish_votes += 2  # Trend daha ağırlıklı
        elif 'downtrend' in indicators['trend']:
            bearish_votes += 2
        
        # Price vs BB Middle
        if indicators['price'] > indicators['bb_middle']:
            bullish_votes += 1
        else:
            bearish_votes += 1
        
        return 'LONG' if bullish_votes > bearish_votes else 'SHORT'
    
    def _calculate_sr_levels(self, prices: List[float]) -> Tuple[List[float], List[float]]:
        """Support ve resistance seviyelerini hesapla"""
        from utils.helpers import calculate_support_resistance
        return calculate_support_resistance(prices, window=20)
    
    def _get_rsi_level(self, rsi: float) -> str:
        """RSI seviye ismini al"""
        if rsi <= RSI_LEVELS['extreme_oversold']:
            return 'extreme_oversold'
        elif rsi <= RSI_LEVELS['oversold']:
            return 'oversold'
        elif rsi >= RSI_LEVELS['extreme_overbought']:
            return 'extreme_overbought'
        elif rsi >= RSI_LEVELS['overbought']:
            return 'overbought'
        else:
            return 'neutral'
    
    def _get_bb_position(self, price: float, upper: float, middle: float, lower: float) -> str:
        """Bollinger Bands pozisyonunu al"""
        if price > upper:
            return 'above_upper'
        elif price > middle:
            return 'upper_half'
        elif price > lower:
            return 'lower_half'
        else:
            return 'below_lower'
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Boş analiz sonucu"""
        return {
            'symbol': '',
            'technical_score': 0,
            'signal_direction': 'LONG',
            'rsi': 50,
            'rsi_score': 50,
            'rsi_level': 'neutral',
            'macd': 0,
            'macd_signal': 0,
            'macd_histogram': 0,
            'macd_score': 50,
            'macd_crossover': 'neutral',
            'bb_upper': 0,
            'bb_middle': 0,
            'bb_lower': 0,
            'bb_position': 'middle',
            'bb_score': 50,
            'ema_fast': 0,
            'ema_slow': 0,
            'ema_score': 50,
            'ema_trend': 'neutral',
            'trend': 'sideways',
            'trend_strength': 0,
            'trend_score': 50,
            'support_levels': [],
            'resistance_levels': [],
            'sr_score': 50,
            'current_price': 0
        }