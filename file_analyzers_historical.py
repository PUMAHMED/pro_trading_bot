"""
MEXC Pro Trading Bot - Historical Analyzer
Geçmiş fiyat hareketleri analizi
Bu modül günlük yüksek hareketleri analiz ederek pattern'leri öğrenir
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)

class HistoricalAnalyzer:
    """Geçmiş veriler analiz sınıfı"""
    
    def __init__(self):
        self.min_data_points = 100
    
    async def analyze_pre_movement_conditions(
        self,
        historical_ohlcv: List[List],
        symbol: str,
        target_move_percent: float = 20.0
    ) -> Dict[str, Any]:
        """
        Büyük hareketlerden önceki koşulları analiz et
        Bu fonksiyon geçmişte %20-30 hareket eden coinlerin
        o hareketten önceki durumlarını analiz eder
        """
        try:
            if len(historical_ohlcv) < self.min_data_points:
                logger.warning(f"⚠️ {symbol}: Yetersiz historical veri")
                return self._empty_analysis()
            
            # Büyük hareketleri tespit et
            significant_moves = self._find_significant_moves(
                historical_ohlcv,
                target_move_percent
            )
            
            if not significant_moves:
                return {
                    'symbol': symbol,
                    'has_historical_patterns': False,
                    'significant_moves_found': 0,
                    'message': 'Geçmişte büyük hareket tespit edilemedi'
                }
            
            # Her büyük hareket için pre-conditions analiz et
            pre_movement_patterns = []
            
            for move in significant_moves:
                pattern = self._analyze_pre_conditions(
                    historical_ohlcv,
                    move['start_index'],
                    move['move_percent'],
                    move['direction']
                )
                if pattern:
                    pre_movement_patterns.append(pattern)
            
            # Pattern'leri aggregate et
            aggregated_patterns = self._aggregate_patterns(pre_movement_patterns)
            
            # Common characteristics bul
            common_characteristics = self._find_common_characteristics(pre_movement_patterns)
            
            # Predictive score hesapla
            predictive_score = self._calculate_predictive_score(
                pre_movement_patterns,
                common_characteristics
            )
            
            return {
                'symbol': symbol,
                'has_historical_patterns': True,
                'significant_moves_found': len(significant_moves),
                'analyzed_patterns': len(pre_movement_patterns),
                
                # Ortalama pre-movement koşullar
                'average_pre_conditions': aggregated_patterns,
                
                # Ortak özellikler
                'common_characteristics': common_characteristics,
                
                # Tahmin gücü
                'predictive_score': round(predictive_score, 2),
                'reliability': self._get_reliability_level(predictive_score),
                
                # Detaylı pattern'ler (en iyi 5)
                'top_patterns': sorted(
                    pre_movement_patterns,
                    key=lambda x: x.get('confidence', 0),
                    reverse=True
                )[:5],
                
                # İstatistikler
                'statistics': self._calculate_statistics(significant_moves)
            }
            
        except Exception as e:
            logger.error(f"❌ Historical analiz hatası {symbol}: {e}", exc_info=True)
            return self._empty_analysis()
    
    def _find_significant_moves(
        self,
        ohlcv_data: List[List],
        target_percent: float
    ) -> List[Dict[str, Any]]:
        """Büyük fiyat hareketlerini tespit et"""
        significant_moves = []
        
        closes = [candle[4] for candle in ohlcv_data]
        
        # Sliding window ile büyük hareketleri ara
        window_size = 24  # 24 saatlik pencere (15m timeframe için 96 mum)
        
        for i in range(len(closes) - window_size):
            window = closes[i:i + window_size]
            
            # Window içindeki en düşük ve en yüksek
            min_price = min(window)
            max_price = max(window)
            start_price = window[0]
            
            # Yükseliş hareketi
            if max_price > start_price:
                move_percent = (max_price - start_price) / start_price * 100
                if move_percent >= target_percent:
                    significant_moves.append({
                        'start_index': i,
                        'move_percent': move_percent,
                        'direction': 'up',
                        'start_price': start_price,
                        'peak_price': max_price,
                        'duration_candles': window_size
                    })
            
            # Düşüş hareketi
            if min_price < start_price:
                move_percent = abs((min_price - start_price) / start_price * 100)
                if move_percent >= target_percent:
                    significant_moves.append({
                        'start_index': i,
                        'move_percent': move_percent,
                        'direction': 'down',
                        'start_price': start_price,
                        'bottom_price': min_price,
                        'duration_candles': window_size
                    })
        
        return significant_moves
    
    def _analyze_pre_conditions(
        self,
        ohlcv_data: List[List],
        move_start_index: int,
        move_percent: float,
        direction: str
    ) -> Optional[Dict[str, Any]]:
        """Hareket öncesi koşulları analiz et"""
        
        # Hareketten önceki 50 mumu al
        pre_window = 50
        if move_start_index < pre_window:
            return None
        
        pre_data = ohlcv_data[move_start_index - pre_window:move_start_index]
        
        closes = [c[4] for c in pre_data]
        volumes = [c[5] for c in pre_data]
        highs = [c[2] for c in pre_data]
        lows = [c[3] for c in pre_data]
        
        # Çeşitli metrikleri hesapla
        
        # 1. Volatilite
        volatility = (np.std(closes) / np.mean(closes) * 100) if np.mean(closes) > 0 else 0
        
        # 2. Volume trend
        first_half_vol = np.mean(volumes[:25])
        second_half_vol = np.mean(volumes[25:])
        volume_trend = 'increasing' if second_half_vol > first_half_vol * 1.2 else 'stable'
        volume_change = ((second_half_vol - first_half_vol) / first_half_vol * 100) if first_half_vol > 0 else 0
        
        # 3. Konsolidasyon
        price_range = (max(closes) - min(closes)) / min(closes) * 100 if min(closes) > 0 else 0
        is_consolidating = price_range < 5  # %5'ten az hareket
        
        # 4. Support/Resistance test
        support_tests = self._count_support_tests(lows)
        resistance_tests = self._count_resistance_tests(highs)
        
        # 5. Volume pattern
        volume_spikes = self._count_volume_spikes(volumes)
        
        # 6. Price action
        higher_lows = self._count_higher_lows(lows)
        lower_highs = self._count_lower_highs(highs)
        
        # 7. Momentum buildup
        momentum_score = self._calculate_momentum_buildup(closes, volumes)
        
        # 8. Liquidity accumulation
        liquidity_score = self._calculate_liquidity_accumulation(volumes)
        
        # Confidence hesapla (bu pattern'in ne kadar güçlü olduğu)
        confidence = self._calculate_pattern_confidence(
            volatility=volatility,
            volume_trend=volume_trend,
            is_consolidating=is_consolidating,
            support_tests=support_tests,
            momentum_score=momentum_score
        )
        
        return {
            'move_percent': round(move_percent, 2),
            'direction': direction,
            'confidence': round(confidence, 2),
            
            # Pre-movement koşullar
            'pre_conditions': {
                'volatility': round(volatility, 2),
                'volatility_level': self._categorize_volatility(volatility),
                
                'volume_trend': volume_trend,
                'volume_change_percent': round(volume_change, 2),
                'volume_spikes': volume_spikes,
                
                'consolidation': is_consolidating,
                'price_range_percent': round(price_range, 2),
                
                'support_tests': support_tests,
                'resistance_tests': resistance_tests,
                
                'higher_lows_count': higher_lows,
                'lower_highs_count': lower_highs,
                
                'momentum_score': round(momentum_score, 2),
                'liquidity_score': round(liquidity_score, 2),
                
                # Teknik seviyeler
                'was_oversold': self._was_oversold(closes),
                'was_overbought': self._was_overbought(closes)
            }
        }
    
    def _count_support_tests(self, lows: List[float]) -> int:
        """Support seviyesine kaç kez test edildi"""
        if not lows:
            return 0
        
        # En düşük seviyeye yakın touchlar
        min_low = min(lows)
        threshold = min_low * 1.02  # %2 threshold
        
        tests = sum(1 for low in lows if low <= threshold)
        return tests
    
    def _count_resistance_tests(self, highs: List[float]) -> int:
        """Resistance seviyesine kaç kez test edildi"""
        if not highs:
            return 0
        
        max_high = max(highs)
        threshold = max_high * 0.98  # %2 threshold
        
        tests = sum(1 for high in highs if high >= threshold)
        return tests
    
    def _count_volume_spikes(self, volumes: List[float]) -> int:
        """Volume spike sayısı"""
        if len(volumes) < 10:
            return 0
        
        avg_volume = np.mean(volumes)
        spikes = sum(1 for vol in volumes if vol > avg_volume * 2)
        return spikes
    
    def _count_higher_lows(self, lows: List[float]) -> int:
        """Higher lows pattern sayısı"""
        if len(lows) < 3:
            return 0
        
        count = 0
        for i in range(2, len(lows)):
            if lows[i] > lows[i-1] and lows[i-1] > lows[i-2]:
                count += 1
        return count
    
    def _count_lower_highs(self, highs: List[float]) -> int:
        """Lower highs pattern sayısı"""
        if len(highs) < 3:
            return 0
        
        count = 0
        for i in range(2, len(highs)):
            if highs[i] < highs[i-1] and highs[i-1] < highs[i-2]:
                count += 1
        return count
    
    def _calculate_momentum_buildup(self, closes: List[float], volumes: List[float]) -> float:
        """Momentum birikimiini hesapla"""
        if len(closes) < 20 or len(volumes) < 20:
            return 0
        
        # Son 20 mumda momentum
        price_momentum = (closes[-1] - closes[-20]) / closes[-20] * 100 if closes[-20] > 0 else 0
        
        # Volume momentum
        recent_vol = np.mean(volumes[-10:])
        older_vol = np.mean(volumes[-20:-10]) if len(volumes) >= 20 else recent_vol
        volume_momentum = (recent_vol / older_vol - 1) * 100 if older_vol > 0 else 0
        
        # Combine
        momentum = (abs(price_momentum) + volume_momentum) / 2
        return max(0, min(100, momentum))
    
    def _calculate_liquidity_accumulation(self, volumes: List[float]) -> float:
        """Likidite birikimi skoru"""
        if len(volumes) < 20:
            return 0
        
        # Volume consistency
        volume_consistency = 1 - (np.std(volumes) / np.mean(volumes)) if np.mean(volumes) > 0 else 0
        
        # Volume uptrend
        first_half = np.mean(volumes[:len(volumes)//2])
        second_half = np.mean(volumes[len(volumes)//2:])
        volume_growth = (second_half / first_half - 1) if first_half > 0 else 0
        
        liquidity_score = (volume_consistency * 50) + (min(volume_growth, 1) * 50)
        return max(0, min(100, liquidity_score))
    
    def _calculate_pattern_confidence(
        self,
        volatility: float,
        volume_trend: str,
        is_consolidating: bool,
        support_tests: int,
        momentum_score: float
    ) -> float:
        """Pattern güven skorunu hesapla"""
        confidence = 50
        
        # Düşük volatilite + konsolidasyon = güçlü pattern
        if is_consolidating and volatility < 3:
            confidence += 20
        
        # Volume artışı = güçlü
        if volume_trend == 'increasing':
            confidence += 15
        
        # Support testleri = accumulation
        if support_tests >= 3:
            confidence += 15
        
        # Momentum buildup
        if momentum_score > 50:
            confidence += 10
        
        return max(0, min(100, confidence))
    
    def _categorize_volatility(self, volatility: float) -> str:
        """Volatilite kategorisi"""
        if volatility < 2:
            return 'very_low'
        elif volatility < 4:
            return 'low'
        elif volatility < 6:
            return 'moderate'
        elif volatility < 10:
            return 'high'
        else:
            return 'very_high'
    
    def _was_oversold(self, closes: List[float]) -> bool:
        """RSI oversold seviyesinde miydi"""
        from utils.helpers import calculate_rsi
        rsi = calculate_rsi(closes, 14)
        return rsi < 35
    
    def _was_overbought(self, closes: List[float]) -> bool:
        """RSI overbought seviyesinde miydi"""
        from utils.helpers import calculate_rsi
        rsi = calculate_rsi(closes, 14)
        return rsi > 65
    
    def _aggregate_patterns(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Pattern'leri aggregate et ve ortalamaları al"""
        if not patterns:
            return {}
        
        # Her metriğin ortalamasını al
        aggregated = {
            'avg_volatility': np.mean([p['pre_conditions']['volatility'] for p in patterns]),
            'avg_volume_change': np.mean([p['pre_conditions']['volume_change_percent'] for p in patterns]),
            'avg_support_tests': np.mean([p['pre_conditions']['support_tests'] for p in patterns]),
            'avg_momentum_score': np.mean([p['pre_conditions']['momentum_score'] for p in patterns]),
            'avg_liquidity_score': np.mean([p['pre_conditions']['liquidity_score'] for p in patterns]),
            
            # Percentage that had these characteristics
            'consolidation_percentage': sum(1 for p in patterns if p['pre_conditions']['consolidation']) / len(patterns) * 100,
            'oversold_percentage': sum(1 for p in patterns if p['pre_conditions']['was_oversold']) / len(patterns) * 100,
            'volume_increasing_percentage': sum(1 for p in patterns if p['pre_conditions']['volume_trend'] == 'increasing') / len(patterns) * 100
        }
        
        return {k: round(v, 2) for k, v in aggregated.items()}
    
    def _find_common_characteristics(self, patterns: List[Dict]) -> List[str]:
        """Ortak özellikleri bul"""
        if len(patterns) < 2:
            return []
        
        common = []
        
        # Konsolidasyon
        consolidation_count = sum(1 for p in patterns if p['pre_conditions']['consolidation'])
        if consolidation_count / len(patterns) >= 0.7:  # %70+
            common.append("📊 Hareket öncesi genelde konsolidasyon var")
        
        # Volume artışı
        volume_inc_count = sum(1 for p in patterns if p['pre_conditions']['volume_trend'] == 'increasing')
        if volume_inc_count / len(patterns) >= 0.6:
            common.append("📈 Volume artışı sıklıkla görülüyor")
        
        # Düşük volatilite
        low_vol_count = sum(1 for p in patterns if p['pre_conditions']['volatility'] < 5)
        if low_vol_count / len(patterns) >= 0.6:
            common.append("🔽 Düşük volatilite periyodu öncesinde görülüyor")
        
        # Support testleri
        support_count = sum(1 for p in patterns if p['pre_conditions']['support_tests'] >= 3)
        if support_count / len(patterns) >= 0.5:
            common.append("🛡️ Multiple support testleri yaygın")
        
        # Momentum buildup
        momentum_count = sum(1 for p in patterns if p['pre_conditions']['momentum_score'] > 60)
        if momentum_count / len(patterns) >= 0.5:
            common.append("⚡ Güçlü momentum birikimiyle başlıyor")
        
        return common
    
    def _calculate_predictive_score(
        self,
        patterns: List[Dict],
        common_characteristics: List[str]
    ) -> float:
        """Bu pattern'lerin tahmin gücü ne kadar?"""
        if not patterns:
            return 0
        
        score = 50
        
        # Pattern sayısı
        if len(patterns) >= 10:
            score += 20
        elif len(patterns) >= 5:
            score += 10
        
        # Ortak özellikler
        score += len(common_characteristics) * 5
        
        # Ortalama confidence
        avg_confidence = np.mean([p['confidence'] for p in patterns])
        score += (avg_confidence - 50) * 0.5
        
        return max(0, min(100, score))
    
    def _get_reliability_level(self, score: float) -> str:
        """Güvenilirlik seviyesi"""
        if score >= 80:
            return 'VERY_HIGH'
        elif score >= 65:
            return 'HIGH'
        elif score >= 50:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def _calculate_statistics(self, moves: List[Dict]) -> Dict[str, Any]:
        """İstatistikler"""
        if not moves:
            return {}
        
        up_moves = [m for m in moves if m['direction'] == 'up']
        down_moves = [m for m in moves if m['direction'] == 'down']
        
        return {
            'total_moves': len(moves),
            'up_moves': len(up_moves),
            'down_moves': len(down_moves),
            'avg_move_percent': round(np.mean([m['move_percent'] for m in moves]), 2),
            'max_move_percent': round(max([m['move_percent'] for m in moves]), 2),
            'avg_up_move': round(np.mean([m['move_percent'] for m in up_moves]), 2) if up_moves else 0,
            'avg_down_move': round(np.mean([m['move_percent'] for m in down_moves]), 2) if down_moves else 0
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Boş analiz sonucu"""
        return {
            'symbol': '',
            'has_historical_patterns': False,
            'significant_moves_found': 0,
            'message': 'Analiz yapılamadı'
        }