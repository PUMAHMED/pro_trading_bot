"""
MEXC Pro Trading Bot - Volume Analyzer
Volume profil analizi
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from config.settings import analysis_config, scanner_config
from config.constants import VOLUME_CATEGORIES
from utils.helpers import calculate_sma
from utils.logger import get_logger

logger = get_logger(__name__)

class VolumeAnalyzer:
    """Volume analiz sınıfı"""
    
    def __init__(self):
        self.config = analysis_config
        self.scanner_config = scanner_config
    
    async def analyze(self, ohlcv_data: List[List], symbol: str) -> Dict[str, Any]:
        """Volume analizi yap"""
        try:
            if len(ohlcv_data) < 30:
                logger.warning(f"⚠️ {symbol}: Volume analizi için yetersiz veri")
                return self._empty_analysis()
            
            volumes = [candle[5] for candle in ohlcv_data]
            closes = [candle[4] for candle in ohlcv_data]
            highs = [candle[2] for candle in ohlcv_data]
            lows = [candle[3] for candle in ohlcv_data]
            
            current_volume = volumes[-1]
            current_price = closes[-1]
            
            # Volume MA
            volume_ma = calculate_sma(volumes, self.config.VOLUME_MA_PERIOD)
            avg_volume = volume_ma[-1] if volume_ma else np.mean(volumes)
            
            # Volume ratio
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Volume trend
            volume_trend = self._calculate_volume_trend(volumes)
            
            # Volume category
            volume_category = self._categorize_volume(volume_ratio)
            
            # Volume-Price correlation
            vp_correlation = self._calculate_volume_price_correlation(volumes[-20:], closes[-20:])
            
            # Buying/Selling pressure
            buy_pressure, sell_pressure = self._calculate_pressure(ohlcv_data[-20:])
            
            # Volume spike detection
            is_spike, spike_strength = self._detect_volume_spike(volumes, volume_ratio)
            
            # Accumulation/Distribution
            accumulation_dist = self._calculate_accumulation_distribution(ohlcv_data[-50:])
            
            # Volume profile
            volume_profile = self._create_volume_profile(ohlcv_data[-100:])
            
            # Volume score hesapla
            volume_score = self._calculate_volume_score({
                'volume_ratio': volume_ratio,
                'volume_trend': volume_trend,
                'vp_correlation': vp_correlation,
                'buy_pressure': buy_pressure,
                'sell_pressure': sell_pressure,
                'is_spike': is_spike,
                'spike_strength': spike_strength,
                'accumulation_dist': accumulation_dist
            })
            
            # On-Balance Volume (OBV)
            obv = self._calculate_obv(ohlcv_data[-50:])
            obv_trend = self._get_obv_trend(obv)
            
            # Money Flow Index (MFI) benzeri
            money_flow = self._calculate_money_flow(ohlcv_data[-20:])
            
            return {
                'symbol': symbol,
                'volume_score': round(volume_score, 2),
                
                # Volume metrikleri
                'current_volume': round(current_volume, 2),
                'average_volume': round(avg_volume, 2),
                'volume_ratio': round(volume_ratio, 2),
                'volume_category': volume_category,
                'volume_trend': volume_trend,
                
                # Spike detection
                'is_volume_spike': is_spike,
                'spike_strength': round(spike_strength, 2),
                
                # Pressure
                'buy_pressure_percent': round(buy_pressure, 2),
                'sell_pressure_percent': round(sell_pressure, 2),
                'net_pressure': round(buy_pressure - sell_pressure, 2),
                'pressure_direction': 'bullish' if buy_pressure > sell_pressure else 'bearish',
                
                # Correlation
                'volume_price_correlation': round(vp_correlation, 2),
                
                # Accumulation/Distribution
                'accumulation_distribution': round(accumulation_dist, 2),
                'accumulation_trend': 'accumulation' if accumulation_dist > 0 else 'distribution',
                
                # OBV
                'obv': round(obv, 2),
                'obv_trend': obv_trend,
                
                # Money flow
                'money_flow_ratio': round(money_flow, 2),
                
                # Volume profile
                'value_area_high': round(volume_profile['value_area_high'], 8),
                'value_area_low': round(volume_profile['value_area_low'], 8),
                'point_of_control': round(volume_profile['poc'], 8),
                'price_above_value_area': current_price > volume_profile['value_area_high'],
                'price_below_value_area': current_price < volume_profile['value_area_low']
            }
            
        except Exception as e:
            logger.error(f"❌ Volume analiz hatası {symbol}: {e}", exc_info=True)
            return self._empty_analysis()
    
    def _calculate_volume_trend(self, volumes: List[float], period: int = 10) -> str:
        """Volume trendini hesapla"""
        if len(volumes) < period:
            return 'neutral'
        
        recent_volumes = volumes[-period:]
        older_volumes = volumes[-period*2:-period] if len(volumes) >= period*2 else volumes[-period:]
        
        recent_avg = np.mean(recent_volumes)
        older_avg = np.mean(older_volumes)
        
        if recent_avg > older_avg * 1.2:
            return 'increasing'
        elif recent_avg < older_avg * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _categorize_volume(self, ratio: float) -> str:
        """Volume kategorisi belirle"""
        if ratio >= VOLUME_CATEGORIES['very_high']:
            return 'very_high'
        elif ratio >= VOLUME_CATEGORIES['high']:
            return 'high'
        elif ratio >= VOLUME_CATEGORIES['normal']:
            return 'normal'
        elif ratio >= VOLUME_CATEGORIES['low']:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_volume_price_correlation(self, volumes: List[float], prices: List[float]) -> float:
        """Volume-fiyat korelasyonu hesapla"""
        if len(volumes) != len(prices) or len(volumes) < 2:
            return 0.0
        
        try:
            correlation = np.corrcoef(volumes, prices)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    def _calculate_pressure(self, ohlcv_data: List[List]) -> Tuple[float, float]:
        """Alım/satım baskısını hesapla"""
        buy_volume = 0
        sell_volume = 0
        
        for candle in ohlcv_data:
            open_price = candle[1]
            high = candle[2]
            low = candle[3]
            close = candle[4]
            volume = candle[5]
            
            # Basit heuristik: Close > Open = buying pressure
            if close > open_price:
                buy_volume += volume
            elif close < open_price:
                sell_volume += volume
            else:
                # Eşitse yarı yarıya böl
                buy_volume += volume / 2
                sell_volume += volume / 2
        
        total_volume = buy_volume + sell_volume
        if total_volume == 0:
            return 50.0, 50.0
        
        buy_pressure = (buy_volume / total_volume) * 100
        sell_pressure = (sell_volume / total_volume) * 100
        
        return buy_pressure, sell_pressure
    
    def _detect_volume_spike(self, volumes: List[float], current_ratio: float) -> Tuple[bool, float]:
        """Volume spike tespit et"""
        if len(volumes) < 20:
            return False, 0.0
        
        # Son 20 mum içinde standart sapma
        recent_volumes = volumes[-20:]
        mean_vol = np.mean(recent_volumes)
        std_vol = np.std(recent_volumes)
        
        if std_vol == 0:
            return False, 0.0
        
        # Z-score hesapla
        z_score = (volumes[-1] - mean_vol) / std_vol
        
        # Spike eşiği: 2.5 standart sapma
        is_spike = z_score > 2.5
        spike_strength = max(0, z_score - 2.5) * 10  # 0-100 arası normalize et
        
        return is_spike, min(spike_strength, 100)
    
    def _calculate_accumulation_distribution(self, ohlcv_data: List[List]) -> float:
        """Accumulation/Distribution Line hesapla"""
        ad_line = 0
        
        for candle in ohlcv_data:
            high = candle[2]
            low = candle[3]
            close = candle[4]
            volume = candle[5]
            
            if high != low:
                money_flow_multiplier = ((close - low) - (high - close)) / (high - low)
                money_flow_volume = money_flow_multiplier * volume
                ad_line += money_flow_volume
        
        return ad_line
    
    def _calculate_obv(self, ohlcv_data: List[List]) -> float:
        """On-Balance Volume hesapla"""
        obv = 0
        
        for i in range(1, len(ohlcv_data)):
            close = ohlcv_data[i][4]
            prev_close = ohlcv_data[i-1][4]
            volume = ohlcv_data[i][5]
            
            if close > prev_close:
                obv += volume
            elif close < prev_close:
                obv -= volume
        
        return obv
    
    def _get_obv_trend(self, obv: float) -> str:
        """OBV trend belirleme"""
        if obv > 0:
            if obv > 1000000:
                return 'strong_bullish'
            else:
                return 'bullish'
        elif obv < 0:
            if obv < -1000000:
                return 'strong_bearish'
            else:
                return 'bearish'
        else:
            return 'neutral'
    
    def _calculate_money_flow(self, ohlcv_data: List[List]) -> float:
        """Money Flow Ratio hesapla (MFI benzeri)"""
        positive_flow = 0
        negative_flow = 0
        
        for i in range(1, len(ohlcv_data)):
            typical_price = (ohlcv_data[i][2] + ohlcv_data[i][3] + ohlcv_data[i][4]) / 3
            prev_typical = (ohlcv_data[i-1][2] + ohlcv_data[i-1][3] + ohlcv_data[i-1][4]) / 3
            
            raw_money_flow = typical_price * ohlcv_data[i][5]
            
            if typical_price > prev_typical:
                positive_flow += raw_money_flow
            elif typical_price < prev_typical:
                negative_flow += raw_money_flow
        
        if negative_flow == 0:
            return 100.0
        
        money_flow_ratio = positive_flow / negative_flow
        return min(money_flow_ratio, 10)  # Cap at 10 for normalization
    
    def _create_volume_profile(self, ohlcv_data: List[List]) -> Dict[str, float]:
        """Volume profile oluştur (Value Area ve POC)"""
        if not ohlcv_data:
            return {'value_area_high': 0, 'value_area_low': 0, 'poc': 0}
        
        # Fiyat seviyelerini belirle
        all_prices = []
        for candle in ohlcv_data:
            all_prices.extend([candle[2], candle[3], candle[4]])  # high, low, close
        
        min_price = min(all_prices)
        max_price = max(all_prices)
        
        # 50 price level oluştur
        num_levels = 50
        price_step = (max_price - min_price) / num_levels if max_price > min_price else 1
        
        # Her seviyedeki volume'u hesapla
        volume_at_price = {}
        for i in range(num_levels):
            level_price = min_price + (i * price_step)
            volume_at_price[level_price] = 0
        
        # Volume dağılımını hesapla
        for candle in ohlcv_data:
            high = candle[2]
            low = candle[3]
            volume = candle[5]
            
            for price_level in volume_at_price.keys():
                if low <= price_level <= high:
                    volume_at_price[price_level] += volume
        
        # POC (Point of Control) - en yüksek volume seviyesi
        poc = max(volume_at_price, key=volume_at_price.get) if volume_at_price else 0
        
        # Value Area (top %70 volume)
        sorted_levels = sorted(volume_at_price.items(), key=lambda x: x[1], reverse=True)
        total_volume = sum(v for _, v in sorted_levels)
        target_volume = total_volume * 0.7
        
        accumulated_volume = 0
        value_area_prices = []
        
        for price, vol in sorted_levels:
            accumulated_volume += vol
            value_area_prices.append(price)
            if accumulated_volume >= target_volume:
                break
        
        value_area_high = max(value_area_prices) if value_area_prices else max_price
        value_area_low = min(value_area_prices) if value_area_prices else min_price
        
        return {
            'value_area_high': value_area_high,
            'value_area_low': value_area_low,
            'poc': poc
        }
    
    def _calculate_volume_score(self, metrics: Dict[str, Any]) -> float:
        """Volume skorunu hesapla"""
        score = 50  # Base score
        
        # Volume ratio
        ratio = metrics['volume_ratio']
        if ratio >= 3:
            score += 30
        elif ratio >= 2:
            score += 20
        elif ratio >= 1.5:
            score += 10
        elif ratio < 0.5:
            score -= 20
        
        # Volume trend
        if metrics['volume_trend'] == 'increasing':
            score += 15
        elif metrics['volume_trend'] == 'decreasing':
            score -= 15
        
        # Correlation
        correlation = metrics['vp_correlation']
        if correlation > 0.5:
            score += 10
        elif correlation < -0.5:
            score -= 10
        
        # Pressure
        net_pressure = metrics['buy_pressure'] - metrics['sell_pressure']
        score += net_pressure / 5  # -20 to +20
        
        # Spike
        if metrics['is_spike']:
            spike_contribution = min(metrics['spike_strength'] / 2, 20)
            score += spike_contribution
        
        # Accumulation/Distribution
        if metrics['accumulation_dist'] > 0:
            score += 10
        else:
            score -= 10
        
        return max(0, min(100, score))
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Boş analiz sonucu"""
        return {
            'symbol': '',
            'volume_score': 0,
            'current_volume': 0,
            'average_volume': 0,
            'volume_ratio': 0,
            'volume_category': 'unknown',
            'volume_trend': 'neutral',
            'is_volume_spike': False,
            'spike_strength': 0,
            'buy_pressure_percent': 50,
            'sell_pressure_percent': 50,
            'net_pressure': 0,
            'pressure_direction': 'neutral',
            'volume_price_correlation': 0,
            'accumulation_distribution': 0,
            'accumulation_trend': 'neutral',
            'obv': 0,
            'obv_trend': 'neutral',
            'money_flow_ratio': 1,
            'value_area_high': 0,
            'value_area_low': 0,
            'point_of_control': 0,
            'price_above_value_area': False,
            'price_below_value_area': False
        }
