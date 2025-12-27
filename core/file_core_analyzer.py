"""
MEXC Pro Trading Bot - Market Analyzer
Ana market analiz motoru - tüm analyzer'ları koordine eder
"""

from typing import Dict, Any, Optional
from analyzers.technical import TechnicalAnalyzer
from analyzers.volume import VolumeAnalyzer
from analyzers.orderbook import OrderBookAnalyzer
from analyzers.pattern import PatternAnalyzer
from analyzers.manipulation import ManipulationDetector
from analyzers.historical import HistoricalAnalyzer
from config.constants import INDICATOR_WEIGHTS
from utils.logger import get_logger

logger = get_logger(__name__)

class MarketAnalyzer:
    """Ana market analiz sınıfı - tüm analizleri koordine eder"""
    
    def __init__(self):
        # Tüm analyzer'ları başlat
        self.technical_analyzer = TechnicalAnalyzer()
        self.volume_analyzer = VolumeAnalyzer()
        self.orderbook_analyzer = OrderBookAnalyzer()
        self.pattern_analyzer = PatternAnalyzer()
        self.manipulation_detector = ManipulationDetector()
        self.historical_analyzer = HistoricalAnalyzer()
        
        logger.info("✅ MarketAnalyzer başlatıldı")
    
    async def analyze_comprehensive(
        self,
        symbol: str,
        ohlcv_data: list,
        orderbook: Dict[str, Any],
        ticker: Dict[str, Any],
        historical_data: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Kapsamlı market analizi
        Tüm analyzer'ları çalıştırır ve sonuçları birleştirir
        """
        try:
            logger.info(f"🔬 {symbol} için kapsamlı analiz başlatılıyor...")
            
            current_price = ticker.get('last', 0)
            
            # 1. Teknik Analiz
            technical_analysis = await self.technical_analyzer.analyze(ohlcv_data, symbol)
            
            # 2. Volume Analizi
            volume_analysis = await self.volume_analyzer.analyze(ohlcv_data, symbol)
            
            # 3. Order Book Analizi
            orderbook_analysis = await self.orderbook_analyzer.analyze(
                orderbook,
                symbol,
                current_price
            )
            
            # 4. Pattern Analizi
            pattern_analysis = await self.pattern_analyzer.analyze(ohlcv_data, symbol)
            
            # 5. Manipülasyon Tespiti
            manipulation_analysis = await self.manipulation_detector.analyze(
                ohlcv_data,
                orderbook,
                symbol,
                orderbook_analysis.get('whale_activity')
            )
            
            # 6. Historical Analiz (opsiyonel - eğer historical data varsa)
            historical_analysis = None
            if historical_data and len(historical_data) >= 100:
                historical_analysis = await self.historical_analyzer.analyze_pre_movement_conditions(
                    historical_data,
                    symbol,
                    target_move_percent=20.0
                )
            
            # Tüm sonuçları birleştir
            comprehensive_result = self._combine_analyses(
                symbol=symbol,
                technical=technical_analysis,
                volume=volume_analysis,
                orderbook=orderbook_analysis,
                pattern=pattern_analysis,
                manipulation=manipulation_analysis,
                historical=historical_analysis,
                current_price=current_price
            )
            
            logger.info(
                f"✅ {symbol} analiz tamamlandı - "
                f"Skor: {comprehensive_result['overall_score']}/100, "
                f"Yön: {comprehensive_result['signal_direction']}"
            )
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"❌ {symbol} analiz hatası: {e}", exc_info=True)
            return self._empty_analysis(symbol)
    
    def _combine_analyses(
        self,
        symbol: str,
        technical: Dict,
        volume: Dict,
        orderbook: Dict,
        pattern: Dict,
        manipulation: Dict,
        historical: Optional[Dict],
        current_price: float
    ) -> Dict[str, Any]:
        """Tüm analizleri birleştir ve genel skor hesapla"""
        
        # Individual skorlar
        technical_score = technical.get('technical_score', 50)
        volume_score = volume.get('volume_score', 50)
        orderbook_score = orderbook.get('orderbook_score', 50)
        pattern_score = pattern.get('pattern_score', 50)
        manipulation_score = manipulation.get('manipulation_score', 50)
        
        # Ağırlıklı ortalama skor
        weights = INDICATOR_WEIGHTS
        
        overall_score = (
            technical_score * (weights['trend'] + weights['momentum']) +
            volume_score * weights['volume'] +
            orderbook_score * weights['orderbook'] +
            pattern_score * weights['pattern'] +
            manipulation_score * weights['support_resistance']
        )
        
        # Manipülasyon riski varsa skoru düşür
        if not manipulation.get('is_safe_to_trade', True):
            overall_score *= 0.5  # %50 penalty
        
        # Pattern confidence bonus
        if pattern.get('has_patterns') and pattern.get('strongest_pattern'):
            confidence = pattern['strongest_pattern'].get('confidence', 0)
            overall_score += confidence * 0.1
        
        # Historical pattern bonus (eğer varsa)
        if historical and historical.get('has_historical_patterns'):
            predictive_score = historical.get('predictive_score', 0)
            overall_score += predictive_score * 0.15
        
        # Normalize et
        overall_score = max(0, min(100, overall_score))
        
        # Sinyal yönü belirleme (consensus)
        signal_direction = self._determine_signal_direction(
            technical.get('signal_direction'),
            volume.get('pressure_direction'),
            orderbook.get('pressure_direction'),
            pattern
        )
        
        # Güven seviyesi
        confidence_level = self._calculate_confidence(
            overall_score,
            manipulation.get('is_safe_to_trade', True),
            pattern.get('has_patterns', False)
        )
        
        # Analiz özeti oluştur
        analysis_summary = self._create_analysis_summary(
            technical=technical,
            volume=volume,
            orderbook=orderbook,
            pattern=pattern,
            manipulation=manipulation
        )
        
        return {
            'symbol': symbol,
            'timestamp': manipulation.get('timestamp', None) or technical.get('timestamp'),
            'current_price': current_price,
            
            # Genel metrikler
            'overall_score': round(overall_score, 2),
            'signal_direction': signal_direction,
            'confidence_level': confidence_level,
            
            # Individual skorlar
            'scores': {
                'technical': round(technical_score, 2),
                'volume': round(volume_score, 2),
                'orderbook': round(orderbook_score, 2),
                'pattern': round(pattern_score, 2),
                'manipulation_check': round(manipulation_score, 2)
            },
            
            # Detaylı analizler
            'technical_analysis': technical,
            'volume_analysis': volume,
            'orderbook_analysis': orderbook,
            'pattern_analysis': pattern,
            'manipulation_analysis': manipulation,
            'historical_analysis': historical,
            
            # Özet
            'analysis_summary': analysis_summary,
            
            # Trade uygunluğu
            'is_tradeable': self._is_tradeable(
                overall_score,
                manipulation.get('is_safe_to_trade', True),
                orderbook.get('is_liquid', True)
            ),
            
            # Risk faktörleri
            'risk_factors': self._identify_risk_factors(manipulation, orderbook, volume)
        }
    
    def _determine_signal_direction(
        self,
        technical_direction: str,
        volume_pressure: str,
        orderbook_pressure: str,
        pattern_analysis: Dict
    ) -> str:
        """Consensus bazlı sinyal yönü belirleme"""
        votes = {'LONG': 0, 'SHORT': 0}
        
        # Teknik analiz (2 oy)
        if technical_direction:
            votes[technical_direction] += 2
        
        # Volume pressure
        if 'bullish' in volume_pressure:
            votes['LONG'] += 1
        elif 'bearish' in volume_pressure:
            votes['SHORT'] += 1
        
        # Order book pressure
        if 'bullish' in orderbook_pressure:
            votes['LONG'] += 1
        elif 'bearish' in orderbook_pressure:
            votes['SHORT'] += 1
        
        # Pattern direction
        if pattern_analysis.get('has_patterns'):
            bullish_count = pattern_analysis.get('bullish_patterns', 0)
            bearish_count = pattern_analysis.get('bearish_patterns', 0)
            
            if bullish_count > bearish_count:
                votes['LONG'] += 1
            elif bearish_count > bullish_count:
                votes['SHORT'] += 1
        
        return 'LONG' if votes['LONG'] >= votes['SHORT'] else 'SHORT'
    
    def _calculate_confidence(
        self,
        overall_score: float,
        is_safe: bool,
        has_patterns: bool
    ) -> str:
        """Güven seviyesi hesapla"""
        if not is_safe:
            return 'LOW'
        
        if overall_score >= 85 and has_patterns:
            return 'VERY_HIGH'
        elif overall_score >= 75:
            return 'HIGH'
        elif overall_score >= 60:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _create_analysis_summary(
        self,
        technical: Dict,
        volume: Dict,
        orderbook: Dict,
        pattern: Dict,
        manipulation: Dict
    ) -> list:
        """Analiz özetini oluştur"""
        summary = []
        
        # Teknik analiz özeti
        rsi_level = technical.get('rsi_level', 'neutral')
        if rsi_level == 'oversold':
            summary.append("✅ RSI oversold - alım fırsatı")
        elif rsi_level == 'overbought':
            summary.append("⚠️ RSI overbought - dikkatli ol")
        
        macd_crossover = technical.get('macd_crossover', 'neutral')
        if macd_crossover == 'bullish':
            summary.append("✅ MACD bullish crossover")
        
        trend = technical.get('trend', 'sideways')
        if 'uptrend' in trend:
            summary.append(f"📈 {trend.replace('_', ' ').title()}")
        elif 'downtrend' in trend:
            summary.append(f"📉 {trend.replace('_', ' ').title()}")
        
        # Volume özeti
        volume_category = volume.get('volume_category', 'normal')
        if volume_category in ['high', 'very_high']:
            summary.append(f"📊 {volume_category.replace('_', ' ').title()} volume")
        
        if volume.get('is_volume_spike'):
            summary.append("⚡ Volume spike tespit edildi")
        
        # Order book özeti
        if orderbook.get('has_strong_support'):
            summary.append("🛡️ Güçlü support seviyesi")
        
        if orderbook.get('has_strong_resistance'):
            summary.append("🚧 Güçlü resistance seviyesi")
        
        # Pattern özeti
        if pattern.get('has_patterns'):
            strongest = pattern.get('strongest_pattern')
            if strongest:
                summary.append(f"📊 {strongest.get('description', 'Pattern detected')}")
        
        # Manipülasyon uyarıları
        if not manipulation.get('is_safe_to_trade'):
            for reason in manipulation.get('rejection_reasons', []):
                if reason.get('severity') == 'high':
                    summary.append(f"⚠️ {reason.get('description')}")
        
        return summary if summary else ["📊 Nötr market koşulları"]
    
    def _is_tradeable(
        self,
        overall_score: float,
        is_safe: bool,
        is_liquid: bool
    ) -> bool:
        """Trade için uygun mu?"""
        from config.settings import analysis_config
        
        return (
            overall_score >= analysis_config.MIN_SIGNAL_SCORE and
            is_safe and
            is_liquid
        )
    
    def _identify_risk_factors(
        self,
        manipulation: Dict,
        orderbook: Dict,
        volume: Dict
    ) -> list:
        """Risk faktörlerini belirle"""
        risks = []
        
        # Manipülasyon riskleri
        if manipulation.get('manipulation_type') != 'NONE':
            risks.append({
                'type': 'manipulation',
                'severity': manipulation.get('risk_level', 'UNKNOWN'),
                'description': f"Manipülasyon tespit edildi: {manipulation.get('manipulation_type')}"
            })
        
        # Likidite riskleri
        if not orderbook.get('is_liquid'):
            risks.append({
                'type': 'liquidity',
                'severity': 'HIGH',
                'description': 'Düşük likidite'
            })
        
        # Spread riski
        if orderbook.get('spread_percent', 0) > 1:
            risks.append({
                'type': 'spread',
                'severity': 'MEDIUM',
                'description': f"Geniş spread: {orderbook.get('spread_percent')}%"
            })
        
        # Volume riski
        if volume.get('volume_category') == 'very_low':
            risks.append({
                'type': 'volume',
                'severity': 'MEDIUM',
                'description': 'Çok düşük volume'
            })
        
        return risks
    
    def _empty_analysis(self, symbol: str) -> Dict[str, Any]:
        """Boş analiz sonucu"""
        return {
            'symbol': symbol,
            'overall_score': 0,
            'signal_direction': 'LONG',
            'confidence_level': 'LOW',
            'is_tradeable': False,
            'analysis_summary': ['❌ Analiz yapılamadı'],
            'error': True
        }