"""
MEXC Pro Trading Bot - Manipulation Detector
Pump/Dump ve manipülasyon tespiti
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from datetime import datetime, timedelta
from config.settings import manipulation_config, scanner_config
from config.constants import ManipulationType
from utils.logger import get_logger

logger = get_logger(__name__)

class ManipulationDetector:
    """Manipülasyon tespit sınıfı"""
    
    def __init__(self):
        self.config = manipulation_config
        self.scanner_config = scanner_config
    
    async def analyze(
        self,
        ohlcv_data: List[List],
        orderbook: Dict[str, Any],
        symbol: str,
        whale_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Kapsamlı manipülasyon analizi"""
        try:
            if len(ohlcv_data) < 20:
                logger.warning(f"⚠️ {symbol}: Manipülasyon analizi için yetersiz veri")
                return self._empty_analysis()
            
            closes = [candle[4] for candle in ohlcv_data]
            volumes = [candle[5] for candle in ohlcv_data]
            highs = [candle[2] for candle in ohlcv_data]
            lows = [candle[3] for candle in ohlcv_data]
            
            current_price = closes[-1]
            
            # Tüm manipülasyon kontrolleri
            
            # 1. Sudden price movement detection
            sudden_movement = self._detect_sudden_movement(closes)
            
            # 2. Volume anomaly detection
            volume_anomaly = self._detect_volume_anomaly(volumes)
            
            # 3. Pump detection
            pump_detected, pump_strength = self._detect_pump(ohlcv_data[-20:])
            
            # 4. Dump detection
            dump_detected, dump_strength = self._detect_dump(ohlcv_data[-20:])
            
            # 5. Wash trading detection
            wash_trading = self._detect_wash_trading(ohlcv_data[-50:])
            
            # 6. Consolidation check
            consolidation = self._check_consolidation(closes[-self.config.MIN_CONSOLIDATION_PERIOD:])
            
            # 7. Spread anomaly
            spread_anomaly = self._check_spread_anomaly(orderbook)
            
            # 8. Liquidity hunt detection
            liquidity_hunt = self._detect_liquidity_hunt(ohlcv_data[-30:])
            
            # 9. Spoofing detection (whale analysis kullanarak)
            spoofing = False
            if whale_analysis and whale_analysis.get('manipulation_risk') == 'extreme':
                spoofing = True
            
            # 10. Volatility spike
            volatility_spike = self._detect_volatility_spike(closes)
            
            # Genel manipülasyon skoru ve tipi
            manipulation_type, manipulation_score = self._assess_manipulation(
                sudden_movement=sudden_movement,
                volume_anomaly=volume_anomaly,
                pump_detected=pump_detected,
                pump_strength=pump_strength,
                dump_detected=dump_detected,
                dump_strength=dump_strength,
                wash_trading=wash_trading,
                has_consolidation=consolidation['has_consolidation'],
                spread_anomaly=spread_anomaly,
                liquidity_hunt=liquidity_hunt,
                spoofing=spoofing,
                volatility_spike=volatility_spike
            )
            
            # Risk seviyesi belirleme
            risk_level = self._determine_risk_level(manipulation_score)
            
            # Trade'e uygun mu?
            is_safe_to_trade = self._is_safe_to_trade(
                manipulation_type=manipulation_type,
                manipulation_score=manipulation_score,
                has_consolidation=consolidation['has_consolidation'],
                spread_anomaly=spread_anomaly
            )
            
            # Detaylı rejection nedenleri
            rejection_reasons = self._get_rejection_reasons(
                sudden_movement=sudden_movement,
                volume_anomaly=volume_anomaly,
                pump_detected=pump_detected,
                dump_detected=dump_detected,
                wash_trading=wash_trading,
                consolidation=consolidation,
                spread_anomaly=spread_anomaly,
                liquidity_hunt=liquidity_hunt,
                spoofing=spoofing,
                volatility_spike=volatility_spike
            )
            
            return {
                'symbol': symbol,
                'manipulation_score': round(100 - manipulation_score, 2),  # 100 = temiz, 0 = manipüle
                'risk_level': risk_level,
                'is_safe_to_trade': is_safe_to_trade,
                'manipulation_type': manipulation_type.value,
                
                # Detaylı kontroller
                'checks': {
                    'sudden_movement': sudden_movement,
                    'volume_anomaly': volume_anomaly,
                    'pump_detected': pump_detected,
                    'pump_strength': round(pump_strength, 2) if pump_detected else 0,
                    'dump_detected': dump_detected,
                    'dump_strength': round(dump_strength, 2) if dump_detected else 0,
                    'wash_trading_suspected': wash_trading,
                    'consolidation': consolidation,
                    'spread_anomaly': spread_anomaly,
                    'liquidity_hunt': liquidity_hunt,
                    'spoofing_detected': spoofing,
                    'volatility_spike': volatility_spike
                },
                
                # Rejection nedenleri
                'rejection_reasons': rejection_reasons,
                'warning_flags': len([r for r in rejection_reasons if r['severity'] == 'high']),
                
                # Öneriler
                'recommendations': self._get_recommendations(
                    manipulation_type,
                    is_safe_to_trade,
                    rejection_reasons
                )
            }
            
        except Exception as e:
            logger.error(f"❌ Manipülasyon analiz hatası {symbol}: {e}", exc_info=True)
            return self._empty_analysis()
    
    def _detect_sudden_movement(self, closes: List[float]) -> Dict[str, Any]:
        """Ani fiyat hareketlerini tespit et"""
        if len(closes) < 10:
            return {'detected': False, 'change_1m': 0, 'change_5m': 0}
        
        # Son 1 mum değişimi (1 dakika için 1m timeframe'de)
        change_1m = abs((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) >= 2 else 0
        
        # Son 5 mum değişimi
        change_5m = abs((closes[-1] - closes[-6]) / closes[-6] * 100) if len(closes) >= 6 else 0
        
        detected = (
            change_1m > self.config.MAX_PRICE_CHANGE_1M or
            change_5m > self.config.MAX_PRICE_CHANGE_5M
        )
        
        return {
            'detected': detected,
            'change_1m': round(change_1m, 2),
            'change_5m': round(change_5m, 2),
            'exceeded_threshold': change_1m > self.config.MAX_PRICE_CHANGE_1M or change_5m > self.config.MAX_PRICE_CHANGE_5M
        }
    
    def _detect_volume_anomaly(self, volumes: List[float]) -> Dict[str, Any]:
        """Volume anomalisi tespit et"""
        if len(volumes) < 20:
            return {'detected': False, 'ratio': 1.0}
        
        current_volume = volumes[-1]
        avg_volume = np.mean(volumes[:-1])  # Son hariç ortalama
        
        if avg_volume == 0:
            return {'detected': False, 'ratio': 1.0}
        
        volume_ratio = current_volume / avg_volume
        
        detected = volume_ratio > self.config.PUMP_VOLUME_MULTIPLIER
        
        return {
            'detected': detected,
            'ratio': round(volume_ratio, 2),
            'current_volume': round(current_volume, 2),
            'average_volume': round(avg_volume, 2),
            'is_extreme': volume_ratio > self.config.PUMP_VOLUME_MULTIPLIER * 1.5
        }
    
    def _detect_pump(self, ohlcv_data: List[List]) -> Tuple[bool, float]:
        """Pump tespiti"""
        if len(ohlcv_data) < 10:
            return False, 0.0
        
        closes = [c[4] for c in ohlcv_data]
        volumes = [c[5] for c in ohlcv_data]
        
        # Hızlı fiyat artışı + yüksek volume
        price_change = (closes[-1] - closes[0]) / closes[0] * 100
        
        # Son 5 mumun average volume'u
        recent_avg_vol = np.mean(volumes[-5:])
        older_avg_vol = np.mean(volumes[:-5]) if len(volumes) > 5 else recent_avg_vol
        
        volume_increase = recent_avg_vol / older_avg_vol if older_avg_vol > 0 else 1
        
        # Pump kriterleri
        is_pump = (
            price_change > 15 and  # %15+ artış
            volume_increase > 3 and  # 3x volume artışı
            closes[-1] > closes[-2]  # Hala yükseliyor
        )
        
        # Pump gücü
        pump_strength = min((price_change / 15) * (volume_increase / 3) * 100, 100)
        
        return is_pump, pump_strength
    
    def _detect_dump(self, ohlcv_data: List[List]) -> Tuple[bool, float]:
        """Dump tespiti"""
        if len(ohlcv_data) < 10:
            return False, 0.0
        
        closes = [c[4] for c in ohlcv_data]
        volumes = [c[5] for c in ohlcv_data]
        
        # Hızlı fiyat düşüşü + yüksek volume
        price_change = abs((closes[-1] - closes[0]) / closes[0] * 100)
        
        recent_avg_vol = np.mean(volumes[-5:])
        older_avg_vol = np.mean(volumes[:-5]) if len(volumes) > 5 else recent_avg_vol
        
        volume_increase = recent_avg_vol / older_avg_vol if older_avg_vol > 0 else 1
        
        # Dump kriterleri
        is_dump = (
            closes[-1] < closes[0] and  # Düşüş var
            price_change > 15 and  # %15+ düşüş
            volume_increase > 3 and  # 3x volume artışı
            closes[-1] < closes[-2]  # Hala düşüyor
        )
        
        # Dump gücü
        dump_strength = min((price_change / 15) * (volume_increase / 3) * 100, 100)
        
        return is_dump, dump_strength
    
    def _detect_wash_trading(self, ohlcv_data: List[List]) -> bool:
        """Wash trading (sahte işlem) tespiti"""
        if len(ohlcv_data) < 20:
            return False
        
        volumes = [c[5] for c in ohlcv_data]
        closes = [c[4] for c in ohlcv_data]
        
        # Yüksek volume ama düşük fiyat hareketi
        volume_volatility = np.std(volumes) / np.mean(volumes) if np.mean(volumes) > 0 else 0
        price_volatility = np.std(closes) / np.mean(closes) if np.mean(closes) > 0 else 0
        
        # Volume çok volatil ama fiyat stabil = wash trading şüphesi
        if volume_volatility > 1.5 and price_volatility < 0.02:
            return True
        
        # Düzenli aralıklarla aynı boyutta işlemler = şüpheli
        # Basitleştirilmiş kontrol
        volume_pattern_score = self._check_volume_pattern(volumes)
        
        return volume_pattern_score > 0.7
    
    def _check_volume_pattern(self, volumes: List[float]) -> float:
        """Volume'de pattern (tekrar eden düzen) var mı?"""
        if len(volumes) < 10:
            return 0.0
        
        # Volume'lerin birbirine benzerliğini kontrol et
        similarities = []
        for i in range(len(volumes) - 1):
            if volumes[i] > 0:
                similarity = min(volumes[i], volumes[i+1]) / max(volumes[i], volumes[i+1])
                similarities.append(similarity)
        
        if not similarities:
            return 0.0
        
        # Çok benzer volume'lar = pattern
        avg_similarity = np.mean(similarities)
        
        return avg_similarity
    
    def _check_consolidation(self, closes: List[float]) -> Dict[str, Any]:
        """Konsolidasyon periyodu kontrolü"""
        if len(closes) < self.config.MIN_CONSOLIDATION_PERIOD:
            return {
                'has_consolidation': False,
                'duration_minutes': 0,
                'volatility': 100
            }
        
        # Volatilite hesapla
        volatility = (np.std(closes) / np.mean(closes) * 100) if np.mean(closes) > 0 else 100
        
        has_consolidation = volatility < self.config.MAX_CONSOLIDATION_VOLATILITY
        
        return {
            'has_consolidation': has_consolidation,
            'duration_minutes': len(closes),
            'volatility': round(volatility, 2),
            'is_stable': volatility < self.config.MAX_CONSOLIDATION_VOLATILITY / 2
        }
    
    def _check_spread_anomaly(self, orderbook: Dict[str, Any]) -> bool:
        """Spread anomalisi kontrolü"""
        if not orderbook or not orderbook.get('bids') or not orderbook.get('asks'):
            return True  # Order book yoksa şüpheli
        
        bids = orderbook['bids']
        asks = orderbook['asks']
        
        if not bids or not asks:
            return True
        
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        
        spread_percent = ((best_ask - best_bid) / best_bid * 100) if best_bid > 0 else 100
        
        return spread_percent > self.config.MAX_SPREAD_PERCENT
    
    def _detect_liquidity_hunt(self, ohlcv_data: List[List]) -> bool:
        """Likidite avı (stop loss hunting) tespiti"""
        if len(ohlcv_data) < 20:
            return False
        
        # Ani wick'ler (uzun fitiller) = likidite avı işareti
        for candle in ohlcv_data[-10:]:
            open_price = candle[1]
            high = candle[2]
            low = candle[3]
            close = candle[4]
            
            body = abs(close - open_price)
            upper_wick = high - max(open_price, close)
            lower_wick = min(open_price, close) - low
            
            # Çok uzun alt wick = likidite avı aşağı
            if lower_wick > body * 3 and lower_wick > upper_wick * 2:
                return True
            
            # Çok uzun üst wick = likidite avı yukarı
            if upper_wick > body * 3 and upper_wick > lower_wick * 2:
                return True
        
        return False
    
    def _detect_volatility_spike(self, closes: List[float]) -> bool:
        """Volatilite spike'ı tespit et"""
        if len(closes) < 30:
            return False
        
        # Son 10 mum volatilitesi
        recent_volatility = np.std(closes[-10:])
        
        # Önceki 20 mum volatilitesi
        historical_volatility = np.std(closes[-30:-10])
        
        if historical_volatility == 0:
            return False
        
        # 3x artış = spike
        volatility_ratio = recent_volatility / historical_volatility
        
        return volatility_ratio > 3
    
    def _assess_manipulation(
        self,
        sudden_movement: Dict,
        volume_anomaly: Dict,
        pump_detected: bool,
        pump_strength: float,
        dump_detected: bool,
        dump_strength: float,
        wash_trading: bool,
        has_consolidation: bool,
        spread_anomaly: bool,
        liquidity_hunt: bool,
        spoofing: bool,
        volatility_spike: bool
    ) -> Tuple[ManipulationType, float]:
        """Genel manipülasyon değerlendirmesi"""
        
        manipulation_score = 0  # 0 = temiz, 100 = çok manipüle
        manipulation_type = ManipulationType.NONE
        
        # Pump tespiti
        if pump_detected:
            manipulation_score += pump_strength * 0.8
            manipulation_type = ManipulationType.PUMP
        
        # Dump tespiti
        if dump_detected:
            manipulation_score += dump_strength * 0.8
            manipulation_type = ManipulationType.DUMP
        
        # Ani hareket
        if sudden_movement['detected']:
            manipulation_score += 30
        
        # Volume anomalisi
        if volume_anomaly['detected']:
            manipulation_score += 25
            if volume_anomaly.get('is_extreme'):
                manipulation_score += 15
        
        # Wash trading
        if wash_trading:
            manipulation_score += 35
            if manipulation_type == ManipulationType.NONE:
                manipulation_type = ManipulationType.WASH_TRADING
        
        # Spoofing
        if spoofing:
            manipulation_score += 40
            if manipulation_type == ManipulationType.NONE:
                manipulation_type = ManipulationType.SPOOFING
        
        # Likidite avı
        if liquidity_hunt:
            manipulation_score += 25
            if manipulation_type == ManipulationType.NONE:
                manipulation_type = ManipulationType.LIQUIDITY_HUNT
        
        # Spread anomalisi
        if spread_anomaly:
            manipulation_score += 20
        
        # Volatility spike
        if volatility_spike:
            manipulation_score += 15
        
        # Konsolidasyon eksikliği (pozitif faktör)
        if not has_consolidation:
            manipulation_score += 20
        
        manipulation_score = min(manipulation_score, 100)
        
        return manipulation_type, manipulation_score
    
    def _determine_risk_level(self, manipulation_score: float) -> str:
        """Risk seviyesi belirle"""
        if manipulation_score >= 70:
            return 'EXTREME'
        elif manipulation_score >= 50:
            return 'HIGH'
        elif manipulation_score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _is_safe_to_trade(
        self,
        manipulation_type: ManipulationType,
        manipulation_score: float,
        has_consolidation: bool,
        spread_anomaly: bool
    ) -> bool:
        """Trade için güvenli mi?"""
        
        # Kesinlikle güvenli değil
        if manipulation_type in [ManipulationType.PUMP, ManipulationType.DUMP]:
            return False
        
        # Yüksek manipülasyon skoru
        if manipulation_score > 60:
            return False
        
        # Konsolidasyon yok + yüksek spread
        if not has_consolidation and spread_anomaly:
            return False
        
        # Wash trading ve spoofing
        if manipulation_type in [ManipulationType.WASH_TRADING, ManipulationType.SPOOFING]:
            return False
        
        return True
    
    def _get_rejection_reasons(
        self,
        sudden_movement: Dict,
        volume_anomaly: Dict,
        pump_detected: bool,
        dump_detected: bool,
        wash_trading: bool,
        consolidation: Dict,
        spread_anomaly: bool,
        liquidity_hunt: bool,
        spoofing: bool,
        volatility_spike: bool
    ) -> List[Dict[str, Any]]:
        """Rejection nedenlerini listele"""
        reasons = []
        
        if pump_detected:
            reasons.append({
                'reason': 'PUMP_DETECTED',
                'severity': 'high',
                'description': 'Pump pattern tespit edildi - yüksek risk'
            })
        
        if dump_detected:
            reasons.append({
                'reason': 'DUMP_DETECTED',
                'severity': 'high',
                'description': 'Dump pattern tespit edildi - yüksek risk'
            })
        
        if sudden_movement['detected']:
            reasons.append({
                'reason': 'SUDDEN_PRICE_MOVEMENT',
                'severity': 'high',
                'description': f"Ani fiyat hareketi: {sudden_movement['change_5m']}% (5m)"
            })
        
        if volume_anomaly['detected']:
            severity = 'high' if volume_anomaly.get('is_extreme') else 'medium'
            reasons.append({
                'reason': 'VOLUME_ANOMALY',
                'severity': severity,
                'description': f"Anormal volume: {volume_anomaly['ratio']}x normal"
            })
        
        if wash_trading:
            reasons.append({
                'reason': 'WASH_TRADING_SUSPECTED',
                'severity': 'high',
                'description': 'Wash trading şüphesi - sahte volume'
            })
        
        if spoofing:
            reasons.append({
                'reason': 'SPOOFING_DETECTED',
                'severity': 'high',
                'description': 'Spoofing tespit edildi - sahte orderlar'
            })
        
        if not consolidation['has_consolidation']:
            reasons.append({
                'reason': 'NO_CONSOLIDATION',
                'severity': 'medium',
                'description': f"Konsolidasyon yok - volatilite: {consolidation['volatility']}%"
            })
        
        if spread_anomaly:
            reasons.append({
                'reason': 'WIDE_SPREAD',
                'severity': 'medium',
                'description': 'Spread çok geniş - düşük likidite'
            })
        
        if liquidity_hunt:
            reasons.append({
                'reason': 'LIQUIDITY_HUNT',
                'severity': 'medium',
                'description': 'Likidite avı tespit edildi'
            })
        
        if volatility_spike:
            reasons.append({
                'reason': 'VOLATILITY_SPIKE',
                'severity': 'medium',
                'description': 'Ani volatilite artışı'
            })
        
        return reasons
    
    def _get_recommendations(
        self,
        manipulation_type: ManipulationType,
        is_safe: bool,
        rejection_reasons: List[Dict]
    ) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        if not is_safe:
            recommendations.append("⛔ Bu coin şu anda trade için güvenli değil")
        
        if manipulation_type == ManipulationType.PUMP:
            recommendations.append("🚫 PUMP tespit edildi - GİRMEYİN")
            recommendations.append("⏳ Konsolidasyon bekleyin")
        
        elif manipulation_type == ManipulationType.DUMP:
            recommendations.append("🚫 DUMP tespit edildi - SHORT için bile riskli")
            recommendations.append("⏳ Dip oluşumunu bekleyin")
        
        elif manipulation_type == ManipulationType.WASH_TRADING:
            recommendations.append("⚠️ Sahte volume tespit edildi")
            recommendations.append("🔍 Gerçek volume doğrulaması yapın")
        
        elif manipulation_type == ManipulationType.SPOOFING:
            recommendations.append("⚠️ Sahte orderlar tespit edildi")
            recommendations.append("📊 Order book'u dikkatli izleyin")
        
        high_severity = len([r for r in rejection_reasons if r['severity'] == 'high'])
        
        if high_severity >= 2:
            recommendations.append("🔴 Birden fazla yüksek risk faktörü - KAÇININ")
        
        if is_safe and not recommendations:
            recommendations.append("✅ Manipülasyon riski düşük görünüyor")
            recommendations.append("⚠️ Yine de dikkatli olun ve risk yönetimi uygulayın")
        
        return recommendations
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Boş analiz sonucu"""
        return {
            'symbol': '',
            'manipulation_score': 0,
            'risk_level': 'UNKNOWN',
            'is_safe_to_trade': False,
            'manipulation_type': ManipulationType.NONE.value,
            'checks': {},
            'rejection_reasons': [],
            'warning_flags': 0,
            'recommendations': ['⚠️ Analiz yapılamadı']
        }