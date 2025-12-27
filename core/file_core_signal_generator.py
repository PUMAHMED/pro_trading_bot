"""
MEXC Pro Trading Bot - Signal Generator
Analiz sonuçlarından trading sinyalleri üretir
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from core.analyzer import MarketAnalyzer
from core.risk_manager import RiskManager
from config.settings import trading_config, analysis_config
from config.constants import (
    SignalType, SignalQuality, get_quality_from_score, 
    get_leverage_recommendation, EMOJIS
)
from database.connection import get_session
from database.operations import SignalOperations, CoinOperations
from utils.logger import get_logger
from utils.helpers import estimate_duration, format_duration, get_risk_level

logger = get_logger(__name__)

class SignalGenerator:
    """Sinyal üretim motoru"""
    
    def __init__(self, analyzer: MarketAnalyzer):
        self.analyzer = analyzer
        self.risk_manager = RiskManager()
        
        self.daily_signal_count = 0
        self.last_reset_date = datetime.utcnow().date()
        
        logger.info("✅ SignalGenerator başlatıldı")
    
    async def process_scan_results(self, scan_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Tarama sonuçlarını işle ve sinyal üret
        """
        try:
            # Günlük limit kontrolü
            self._check_daily_reset()
            
            if self.daily_signal_count >= trading_config.MAX_DAILY_SIGNALS:
                logger.warning(f"⚠️ Günlük sinyal limiti doldu: {self.daily_signal_count}")
                return []
            
            logger.info(f"🔬 {len(scan_results)} scan sonucu işleniyor...")
            
            generated_signals = []
            
            for scan_result in scan_results:
                try:
                    # Günlük limiti her iterasyonda kontrol et
                    if self.daily_signal_count >= trading_config.MAX_DAILY_SIGNALS:
                        break
                    
                    signal = await self._process_single_result(scan_result)
                    
                    if signal:
                        generated_signals.append(signal)
                        self.daily_signal_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Scan result işleme hatası: {e}")
                    continue
            
            logger.info(f"✅ {len(generated_signals)} sinyal üretildi")
            return generated_signals
            
        except Exception as e:
            logger.error(f"❌ Scan results işleme hatası: {e}", exc_info=True)
            return []
    
    async def _process_single_result(self, scan_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Tek bir scan sonucunu işle"""
        try:
            symbol = scan_result['symbol']
            exchange = scan_result['exchange']
            ohlcv = scan_result['ohlcv']
            orderbook = scan_result['orderbook']
            ticker = scan_result['ticker']
            
            # Kapsamlı analiz yap
            analysis = await self.analyzer.analyze_comprehensive(
                symbol=symbol,
                ohlcv_data=ohlcv,
                orderbook=orderbook,
                ticker=ticker
            )
            
            # Trade'e uygun mu?
            if not analysis.get('is_tradeable', False):
                return None
            
            # Minimum skor kontrolü
            overall_score = analysis.get('overall_score', 0)
            if overall_score < analysis_config.MIN_SIGNAL_SCORE:
                return None
            
            # Sinyal oluştur
            signal = await self._create_signal(analysis, scan_result)
            
            # Risk yönetimi kontrolü
            risk_check = await self.risk_manager.evaluate_signal(signal, analysis)
            
            if not risk_check['approved']:
                logger.info(f"⚠️ {symbol} sinyal risk yönetiminden geçemedi: {risk_check['reason']}")
                return None
            
            # Database'e kaydet
            await self._save_signal_to_db(signal)
            
            logger.info(f"✅ {symbol} sinyali oluşturuldu - Skor: {overall_score}")
            return signal
            
        except Exception as e:
            logger.error(f"❌ Single result işleme hatası: {e}")
            return None
    
    async def _create_signal(
        self,
        analysis: Dict[str, Any],
        scan_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analiz sonuçlarından sinyal oluştur"""
        
        symbol = analysis['symbol']
        current_price = analysis['current_price']
        signal_direction = analysis['signal_direction']
        overall_score = analysis['overall_score']
        
        # Sinyal kalitesi
        quality = get_quality_from_score(overall_score)
        
        # Kaldıraç önerisi
        volatility = scan_result.get('volatility', 5)
        leverage = get_leverage_recommendation(overall_score, volatility)
        
        # TP seviyeleri hesapla
        if signal_direction == 'LONG':
            tp1 = current_price * (1 + trading_config.TP1 / 100)
            tp2 = current_price * (1 + trading_config.TP2 / 100)
            tp3 = current_price * (1 + trading_config.TP3 / 100)
            
            # Stop loss (dinamik)
            technical = analysis.get('technical_analysis', {})
            support_levels = technical.get('support_levels', [])
            
            if support_levels and len(support_levels) > 0:
                # En yakın support'un biraz altı
                nearest_support = max([s for s in support_levels if s < current_price], default=current_price * 0.98)
                stop_loss = nearest_support * 0.995
            else:
                # Varsayılan %2 SL
                stop_loss = current_price * (1 - trading_config.MAX_STOP_LOSS / 100)
        
        else:  # SHORT
            tp1 = current_price * (1 - trading_config.TP1 / 100)
            tp2 = current_price * (1 - trading_config.TP2 / 100)
            tp3 = current_price * (1 - trading_config.TP3 / 100)
            
            # Stop loss
            technical = analysis.get('technical_analysis', {})
            resistance_levels = technical.get('resistance_levels', [])
            
            if resistance_levels and len(resistance_levels) > 0:
                nearest_resistance = min([r for r in resistance_levels if r > current_price], default=current_price * 1.02)
                stop_loss = nearest_resistance * 1.005
            else:
                stop_loss = current_price * (1 + trading_config.MAX_STOP_LOSS / 100)
        
        # Tahmini süre
        estimated_duration = estimate_duration(volatility, trading_config.TP1)
        
        # Risk seviyesi
        risk_level = get_risk_level(leverage, overall_score)
        
        # Analiz özeti formatla
        analysis_summary = "\n".join(analysis.get('analysis_summary', [])[:5])  # İlk 5 madde
        
        # Expires at hesapla
        expires_at = datetime.utcnow() + timedelta(minutes=trading_config.SIGNAL_TIMEOUT)
        
        return {
            'symbol': symbol,
            'exchange': scan_result['exchange'],
            'signal_type': SignalType.LONG if signal_direction == 'LONG' else SignalType.SHORT,
            
            # Fiyatlar
            'entry_price': current_price,
            'current_price': current_price,
            'tp1': tp1,
            'tp2': tp2,
            'tp3': tp3,
            'stop_loss': stop_loss,
            
            # Kaldıraç
            'leverage': leverage,
            
            # Kalite
            'quality': quality,
            'score': overall_score,
            'confidence': analysis.get('confidence_level', 'MEDIUM'),
            
            # Zaman
            'created_at': datetime.utcnow(),
            'expires_at': expires_at,
            'estimated_duration_minutes': estimated_duration,
            'estimated_profit_percent': trading_config.TP1,
            
            # Analiz detayları
            'analysis_summary': analysis_summary,
            'technical_score': analysis['scores']['technical'],
            'volume_score': analysis['scores']['volume'],
            'momentum_score': analysis['scores']['technical'],  # Teknik içinde
            'pattern_score': analysis['scores']['pattern'],
            
            # Risk
            'risk_level': risk_level,
            'max_position_size': self.risk_manager.calculate_position_size(current_price, stop_loss),
            
            # Full analysis (reference için)
            '_full_analysis': analysis
        }
    
    async def _save_signal_to_db(self, signal: Dict[str, Any]):
        """Sinyali database'e kaydet"""
        try:
            async with get_session() as session:
                # Full analysis'i çıkar (database'e kaydetmiyoruz)
                signal_data = {k: v for k, v in signal.items() if not k.startswith('_')}
                
                # Enum'ları değere çevir
                signal_data['signal_type'] = signal_data['signal_type']
                signal_data['quality'] = signal_data['quality']
                signal_data['exchange'] = signal_data['exchange']
                
                # Database'e kaydet
                db_signal = await SignalOperations.create_signal(session, signal_data)
                
                # Signal ID'yi ekle
                signal['id'] = db_signal.id
                
                # Coin istatistiklerini güncelle
                await CoinOperations.update_coin_stats(
                    session,
                    signal['symbol'],
                    signal['exchange'],
                    {
                        'last_signal': datetime.utcnow(),
                        'total_signals': 1  # Increment edilecek
                    }
                )
                
        except Exception as e:
            logger.error(f"❌ Signal DB kaydetme hatası: {e}")
    
    def format_signal_message(self, signal: Dict[str, Any]) -> str:
        """Sinyali Telegram mesajı formatında hazırla"""
        
        quality = signal['quality']
        symbol = signal['symbol']
        exchange = signal['exchange'].value
        direction = signal['signal_type'].value
        price = signal['entry_price']
        
        tp1 = signal['tp1']
        tp2 = signal['tp2']
        tp3 = signal['tp3']
        stop_loss = signal['stop_loss']
        
        leverage = signal['leverage']
        score = signal['score']
        confidence = signal['confidence']
        
        estimated_time = format_duration(signal['estimated_duration_minutes'])
        risk_level = signal['risk_level']
        
        analysis_summary = signal['analysis_summary']
        
        # TP yüzdeleri hesapla
        if direction == 'LONG':
            tp1_percent = (tp1 - price) / price * 100
            tp2_percent = (tp2 - price) / price * 100
            tp3_percent = (tp3 - price) / price * 100
            sl_percent = (stop_loss - price) / price * 100
        else:
            tp1_percent = (price - tp1) / price * 100
            tp2_percent = (price - tp2) / price * 100
            tp3_percent = (price - tp3) / price * 100
            sl_percent = (price - stop_loss) / price * 100
        
        # Emoji seç
        if quality == SignalQuality.EXCELLENT:
            emoji = EMOJIS['fire']
        elif quality == SignalQuality.HIGH:
            emoji = EMOJIS['star']
        else:
            emoji = EMOJIS['check']
        
        message = f"""
{emoji} {quality.value} SİNYAL - {exchange}

💎 Coin: {symbol}
📊 Yön: {direction}
💰 Fiyat: ${price:.8f}

🎯 Hedefler:
  TP1: ${tp1:.8f} ({tp1_percent:+.2f}%)
  TP2: ${tp2:.8f} ({tp2_percent:+.2f}%)
  TP3: ${tp3:.8f} ({tp3_percent:+.2f}%)

🛡️ Stop Loss: ${stop_loss:.8f} ({sl_percent:+.2f}%)
⚡ Kaldıraç: {leverage}x

⏰ Tahmini Süre: {estimated_time}
📈 Sinyal Skoru: {score:.0f}/100
🧠 Güven: {confidence}

📊 Analiz Özeti:
{analysis_summary}

⚠️ Risk: {risk_level}
"""
        
        return message.strip()
    
    def _check_daily_reset(self):
        """Günlük sayacı kontrol et ve resetle"""
        today = datetime.utcnow().date()
        
        if today > self.last_reset_date:
            logger.info(f"🔄 Günlük sinyal sayacı resetlendi: {self.daily_signal_count} -> 0")
            self.daily_signal_count = 0
            self.last_reset_date = today
    
    async def update_active_signals(self):
        """Aktif sinyalleri güncelle (TP/SL kontrolü)"""
        try:
            async with get_session() as session:
                active_signals = await SignalOperations.get_active_signals(session)
                
                for signal in active_signals:
                    # Fiyat güncelleme ve TP/SL kontrolü yapılacak
                    # Bu kısım telegram_bot içinde handle edilecek
                    pass
                    
        except Exception as e:
            logger.error(f"❌ Aktif sinyal güncelleme hatası: {e}")