"""
MEXC Pro Trading Bot - Pattern Analyzer
Chart pattern recognition
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from config.constants import PATTERN_CONFIDENCE
from utils.logger import get_logger

logger = get_logger(__name__)

class PatternAnalyzer:
    """Pattern tanıma sınıfı"""
    
    def __init__(self):
        self.pattern_confidence = PATTERN_CONFIDENCE
    
    async def analyze(self, ohlcv_data: List[List], symbol: str) -> Dict[str, Any]:
        """Pattern analizi yap"""
        try:
            if len(ohlcv_data) < 50:
                logger.warning(f"⚠️ {symbol}: Pattern analizi için yetersiz veri")
                return self._empty_analysis()
            
            closes = [candle[4] for candle in ohlcv_data]
            highs = [candle[2] for candle in ohlcv_data]
            lows = [candle[3] for candle in ohlcv_data]
            
            # Tüm pattern'leri kontrol et
            patterns_found = []
            
            # Double Top/Bottom
            double_top = self._detect_double_top(highs, closes)
            if double_top:
                patterns_found.append(double_top)
            
            double_bottom = self._detect_double_bottom(lows, closes)
            if double_bottom:
                patterns_found.append(double_bottom)
            
            # Head and Shoulders
            head_shoulders = self._detect_head_shoulders(highs, closes)
            if head_shoulders:
                patterns_found.append(head_shoulders)
            
            inverse_hs = self._detect_inverse_head_shoulders(lows, closes)
            if inverse_hs:
                patterns_found.append(inverse_hs)
            
            # Triangles
            triangle = self._detect_triangle(highs, lows, closes)
            if triangle:
                patterns_found.append(triangle)
            
            # Flags and Pennants
            flag = self._detect_flag(ohlcv_data)
            if flag:
                patterns_found.append(flag)
            
            # Wedges
            wedge = self._detect_wedge(highs, lows)
            if wedge:
                patterns_found.append(wedge)
            
            # Channels
            channel = self._detect_channel(highs, lows, closes)
            if channel:
                patterns_found.append(channel)
            
            # Candlestick patterns
            candle_patterns = self._detect_candlestick_patterns(ohlcv_data[-10:])
            patterns_found.extend(candle_patterns)
            
            # En güçlü pattern'i seç
            strongest_pattern = max(patterns_found, key=lambda x: x['confidence']) if patterns_found else None
            
            # Pattern score hesapla
            pattern_score = self._calculate_pattern_score(patterns_found, strongest_pattern)
            
            return {
                'symbol': symbol,
                'pattern_score': round(pattern_score, 2),
                'patterns_found': len(patterns_found),
                'has_patterns': len(patterns_found) > 0,
                'patterns': patterns_found,
                'strongest_pattern': strongest_pattern,
                'bullish_patterns': len([p for p in patterns_found if p['direction'] == 'bullish']),
                'bearish_patterns': len([p for p in patterns_found if p['direction'] == 'bearish'])
            }
            
        except Exception as e:
            logger.error(f"❌ Pattern analiz hatası {symbol}: {e}", exc_info=True)
            return self._empty_analysis()
    
    def _detect_double_top(self, highs: List[float], closes: List[float]) -> Optional[Dict[str, Any]]:
        """Double Top pattern tespit et"""
        if len(highs) < 30:
            return None
        
        recent_highs = highs[-30:]
        
        # İki benzer peak bul
        peaks = self._find_peaks(recent_highs, prominence=2)
        
        if len(peaks) >= 2:
            last_two_peaks = peaks[-2:]
            peak1_val = recent_highs[last_two_peaks[0]]
            peak2_val = recent_highs[last_two_peaks[1]]
            
            # Peak'ler birbirine yakın mı?
            similarity = abs(peak1_val - peak2_val) / peak1_val
            
            if similarity < 0.03:  # %3 içinde
                return {
                    'name': 'double_top',
                    'type': 'reversal',
                    'direction': 'bearish',
                    'confidence': self.pattern_confidence['double_top'] * (1 - similarity),
                    'description': 'Double Top - Bearish Reversal'
                }
        
        return None
    
    def _detect_double_bottom(self, lows: List[float], closes: List[float]) -> Optional[Dict[str, Any]]:
        """Double Bottom pattern tespit et"""
        if len(lows) < 30:
            return None
        
        recent_lows = lows[-30:]
        
        # İki benzer valley bul
        valleys = self._find_valleys(recent_lows, prominence=2)
        
        if len(valleys) >= 2:
            last_two_valleys = valleys[-2:]
            valley1_val = recent_lows[last_two_valleys[0]]
            valley2_val = recent_lows[last_two_valleys[1]]
            
            similarity = abs(valley1_val - valley2_val) / valley1_val
            
            if similarity < 0.03:
                return {
                    'name': 'double_bottom',
                    'type': 'reversal',
                    'direction': 'bullish',
                    'confidence': self.pattern_confidence['double_bottom'] * (1 - similarity),
                    'description': 'Double Bottom - Bullish Reversal'
                }
        
        return None
    
    def _detect_head_shoulders(self, highs: List[float], closes: List[float]) -> Optional[Dict[str, Any]]:
        """Head and Shoulders pattern"""
        if len(highs) < 40:
            return None
        
        recent_highs = highs[-40:]
        peaks = self._find_peaks(recent_highs, prominence=2)
        
        if len(peaks) >= 3:
            # Son 3 peak'i al
            last_three = peaks[-3:]
            left_shoulder = recent_highs[last_three[0]]
            head = recent_highs[last_three[1]]
            right_shoulder = recent_highs[last_three[2]]
            
            # Head en yüksek olmalı
            if head > left_shoulder and head > right_shoulder:
                # Shoulder'lar benzer olmalı
                shoulder_similarity = abs(left_shoulder - right_shoulder) / left_shoulder
                
                if shoulder_similarity < 0.05:  # %5 içinde
                    return {
                        'name': 'head_shoulders',
                        'type': 'reversal',
                        'direction': 'bearish',
                        'confidence': self.pattern_confidence['head_shoulders'] * (1 - shoulder_similarity),
                        'description': 'Head and Shoulders - Bearish Reversal'
                    }
        
        return None
    
    def _detect_inverse_head_shoulders(self, lows: List[float], closes: List[float]) -> Optional[Dict[str, Any]]:
        """Inverse Head and Shoulders pattern"""
        if len(lows) < 40:
            return None
        
        recent_lows = lows[-40:]
        valleys = self._find_valleys(recent_lows, prominence=2)
        
        if len(valleys) >= 3:
            last_three = valleys[-3:]
            left_shoulder = recent_lows[last_three[0]]
            head = recent_lows[last_three[1]]
            right_shoulder = recent_lows[last_three[2]]
            
            if head < left_shoulder and head < right_shoulder:
                shoulder_similarity = abs(left_shoulder - right_shoulder) / left_shoulder
                
                if shoulder_similarity < 0.05:
                    return {
                        'name': 'inverse_head_shoulders',
                        'type': 'reversal',
                        'direction': 'bullish',
                        'confidence': self.pattern_confidence['inverse_head_shoulders'] * (1 - shoulder_similarity),
                        'description': 'Inverse Head and Shoulders - Bullish Reversal'
                    }
        
        return None
    
    def _detect_triangle(self, highs: List[float], lows: List[float], closes: List[float]) -> Optional[Dict[str, Any]]:
        """Triangle pattern (ascending, descending, symmetrical)"""
        if len(highs) < 20:
            return None
        
        recent_highs = highs[-20:]
        recent_lows = lows[-20:]
        
        # Trend lines
        high_slope = self._calculate_slope(recent_highs)
        low_slope = self._calculate_slope(recent_lows)
        
        # Ascending triangle: flat top, rising bottom
        if abs(high_slope) < 0.001 and low_slope > 0.002:
            return {
                'name': 'ascending_triangle',
                'type': 'continuation',
                'direction': 'bullish',
                'confidence': 0.75,
                'description': 'Ascending Triangle - Bullish Continuation'
            }
        
        # Descending triangle: falling top, flat bottom
        if high_slope < -0.002 and abs(low_slope) < 0.001:
            return {
                'name': 'descending_triangle',
                'type': 'continuation',
                'direction': 'bearish',
                'confidence': 0.75,
                'description': 'Descending Triangle - Bearish Continuation'
            }
        
        # Symmetrical triangle
        if high_slope < -0.001 and low_slope > 0.001:
            return {
                'name': 'symmetrical_triangle',
                'type': 'continuation',
                'direction': 'neutral',
                'confidence': 0.70,
                'description': 'Symmetrical Triangle - Breakout Expected'
            }
        
        return None
    
    def _detect_flag(self, ohlcv_data: List[List]) -> Optional[Dict[str, Any]]:
        """Flag pattern"""
        if len(ohlcv_data) < 30:
            return None
        
        # Son 30 mum
        recent_data = ohlcv_data[-30:]
        closes = [c[4] for c in recent_data]
        
        # Güçlü hareket + konsolidasyon
        first_half = closes[:15]
        second_half = closes[15:]
        
        first_half_change = (first_half[-1] - first_half[0]) / first_half[0] * 100
        second_half_volatility = np.std(second_half) / np.mean(second_half) * 100
        
        # Bull flag: güçlü yükseliş + düşük volatilite konsolidasyon
        if first_half_change > 5 and second_half_volatility < 3:
            return {
                'name': 'bull_flag',
                'type': 'continuation',
                'direction': 'bullish',
                'confidence': 0.70,
                'description': 'Bull Flag - Bullish Continuation'
            }
        
        # Bear flag
        if first_half_change < -5 and second_half_volatility < 3:
            return {
                'name': 'bear_flag',
                'type': 'continuation',
                'direction': 'bearish',
                'confidence': 0.70,
                'description': 'Bear Flag - Bearish Continuation'
            }
        
        return None
    
    def _detect_wedge(self, highs: List[float], lows: List[float]) -> Optional[Dict[str, Any]]:
        """Wedge pattern (rising, falling)"""
        if len(highs) < 20:
            return None
        
        high_slope = self._calculate_slope(highs[-20:])
        low_slope = self._calculate_slope(lows[-20:])
        
        # Rising wedge: her ikisi de yükseliyor ama low daha hızlı
        if high_slope > 0 and low_slope > 0 and low_slope > high_slope * 1.2:
            return {
                'name': 'rising_wedge',
                'type': 'reversal',
                'direction': 'bearish',
                'confidence': 0.70,
                'description': 'Rising Wedge - Bearish Reversal'
            }
        
        # Falling wedge: her ikisi de düşüyor ama high daha yavaş
        if high_slope < 0 and low_slope < 0 and abs(low_slope) > abs(high_slope) * 1.2:
            return {
                'name': 'falling_wedge',
                'type': 'reversal',
                'direction': 'bullish',
                'confidence': 0.70,
                'description': 'Falling Wedge - Bullish Reversal'
            }
        
        return None
    
    def _detect_channel(self, highs: List[float], lows: List[float], closes: List[float]) -> Optional[Dict[str, Any]]:
        """Channel pattern"""
        if len(highs) < 30:
            return None
        
        high_slope = self._calculate_slope(highs[-30:])
        low_slope = self._calculate_slope(lows[-30:])
        
        # Parallel channel: benzer eğim
        slope_diff = abs(high_slope - low_slope)
        
        if slope_diff < 0.001:  # Paralel
            if high_slope > 0.002:
                return {
                    'name': 'ascending_channel',
                    'type': 'trend',
                    'direction': 'bullish',
                    'confidence': 0.65,
                    'description': 'Ascending Channel - Uptrend'
                }
            elif high_slope < -0.002:
                return {
                    'name': 'descending_channel',
                    'type': 'trend',
                    'direction': 'bearish',
                    'confidence': 0.65,
                    'description': 'Descending Channel - Downtrend'
                }
            else:
                return {
                    'name': 'horizontal_channel',
                    'type': 'range',
                    'direction': 'neutral',
                    'confidence': 0.60,
                    'description': 'Horizontal Channel - Range Bound'
                }
        
        return None
    
    def _detect_candlestick_patterns(self, ohlcv_data: List[List]) -> List[Dict[str, Any]]:
        """Candlestick pattern'leri tespit et"""
        patterns = []
        
        if len(ohlcv_data) < 3:
            return patterns
        
        # Engulfing
        engulfing = self._detect_engulfing(ohlcv_data[-2:])
        if engulfing:
            patterns.append(engulfing)
        
        # Hammer / Hanging Man
        hammer = self._detect_hammer(ohlcv_data[-1])
        if hammer:
            patterns.append(hammer)
        
        # Doji
        doji = self._detect_doji(ohlcv_data[-1])
        if doji:
            patterns.append(doji)
        
        # Morning/Evening Star
        star = self._detect_star(ohlcv_data[-3:])
        if star:
            patterns.append(star)
        
        return patterns
    
    def _detect_engulfing(self, candles: List[List]) -> Optional[Dict[str, Any]]:
        """Engulfing pattern"""
        if len(candles) < 2:
            return None
        
        prev_candle = candles[0]
        curr_candle = candles[1]
        
        prev_open, prev_close = prev_candle[1], prev_candle[4]
        curr_open, curr_close = curr_candle[1], curr_candle[4]
        
        # Bullish engulfing
        if prev_close < prev_open and curr_close > curr_open:
            if curr_open <= prev_close and curr_close >= prev_open:
                return {
                    'name': 'bullish_engulfing',
                    'type': 'reversal',
                    'direction': 'bullish',
                    'confidence': 0.75,
                    'description': 'Bullish Engulfing - Reversal Signal'
                }
        
        # Bearish engulfing
        if prev_close > prev_open and curr_close < curr_open:
            if curr_open >= prev_close and curr_close <= prev_open:
                return {
                    'name': 'bearish_engulfing',
                    'type': 'reversal',
                    'direction': 'bearish',
                    'confidence': 0.75,
                    'description': 'Bearish Engulfing - Reversal Signal'
                }
        
        return None
    
    def _detect_hammer(self, candle: List) -> Optional[Dict[str, Any]]:
        """Hammer / Hanging Man"""
        open_price, high, low, close = candle[1], candle[2], candle[3], candle[4]
        
        body = abs(close - open_price)
        lower_shadow = min(open_price, close) - low
        upper_shadow = high - max(open_price, close)
        
        if body > 0 and lower_shadow > body * 2 and upper_shadow < body * 0.5:
            if close > open_price:
                return {
                    'name': 'hammer',
                    'type': 'reversal',
                    'direction': 'bullish',
                    'confidence': 0.70,
                    'description': 'Hammer - Bullish Reversal'
                }
            else:
                return {
                    'name': 'hanging_man',
                    'type': 'reversal',
                    'direction': 'bearish',
                    'confidence': 0.65,
                    'description': 'Hanging Man - Bearish Reversal'
                }
        
        return None
    
    def _detect_doji(self, candle: List) -> Optional[Dict[str, Any]]:
        """Doji candlestick"""
        open_price, high, low, close = candle[1], candle[2], candle[3], candle[4]
        
        body = abs(close - open_price)
        total_range = high - low
        
        if total_range > 0 and body / total_range < 0.1:
            return {
                'name': 'doji',
                'type': 'indecision',
                'direction': 'neutral',
                'confidence': 0.60,
                'description': 'Doji - Market Indecision'
            }
        
        return None
    
    def _detect_star(self, candles: List[List]) -> Optional[Dict[str, Any]]:
        """Morning/Evening Star"""
        if len(candles) < 3:
            return None
        
        first, second, third = candles
        
        first_body = abs(first[4] - first[1])
        second_body = abs(second[4] - second[1])
        third_body = abs(third[4] - third[1])
        
        # Morning star
        if first[4] < first[1] and third[4] > third[1]:
            if second_body < first_body * 0.3:
                return {
                    'name': 'morning_star',
                    'type': 'reversal',
                    'direction': 'bullish',
                    'confidence': 0.75,
                    'description': 'Morning Star - Bullish Reversal'
                }
        
        # Evening star
        if first[4] > first[1] and third[4] < third[1]:
            if second_body < first_body * 0.3:
                return {
                    'name': 'evening_star',
                    'type': 'reversal',
                    'direction': 'bearish',
                    'confidence': 0.75,
                    'description': 'Evening Star - Bearish Reversal'
                }
        
        return None
    
    def _find_peaks(self, data: List[float], prominence: int = 1) -> List[int]:
        """Peak noktalarını bul"""
        peaks = []
        for i in range(prominence, len(data) - prominence):
            is_peak = all(data[i] > data[i-j] and data[i] > data[i+j] for j in range(1, prominence + 1))
            if is_peak:
                peaks.append(i)
        return peaks
    
    def _find_valleys(self, data: List[float], prominence: int = 1) -> List[int]:
        """Valley noktalarını bul"""
        valleys = []
        for i in range(prominence, len(data) - prominence):
            is_valley = all(data[i] < data[i-j] and data[i] < data[i+j] for j in range(1, prominence + 1))
            if is_valley:
                valleys.append(i)
        return valleys
    
    def _calculate_slope(self, data: List[float]) -> float:
        """Veri setinin eğimini hesapla"""
        if len(data) < 2:
            return 0.0
        
        x = np.arange(len(data))
        coefficients = np.polyfit(x, data, 1)
        return coefficients[0]
    
    def _calculate_pattern_score(self, patterns: List[Dict], strongest: Optional[Dict]) -> float:
        """Pattern skorunu hesapla"""
        if not patterns:
            return 50
        
        score = 50
        
        # Strongest pattern contribution
        if strongest:
            confidence_boost = strongest['confidence'] * 30
            if strongest['direction'] == 'bullish':
                score += confidence_boost
            elif strongest['direction'] == 'bearish':
                score -= confidence_boost
        
        # Consensus contribution
        bullish_count = len([p for p in patterns if p['direction'] == 'bullish'])
        bearish_count = len([p for p in patterns if p['direction'] == 'bearish'])
        
        if bullish_count > bearish_count:
            score += (bullish_count - bearish_count) * 5
        elif bearish_count > bullish_count:
            score -= (bearish_count - bullish_count) * 5
        
        return max(0, min(100, score))
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Boş analiz sonucu"""
        return {
            'symbol': '',
            'pattern_score': 50,
            'patterns_found': 0,
            'has_patterns': False,
            'patterns': [],
            'strongest_pattern': None,
            'bullish_patterns': 0,
            'bearish_patterns': 0
        }
