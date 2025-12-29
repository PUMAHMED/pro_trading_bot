"""
MEXC Pro Trading Bot - Signal Generator
Analiz sonuçlarından trading sinyalleri üretir
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pytz
from core.analyzer import MarketAnalyzer
from core.risk_manager import RiskManager
from config.settings import trading_config, analysis_config, bot_config
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
        self.last_reset_date = self._get_today_istanbul()
        
        # Aynı gün gönderilen coinleri takip et
        self.today_sent_signals: Dict[str, Dict[str, Any]] = {}
        
        logger.info("✅ SignalGenerator başlatıldı")
    
    def _get_today_istanbul(self) -> datetime:
        """İstanbul saatine göre bugünün tarihini al"""
        tz = pytz.timezone(bot_config.TIMEZONE)
        return datetime.now(tz).date()
    
    def _get_current_time_istanbul(self) -> datetime:
        """İstanbul saatine göre şu anki zamanı al"""
        tz = pytz.timezone(bot_config.TIMEZONE)
        return datetime.now(tz)
    
    async def process_scan_results(self, scan_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tarama sonuçlarını işle ve sinyal üret"""
        try:
            # Günlük limit kontrolü
            self._check_daily_reset()
            
            if self.daily_signal_count >= trading_config.MAX_DAILY_SIGNALS:
                logger.warning(f"⚠️ Günlük sinyal limiti doldu: {self.daily_signal_count}/{trading_config.MAX_DAILY_SIGNALS}")
                return []
            
            logger.info(f"🔬 {len(scan_results)} scan sonucu işleniyor...")
            
            generated_signals = []
            
            for scan_result in scan_results:
                try:
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
            
            # Aynı coin bugün gönderildi mi kontrol et
            if await self._should_skip_coin(symbol, exchange):
                logger.debug(f"⏭️ {symbol} bugün zaten sinyal gönderildi, atlanıyor")
                return None
            
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
            
            # Entry price optimizasyonu - oynaklığı bekle
            optimized_entry = await self._optimize_entry_price(
                symbol,
                exchange,
                analysis,
                ticker.get('last', 0)
            )
            
            # Sinyal oluştur
            signal = await self._create_signal(analysis, scan_result, optimized_entry)
            
            # Risk yönetimi kontrolü
            risk_check = await self.risk_manager.evaluate_signal(signal, analysis)
            
            if not risk_check['approved']:
                logger.info(f"⚠️ {symbol} sinyal risk yönetiminden geçemedi: {risk_check['reason']}")
                return None
            
            # Database'e kaydet
            await self._save_signal_to_db(signal)
            
            # Bugün gönderilen coinlere ekle
            self._mark_coin_as_sent_today(symbol, exchange, signal, analysis)
            
            logger.info(f"✅ {symbol} sinyali oluşturuldu - Skor: {overall_score}")
            return signal
            
        except Exception as e:
            logger.error(f"❌ Single result işleme hatası: {e}")
            return None
    
    async def _should_skip_coin(self, symbol: str, exchange: Any) -> bool:
        """Bu coin bugün zaten gönderildi mi?"""
        key = f"{exchange.value}:{symbol}"
        return key in self.today_sent_signals
    
    def _mark_coin_as_sent_today(self, symbol: str, exchange: Any, signal: Dict[str, Any], analysis: Dict[str, Any]):
        """Coin'i bugün gönderildi olarak işaretle"""
        key = f"{exchange.value}:{symbol}"
        self.today_sent_signals[key] = {
            'signal': signal,
            'analysis': analysis,
            'sent_at': self._get_current_time_istanbul(),
            'score': signal['score'],
            'expected_profit': signal.get('estimated_profit_percent', 0)
        }
    
    async def check_signal_updates(self):
        """
        Bugün gönderilen sinyalleri kontrol et ve güncelleme gerekiyorsa bildir
        Bu fonksiyon periyodik olarak çağrılmalı (örn: her 15 dakikada bir)
        """
        try:
            for key, data in list(self.today_sent_signals.items()):
                exchange_name, symbol = key.split(':')
                
                # Yeni analiz yap
                # Bu kısmı scanner'dan current data alarak yapmalı
                # Şimdilik placeholder
                pass
                
        except Exception as e:
            logger.error(f"❌ Sinyal güncelleme kontrolü hatası: {e}")
    
    async def _optimize_entry_price(
        self,
        symbol: str,
        exchange: Any,
        analysis: Dict[str, Any],
        current_price: float
    ) -> float:
        """
        Giriş fiyatını optimize et - oynaklıkları hesaba katarak
        Long: Düşüş bekle
        Short: Yükseliş bekle
        """
        try:
            signal_direction = analysis.get('signal_direction', 'LONG')
            
            # Kısa bir süre bekle ve price action'ı gözlemle
            await asyncio.sleep(trading_config.ENTRY_OPTIMIZATION_WAIT)
            
            # Yeni fiyatı al (bu kısmı gerçek implementasyonda exchange'den çekmeli)
            # Şimdilik basit mantık kullan
            
            tolerance = trading_config.ENTRY_PRICE_TOLERANCE / 100
            
            if signal_direction == 'LONG':
                # Long'da düşüş bekle - mevcut fiyattan biraz aşağıdan gir
                optimized = current_price * (1 - tolerance / 2)
                logger.debug(f"🎯 {symbol} LONG entry optimize: {current_price:.8f} -> {optimized:.8f}")
                return optimized
            else:
                # Short'ta yükseliş bekle - mevcut fiyattan biraz yukarıdan gir
                optimized = current_price * (1 + tolerance / 2)
                logger.debug(f"🎯 {symbol} SHORT entry optimize: {current_price:.8f} -> {optimized:.8f}")
                return optimized
                
        except Exception as e:
            logger.error(f"❌ Entry price optimization hatası: {e}")
            return current_price
    
    async def _create_signal(
        self,
        analysis: Dict[str, Any],
        scan_result: Dict[str, Any],
        entry_price: float
    ) -> Dict[str, Any]:
        """Analiz sonuçlarından sinyal oluştur"""
        
        symbol = analysis['symbol']
        signal_direction = analysis['signal_direction']
        overall_score = analysis['overall_score']
        
        # Sinyal kalitesi
        quality = get_quality_from_score(overall_score)
        
        # Kaldıraç önerisi
        volatility = scan_result.get('volatility', 5)
        leverage = get_leverage_recommendation(overall_score, volatility)
        
        # TP seviyeleri hesapla - TP1 SPOT SABİT %4
        if signal_direction == 'LONG':
            # SPOT TP1 SABİT %4
            tp1 = entry_price * (1 + trading_config.TP1_SPOT_FIXED / 100)
            
            # TP2 ve TP3 dinamik (analize göre ayarlanabilir)
            tp2_percent = trading_config.TP2
            tp3_percent = trading_config.TP3
            
            # Eğer çok güçlü sinyal varsa TP'leri artır
            if overall_score >= 90:
                tp2_percent *= 1.2
                tp3_percent *= 1.3
            
            tp2 = entry_price * (1 + tp2_percent / 100)
            tp3 = entry_price * (1 + tp3_percent / 100)
            
            # Stop loss (dinamik - support bazlı)
            technical = analysis.get('technical_analysis', {})
            support_levels = technical.get('support_levels', [])
            
            if support_levels and len(support_levels) > 0:
                nearest_support = max([s for s in support_levels if s < entry_price], default=entry_price * 0.98)
                stop_loss = nearest_support * 0.995
            else:
                stop_loss = entry_price * (1 - trading_config.MAX_STOP_LOSS / 100)
        
        else:  # SHORT
            tp1 = entry_price * (1 - trading_config.TP1_SPOT_FIXED / 100)
            
            tp2_percent = trading_config.TP2
            tp3_percent = trading_config.TP3
            
            if overall_score >= 90:
                tp2_percent *= 1.2
                tp3_percent *= 1.3
            
            tp2 = entry_price * (1 - tp2_percent / 100)
            tp3 = entry_price * (1 - tp3_percent / 100)
            
            # Stop loss (resistance bazlı)
            technical = analysis.get('technical_analysis', {})
            resistance_levels = technical.get('resistance_levels', [])
            
            if resistance_levels and len(resistance_levels) > 0:
                nearest_resistance = min([r for r in resistance_levels if r > entry_price], default=entry_price * 1.02)
                stop_loss = nearest_resistance * 1.005
            else:
                stop_loss = entry_price * (1 + trading_config.MAX_STOP_LOSS / 100)
        
        # Beklenen yükseliş/düşüş aralığı hesapla
        expected_move_range = self._calculate_expected_move_range(analysis, volatility)
        
        # Tahmini süre
        estimated_duration = estimate_duration(volatility, trading_config.TP1_SPOT_FIXED)
        
        # Risk seviyesi
        risk_level = get_risk_level(leverage, overall_score)
        
        # Analiz özeti formatla
        analysis_summary = "\n".join(analysis.get('analysis_summary', [])[:5])
        
        # Expires at hesapla (İstanbul saati)
        expires_at = self._get_current_time_istanbul() + timedelta(minutes=trading_config.SIGNAL_TIMEOUT)
        
        return {
            'symbol': symbol,
            'exchange': scan_result['exchange'],
            'signal_type': SignalType.LONG if signal_direction == 'LONG' else SignalType.SHORT,
            
            # Fiyatlar
            'entry_price': entry_price,
            'current_price': entry_price,
            'tp1': tp1,
            'tp2': tp2,
            'tp3': tp3,
            'stop_loss': stop_loss,
            
            # Beklenen hareket aralığı
            'expected_move_range': expected_move_range,
            
            # Kaldıraç
            'leverage': leverage,
            
            # Kalite
            'quality': quality,
            'score': overall_score,
            'confidence': analysis.get('confidence_level', 'MEDIUM'),
            
            # Zaman (İstanbul saati)
            'created_at': self._get_current_time_istanbul(),
            'expires_at': expires_at,
            'estimated_duration_minutes': estimated_duration,
            'estimated_profit_percent': trading_config.TP1_SPOT_FIXED,
            
            # Analiz detayları
            'analysis_summary': analysis_summary,
            'technical_score': analysis['scores']['technical'],
            'volume_score': analysis['scores']['volume'],
            'momentum_score': analysis['scores']['technical'],
            'pattern_score': analysis['scores']['pattern'],
            
            # Risk
            'risk_level': risk_level,
            'max_position_size': self.risk_manager.calculate_position_size(entry_price, stop_loss),
            
            # Full analysis (reference için)
            '_full_analysis': analysis
        }
    
    def _calculate_expected_move_range(self, analysis: Dict[str, Any], volatility: float) -> str:
        """Beklenen hareket aralığını hesapla"""
        score = analysis.get('overall_score', 0)
        
        # Skor ve volatiliteye göre beklenen hareket
        if score >= 90:
            min_move = trading_config.TP1_SPOT_FIXED
            max_move = trading_config.TP3 * 1.2
        elif score >= 80:
            min_move = trading_config.TP1_SPOT_FIXED
            max_move = trading_config.TP2 * 1.1
        else:
            min_move = trading_config.TP1_SPOT_FIXED * 0.8
            max_move = trading_config.TP2
        
        return f"%{min_move:.1f} - %{max_move:.1f}"
    
    async def _save_signal_to_db(self, signal: Dict[str, Any]):
        """Sinyali database'e kaydet"""
        try:
            async with get_session() as session:
                signal_data = {k: v for k, v in signal.items() if not k.startswith('_')}
                
                # Datetime objelerini UTC'ye çevir
                if 'created_at' in signal_data:
                    signal_data['created_at'] = signal_data['created_at'].astimezone(pytz.UTC).replace(tzinfo=None)
                if 'expires_at' in signal_data:
                    signal_data['expires_at'] = signal_data['expires_at'].astimezone(pytz.UTC).replace(tzinfo=None)
                
                db_signal = await SignalOperations.create_signal(session, signal_data)
                signal['id'] = db_signal.id
                
                await CoinOperations.update_coin_stats(
                    session,
                    signal['symbol'],
                    signal['exchange'],
                    {
                        'last_signal': datetime.utcnow(),
                        'total_signals': 1
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
        
        # Beklenen yükseliş aralığı
        expected_range = signal.get('expected_move_range', 'N/A')
        
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
        
        # İstanbul saatini formatla
        tz = pytz.timezone(bot_config.TIMEZONE)
        created_at_istanbul = signal['created_at'].astimezone(tz) if hasattr(signal['created_at'], 'astimezone') else signal['created_at']
        time_str = created_at_istanbul.strftime('%H:%M:%S')
        
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
📈 Beklenen Hareket: {expected_range}

🎯 Hedefler:
  TP1: ${tp1:.8f} ({tp1_percent:+.2f}%)
  TP2: ${tp2:.8f} ({tp2_percent:+.2f}%)
  TP3: ${tp3:.8f} ({tp3_percent:+.2f}%)

🛡️ Stop Loss: ${stop_loss:.8f} ({sl_percent:+.2f}%)
⚡ Kaldıraç: {leverage}x

⏰ Tahmini Süre: {estimated_time}
📈 Sinyal Skoru: {score:.0f}/100
🧠 Güven: {confidence}
🕒 Saat: {time_str} (İST)

📊 Analiz Özeti:
{analysis_summary}

⚠️ Risk: {risk_level}
"""
        
        return message.strip()
    
    def _check_daily_reset(self):
        """Günlük sayacı kontrol et ve resetle"""
        today = self._get_today_istanbul()
        
        if today > self.last_reset_date:
            logger.info(f"🔄 Günlük sinyal sayacı resetlendi: {self.daily_signal_count} -> 0")
            self.daily_signal_count = 0
            self.last_reset_date = today
            self.today_sent_signals.clear()  # Bugün gönderilen coinleri temizle